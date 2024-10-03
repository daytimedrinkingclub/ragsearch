from datetime import datetime
from extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid

class System(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = db.Column(db.String(255), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=True)
    modified_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<System {self.key}: {self.value[:20]}...>"

    @property
    def as_dict(self):
        return {self.key: self.value}

    @classmethod
    def from_dict(cls, data):
        key, value = next(iter(data.items()))
        return cls(key=key, value=value)