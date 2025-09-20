from ..extensions import db


class UserRole(db.Model):
    __tablename__ = "user_roles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = db.Column(
        db.Enum("candidate", "recruiter", "admin", name="user_role_enum"),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "role", name="uq_user_roles_user_id_role"),
    )

    def __repr__(self) -> str:
        return f"<UserRole user_id={self.user_id} role={self.role}>"


