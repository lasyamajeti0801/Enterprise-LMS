"""Role management services, RBAC matrix seeding and verification."""

from core.database import get_session
from roles.models import Permission, Role

DEFAULT_PERMISSIONS = [
    # User Management
    ("user:create", "Create User", "users", "Ability to create new user accounts"),
    ("user:read", "Read User", "users", "Ability to view user profiles"),
    ("user:update", "Update User", "users", "Ability to update user details"),
    ("user:delete", "Delete User", "users", "Ability to deactivate or delete users"),
    # Course Management
    ("course:create", "Create Course", "courses", "Ability to create draft courses"),
    ("course:read", "Read Course", "courses", "Ability to view course details"),
    ("course:update", "Update Course", "courses", "Ability to edit course content"),
    ("course:delete", "Delete Course", "courses", "Ability to archive or delete courses"),
    ("course:approve", "Approve Course", "courses", "Ability to approve submitted courses"),
    ("course:publish", "Publish Course", "courses", "Ability to publish courses to catalog"),
    # Curriculum
    ("curriculum:manage", "Manage Curriculum", "curriculum", "Ability to add modules and lessons"),
    # Enrollment
    ("enrollment:create", "Enroll Student", "enrollment", "Ability to enroll in courses"),
    ("enrollment:manage", "Manage Enrollment", "enrollment", "Ability to manage course enrollments"),
    # Assessments & Grading
    ("assessment:create", "Create Assessment", "assessment", "Ability to build quizzes and exams"),
    ("assessment:grade", "Grade Submissions", "assessment", "Ability to grade assignments and exams"),
    ("grade:view_own", "View Own Grades", "grading", "Ability for student to view own grades"),
    ("grade:view_all", "View All Grades", "grading", "Ability to view class gradebook"),
    # Attendance
    ("attendance:record", "Record Attendance", "attendance", "Ability to mark attendance sessions"),
    ("attendance:view", "View Attendance", "attendance", "Ability to view attendance records"),
    # Certificates
    ("certificate:issue", "Issue Certificate", "certificates", "Ability to issue course completion certificate"),
    ("certificate:view", "View Certificate", "certificates", "Ability to view and download certificates"),
    # Analytics & Reports
    ("analytics:view", "View Analytics", "analytics", "Ability to view platform analytics"),
    ("reports:export", "Export Reports", "reports", "Ability to export CSV/JSON/PDF reports"),
    # System Administration
    ("system:settings", "System Settings", "system", "Ability to configure system settings"),
    ("audit:view", "View Audit Logs", "audit", "Ability to inspect system audit trail"),
]


class RoleService:
    """Service class for managing roles and permissions."""

    @staticmethod
    def seed_default_roles_and_permissions():
        """Initialize all default system permissions and roles."""
        session = get_session()
        created_perms = {}

        # 1. Seed Permissions
        for code, name, module, desc in DEFAULT_PERMISSIONS:
            perm = session.query(Permission).filter_by(code=code).first()
            if not perm:
                perm = Permission(code=code, name=name, module=module, description=desc)
                session.add(perm)
                session.flush()
            created_perms[code] = perm

        # 2. Seed Default Roles
        roles_def = [
            ("admin", "System Administrator", "Full unrestricted access to all platform features", 1),
            ("instructor", "Course Instructor", "Create and manage courses, curriculum, grading, and students", 1),
            ("student", "Student / Learner", "Enroll in courses, complete lessons, take quizzes, view certificates", 1),
            ("auditor", "Academic Auditor", "Read-only access to academic records and reports", 1),
        ]

        created_roles = {}
        for role_name, display_name, desc, is_sys in roles_def:
            role = session.query(Role).filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name, display_name=display_name, description=desc, is_system=is_sys)
                session.add(role)
                session.flush()
            created_roles[role_name] = role

        # 3. Assign Role Permissions
        # Admin gets all
        admin_role = created_roles["admin"]
        admin_role.permissions = list(created_perms.values())

        # Instructor permissions
        instructor_perms = [
            "course:create", "course:read", "course:update", "curriculum:manage",
            "enrollment:manage", "assessment:create", "assessment:grade", "grade:view_all",
            "attendance:record", "attendance:view", "certificate:issue", "certificate:view",
            "analytics:view", "reports:export"
        ]
        created_roles["instructor"].permissions = [created_perms[p] for p in instructor_perms if p in created_perms]

        # Student permissions
        student_perms = [
            "course:read", "enrollment:create", "grade:view_own", "attendance:view", "certificate:view"
        ]
        created_roles["student"].permissions = [created_perms[p] for p in student_perms if p in created_perms]

        # Auditor permissions
        auditor_perms = [
            "user:read", "course:read", "grade:view_all", "attendance:view",
            "analytics:view", "reports:export", "audit:view"
        ]
        created_roles["auditor"].permissions = [created_perms[p] for p in auditor_perms if p in created_perms]

        session.commit()
        return created_roles

    @staticmethod
    def get_role_by_name(name: str):
        """Find a role by its unique system name."""
        return get_session().query(Role).filter_by(name=name.lower()).first()

    @staticmethod
    def get_all_roles():
        """Retrieve list of all registered roles."""
        return get_session().query(Role).order_by(Role.id).all()

    @staticmethod
    def get_all_permissions():
        """Retrieve list of all registered permissions."""
        return get_session().query(Permission).order_by(Permission.module, Permission.code).all()
