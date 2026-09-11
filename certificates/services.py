"""Local PDF Certificate generation engine and cryptographic verification service."""

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from config.settings import BaseConfig
from core.database import get_session, get_utc_now
from core.exceptions import CertificateIneligibleError, ResourceNotFoundError
from core.security import generate_certificate_code
from certificates.models import Certificate
from courses.models import Course
from enrollment.models import CourseEnrollment
from grading.services import GradingService
from students.models import StudentProfile


class CertificateService:
    """Operations evaluating certificate eligibility and producing high-resolution PDF credentials."""

    @staticmethod
    def check_eligibility(course_id: int, student_id: int) -> tuple[bool, str]:
        """Verify whether a student qualifies for a course certificate."""
        session = get_session()
        course = session.query(Course).filter_by(id=course_id).first()
        if not course:
            return False, "Course not found."

        if not course.is_certificate_enabled:
            return False, "Certificates are not enabled for this course."

        enrollment = (
            session.query(CourseEnrollment)
            .filter_by(course_id=course_id, student_id=student_id)
            .first()
        )
        if not enrollment:
            return False, "Student is not enrolled in this course."

        if enrollment.progress_percentage < 100.0 and enrollment.status != "completed":
            return False, f"Course progress ({enrollment.progress_percentage:.1f}%) is below the required 100%."

        grade_record = GradingService.calculate_student_grade(course_id, student_id)
        if not grade_record.is_passed:
            return False, f"Final grade ({grade_record.total_weighted_score:.1f}%) is below the passing threshold of {course.passing_grade}%."

        return True, "Eligible for certificate."

    @staticmethod
    def generate_certificate(course_id: int, student_id: int) -> Certificate:
        """Issue and generate local PDF certificate for an eligible student."""
        session = get_session()
        is_eligible, reason = CertificateService.check_eligibility(course_id, student_id)
        if not is_eligible:
            raise CertificateIneligibleError(reason)

        course = session.query(Course).filter_by(id=course_id).first()
        student = session.query(StudentProfile).filter_by(id=student_id).first()
        user = student.user

        cert = (
            session.query(Certificate)
            .filter_by(course_id=course_id, student_id=student_id)
            .first()
        )

        now = get_utc_now()
        grade_record = GradingService.calculate_student_grade(course_id, student_id)

        if not cert:
            cert_num = f"LMS-{course.code}-{student.student_id_number}"
            v_code = generate_certificate_code(course_id, student_id, user.uuid)

            cert = Certificate(
                certificate_number=cert_num,
                verification_code=v_code,
                course_id=course_id,
                student_id=student_id,
                issue_date=now,
                final_grade_percentage=grade_record.total_weighted_score,
                is_revoked=False,
            )
            session.add(cert)
            session.flush()

        # Build PDF locally
        BaseConfig.ensure_directories()
        pdf_filename = f"Certificate_{cert.certificate_number}.pdf"
        pdf_path = os.path.join(BaseConfig.CERTIFICATES_FOLDER, pdf_filename)

        CertificateService._render_pdf(
            pdf_path=pdf_path,
            student_name=user.full_name,
            course_title=course.title,
            course_code=course.code,
            issue_date=cert.issue_date.strftime("%B %d, %Y"),
            verification_code=cert.verification_code,
            grade=f"{cert.final_grade_percentage:.1f}% ({grade_record.letter_grade})",
            instructor_name=course.instructor.user.full_name if course.instructor and course.instructor.user else "Academic Director",
        )

        cert.pdf_file_path = pdf_path
        session.commit()
        return cert

    @staticmethod
    def _render_pdf(
        pdf_path: str,
        student_name: str,
        course_title: str,
        course_code: str,
        issue_date: str,
        verification_code: str,
        grade: str,
        instructor_name: str,
    ):
        """Render high-resolution PDF certificate using ReportLab canvas."""
        c = canvas.Canvas(pdf_path, pagesize=landscape(letter))
        width, height = landscape(letter)

        # 1. Background styling & Luxury Outer Border
        c.setFillColor(colors.HexColor("#0B132B"))  # Deep navy
        c.rect(0, 0, width, height, fill=True, stroke=False)

        # Inner cream canvas
        margin = 25
        c.setFillColor(colors.HexColor("#FCFCFD"))
        c.roundRect(margin, margin, width - (margin * 2), height - (margin * 2), 12, fill=True, stroke=False)

        # Double Gold Border
        c.setStrokeColor(colors.HexColor("#D4AF37"))  # Metallic gold
        c.setLineWidth(3)
        c.rect(margin + 12, margin + 12, width - ((margin + 12) * 2), height - ((margin + 12) * 2), fill=False, stroke=True)
        c.setLineWidth(1)
        c.rect(margin + 18, margin + 18, width - ((margin + 18) * 2), height - ((margin + 18) * 2), fill=False, stroke=True)

        # 2. Header
        c.setFillColor(colors.HexColor("#1E293B"))
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2.0, height - 70, "ENTERPRISE LEARNING MANAGEMENT SYSTEM")

        c.setFillColor(colors.HexColor("#B45309"))  # Gold/Amber
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(width / 2.0, height - 110, "CERTIFICATE OF ACHIEVEMENT")

        # 3. Presentation text
        c.setFillColor(colors.HexColor("#475569"))
        c.setFont("Helvetica-Oblique", 14)
        c.drawCentredString(width / 2.0, height - 150, "This is proudly presented to")

        # Student Name
        c.setFillColor(colors.HexColor("#0F172A"))
        c.setFont("Helvetica-Bold", 32)
        c.drawCentredString(width / 2.0, height - 195, student_name)

        # Underline
        c.setStrokeColor(colors.HexColor("#D4AF37"))
        c.setLineWidth(1.5)
        c.line((width / 2.0) - 180, height - 205, (width / 2.0) + 180, height - 205)

        # Completion text
        c.setFillColor(colors.HexColor("#475569"))
        c.setFont("Helvetica", 13)
        c.drawCentredString(
            width / 2.0,
            height - 235,
            f"for successfully mastering the curriculum and fulfilling all graduation requirements for",
        )

        # Course Title
        c.setFillColor(colors.HexColor("#1E3A8A"))  # Rich blue
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(width / 2.0, height - 270, f"{course_title} ({course_code})")

        # Grade details
        c.setFillColor(colors.HexColor("#334155"))
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2.0, height - 300, f"Graduated with Distinction | Final Score: {grade}")

        # 4. Signatures and Verification Footer
        # Issue Date (Left)
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(colors.HexColor("#1E293B"))
        c.drawString(70, 110, f"Date Issued: {issue_date}")
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor("#64748B"))
        c.drawString(70, 95, f"Verification Code: {verification_code}")

        # Instructor Signature (Right)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.HexColor("#1E293B"))
        c.drawRightString(width - 70, 110, instructor_name)
        c.setStrokeColor(colors.HexColor("#94A3B8"))
        c.setLineWidth(1)
        c.line(width - 220, 125, width - 70, 125)
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.HexColor("#64748B"))
        c.drawRightString(width - 70, 95, "Authorized Instructor & Academic Board")

        # Official Stamp emblem (Center Bottom)
        c.setFillColor(colors.HexColor("#D97706"))
        c.circle(width / 2.0, 95, 30, fill=False, stroke=True)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(width / 2.0, 100, "OFFICIAL")
        c.drawCentredString(width / 2.0, 90, "CREDENTIAL")

        c.save()

    @staticmethod
    def verify_certificate(verification_code: str) -> dict | None:
        """Verify authenticity of a certificate using its verification code."""
        session = get_session()
        cert = (
            session.query(Certificate)
            .filter(
                (Certificate.verification_code == verification_code.strip())
                | (Certificate.certificate_number == verification_code.strip())
            )
            .first()
        )
        if not cert:
            return None

        return {
            "is_valid": not cert.is_revoked,
            "certificate_number": cert.certificate_number,
            "verification_code": cert.verification_code,
            "student_name": cert.student.user.full_name,
            "student_id": cert.student.student_id_number,
            "course_title": cert.course.title,
            "course_code": cert.course.code,
            "issue_date": cert.issue_date.strftime("%B %d, %Y"),
            "final_grade": f"{cert.final_grade_percentage:.1f}%",
            "is_revoked": cert.is_revoked,
            "revocation_reason": cert.revocation_reason,
        }
