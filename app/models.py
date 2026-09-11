from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
import mistune

db = SQLAlchemy()

# Create a customized mistune markdown parser with standard plugins
markdown_parser = mistune.create_markdown(
    plugins=['table', 'strikethrough', 'task_lists', 'url', 'def_list']
)


class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def render_content_html(self) -> str:
        """
        Renders the note's raw markdown content into sanitized HTML using mistune.
        """
        if not self.content:
            return ""
        return markdown_parser(self.content)

    def to_dict(self) -> dict:
        """
        Serializes the note object into a JSON-friendly dictionary.
        """
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'rendered_html': self.render_content_html(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<Note {self.id}: '{self.title}'>"
