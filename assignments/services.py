"""Assignment management and submission grading services."""

from datetime import datetime, timedelta
from core.database import get_session, get_utc_now
from core.events import events
from core.exceptions import AssessmentError, ResourceNotFoundError
from core.pagination import paginate_query
from assignments.models import Assignment
from submissions.models import AssignmentSubmission


class AssignmentService:
    """Operations managing course assignments and student submissions."""

    @staticmethod
    def create_assignment(
        course_id: int,
        title: str,
        instructions: str,
        due_date: datetime = None,
        description: str = "",
        module_id: int = None,
        max_marks: float = 100.0,
        allow_late: bool = True,
        late_penalty_percentage: float = 10.0,
        max_attempts: int = 2,
    ) -> Assignment:
        """Create a new course assignment."""
        session = get_session()
        if due_date is None:
            due_date = get_utc_now() + timedelta(days=14)

        assignment = Assignment(
            course_id=course_id,
            module_id=module_id,
            title=title.strip(),
            instructions=instructions.strip(),
            description=description.strip() if description else None,
            due_date=due_date,
            max_marks=max_marks,
            allow_late=allow_late,
            late_penalty_percentage=late_penalty_percentage,
            max_attempts=max_attempts,
            is_published=True,
        )
        session.add(assignment)
        session.commit()
        return assignment

    @staticmethod
    def get_by_id(assignment_id: int) -> Assignment:
        """Fetch assignment by ID."""
        assignment = get_session().query(Assignment).filter_by(id=assignment_id).first()
        if not assignment:
            raise ResourceNotFoundError(f"Assignment {assignment_id} not found.")
        return assignment

    @staticmethod
    def submit_work(
        assignment_id: int,
        student_id: int,
        submission_text: str = "",
        file_path: str = None,
    ) -> AssignmentSubmission:
        """Submit student work for an assignment."""
        session = get_session()
        assignment = AssignmentService.get_by_id(assignment_id)

        prior_count = (
            session.query(AssignmentSubmission)
            .filter_by(assignment_id=assignment_id, student_id=student_id)
            .count()
        )

        if prior_count >= assignment.max_attempts:
            raise AssessmentError(f"Maximum submission limit ({assignment.max_attempts}) reached.")

        now = get_utc_now()
        is_late = False
        if assignment.due_date and now > assignment.due_date:
            if not assignment.allow_late:
                raise AssessmentError("Submission deadline has passed and late submissions are disallowed.")
            is_late = True

        submission = AssignmentSubmission(
            assignment_id=assignment_id,
            student_id=student_id,
            attempt_number=prior_count + 1,
            submission_text=submission_text.strip() if submission_text else None,
            file_path=file_path,
            submitted_at=now,
            is_late=is_late,
            status="submitted",
        )
        session.add(submission)
        session.commit()

        events.emit(
            "assignment_submitted",
            student_id=student_id,
            assignment_id=assignment_id,
            is_late=is_late,
        )

        return submission

    @staticmethod
    def grade_submission(
        submission_id: int,
        score: float,
        instructor_feedback: str = "",
        letter_grade: str = None,
        graded_by: int = None,
    ) -> AssignmentSubmission:
        """Instructor grades student submission with feedback."""
        session = get_session()
        submission = session.query(AssignmentSubmission).filter_by(id=submission_id).first()
        if not submission:
            raise ResourceNotFoundError(f"Submission {submission_id} not found.")

        assignment = submission.assignment
        final_score = float(score)

        # Apply late penalty if applicable
        if submission.is_late and assignment.late_penalty_percentage > 0:
            penalty = (assignment.late_penalty_percentage / 100.0) * assignment.max_marks
            final_score = max(0.0, final_score - penalty)

        submission.score = round(final_score, 2)
        submission.letter_grade = letter_grade
        submission.instructor_feedback = instructor_feedback.strip() if instructor_feedback else None
        submission.graded_by = graded_by
        submission.graded_at = get_utc_now()
        submission.status = "graded"

        session.commit()

        events.emit(
            "assignment_graded",
            student_id=submission.student_id,
            assignment_id=submission.assignment_id,
            score=submission.score,
        )

        return submission

    @staticmethod
    def get_student_submission(assignment_id: int, student_id: int) -> AssignmentSubmission | None:
        """Fetch student's latest submission for an assignment."""
        return (
            get_session()
            .query(AssignmentSubmission)
            .filter_by(assignment_id=assignment_id, student_id=student_id)
            .order_by(AssignmentSubmission.attempt_number.desc())
            .first()
        )
