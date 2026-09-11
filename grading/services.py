"""Grading calculation engine, weighted scoring, GPA conversion, and gradebook management."""

from core.database import get_session, get_utc_now
from core.exceptions import ResourceNotFoundError
from assignments.models import Assignment
from attendance.services import AttendanceService
from courses.models import Course
from grading.models import FinalGradeRecord, GradingScheme
from quizzes.models import Quiz, QuizAttempt
from students.models import StudentProfile
from submissions.models import AssignmentSubmission


def percentage_to_letter_and_gpa(percentage: float) -> tuple[str, float]:
    """Convert numeric percentage to letter grade and GPA points (4.0 scale)."""
    p = round(percentage, 1)
    if p >= 93.0:
        return "A", 4.0
    elif p >= 90.0:
        return "A-", 3.7
    elif p >= 87.0:
        return "B+", 3.3
    elif p >= 83.0:
        return "B", 3.0
    elif p >= 80.0:
        return "B-", 2.7
    elif p >= 77.0:
        return "C+", 2.3
    elif p >= 73.0:
        return "C", 2.0
    elif p >= 70.0:
        return "C-", 1.7
    elif p >= 60.0:
        return "D", 1.0
    else:
        return "F", 0.0


class GradingService:
    """Operations managing weighted grading rules and gradebook calculations."""

    @staticmethod
    def get_or_create_scheme(course_id: int) -> GradingScheme:
        """Fetch course grading scheme or create with defaults."""
        session = get_session()
        scheme = session.query(GradingScheme).filter_by(course_id=course_id).first()
        if not scheme:
            scheme = GradingScheme(
                course_id=course_id,
                assignment_weight=25.0,
                quiz_weight=25.0,
                exam_weight=40.0,
                attendance_weight=10.0,
                passing_threshold=60.0,
            )
            session.add(scheme)
            session.commit()
        return scheme

    @staticmethod
    def update_scheme(
        course_id: int,
        assignment_weight: float,
        quiz_weight: float,
        exam_weight: float,
        attendance_weight: float,
        passing_threshold: float = 60.0,
    ) -> GradingScheme:
        """Update course grading weights."""
        session = get_session()
        scheme = GradingService.get_or_create_scheme(course_id)
        scheme.assignment_weight = float(assignment_weight)
        scheme.quiz_weight = float(quiz_weight)
        scheme.exam_weight = float(exam_weight)
        scheme.attendance_weight = float(attendance_weight)
        scheme.passing_threshold = float(passing_threshold)
        session.commit()
        return scheme

    @staticmethod
    def calculate_student_grade(course_id: int, student_id: int) -> FinalGradeRecord:
        """Calculate aggregate weighted final grade for a student in a course."""
        session = get_session()
        course = session.query(Course).filter_by(id=course_id).first()
        if not course:
            raise ResourceNotFoundError(f"Course {course_id} not found.")

        scheme = GradingService.get_or_create_scheme(course_id)

        # 1. Assignment average score %
        total_course_assignments = session.query(Assignment).filter_by(course_id=course_id).count()
        submissions = (
            session.query(AssignmentSubmission)
            .join(AssignmentSubmission.assignment)
            .filter(AssignmentSubmission.student_id == student_id, AssignmentSubmission.assignment.has(course_id=course_id))
            .all()
        )
        if submissions:
            assignment_pct = sum((s.score / s.assignment.max_marks * 100.0) for s in submissions if s.score is not None) / len(submissions)
        elif total_course_assignments == 0:
            assignment_pct = 100.0
        else:
            assignment_pct = 0.0

        # 2. Quiz average score %
        total_course_quizzes = session.query(Quiz).filter_by(course_id=course_id).count()
        quiz_attempts = (
            session.query(QuizAttempt)
            .join(QuizAttempt.quiz)
            .filter(QuizAttempt.student_id == student_id, QuizAttempt.quiz.has(course_id=course_id), QuizAttempt.status == "evaluated")
            .all()
        )
        if quiz_attempts:
            quiz_pct = sum(a.percentage for a in quiz_attempts) / len(quiz_attempts)
        elif total_course_quizzes == 0:
            quiz_pct = 100.0
        else:
            quiz_pct = 0.0

        # 3. Exam average score % (default to quiz score if no standalone exam taken)
        exam_pct = quiz_pct

        # 4. Attendance %
        att_summary = AttendanceService.get_student_course_attendance(course_id, student_id)
        attendance_pct = att_summary["percentage"]

        # Weighted calculation
        total_weight = scheme.assignment_weight + scheme.quiz_weight + scheme.exam_weight + scheme.attendance_weight
        if total_weight <= 0:
            total_weight = 100.0

        weighted_sum = (
            (assignment_pct * scheme.assignment_weight)
            + (quiz_pct * scheme.quiz_weight)
            + (exam_pct * scheme.exam_weight)
            + (attendance_pct * scheme.attendance_weight)
        )
        final_score = round(weighted_sum / total_weight, 1)

        letter, gpa = percentage_to_letter_and_gpa(final_score)
        is_passed = final_score >= scheme.passing_threshold

        record = (
            session.query(FinalGradeRecord)
            .filter_by(course_id=course_id, student_id=student_id)
            .first()
        )
        if not record:
            record = FinalGradeRecord(
                course_id=course_id,
                student_id=student_id,
                assignment_score=round(assignment_pct, 1),
                quiz_score=round(quiz_pct, 1),
                exam_score=round(exam_pct, 1),
                attendance_score=round(attendance_pct, 1),
                total_weighted_score=final_score,
                letter_grade=letter,
                gpa_value=gpa,
                is_passed=is_passed,
                finalized_at=get_utc_now(),
            )
            session.add(record)
        else:
            record.assignment_score = round(assignment_pct, 1)
            record.quiz_score = round(quiz_pct, 1)
            record.exam_score = round(exam_pct, 1)
            record.attendance_score = round(attendance_pct, 1)
            record.total_weighted_score = final_score
            record.letter_grade = letter
            record.gpa_value = gpa
            record.is_passed = is_passed
            record.finalized_at = get_utc_now()

        session.commit()

        # Update student cumulative GPA
        GradingService.recalculate_student_cumulative_gpa(student_id)

        return record

    @staticmethod
    def recalculate_student_cumulative_gpa(student_id: int):
        """Update student's overall GPA across all finished/evaluated courses."""
        session = get_session()
        records = session.query(FinalGradeRecord).filter_by(student_id=student_id).all()
        if not records:
            return

        avg_gpa = sum(r.gpa_value for r in records) / len(records)
        profile = session.query(StudentProfile).filter_by(id=student_id).first()
        if profile:
            profile.gpa = round(avg_gpa, 2)
            profile.total_credits = len(records) * 3
            session.commit()
