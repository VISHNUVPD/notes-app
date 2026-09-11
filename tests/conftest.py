import pytest
from sqlalchemy.pool import StaticPool
from app.app import create_app
from app.models import db, Note


@pytest.fixture
def app():
    """
    Creates and configures a new Flask app instance for each test.
    Uses in-memory SQLite with StaticPool so all test connections share the same state.
    """
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'connect_args': {'check_same_thread': False},
            'poolclass': StaticPool,
        },
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """
    A test client for sending simulated HTTP requests to the app.
    """
    return app.test_client()


@pytest.fixture
def sample_note(app):
    """
    Creates a pre-populated Note in the test database for testing read/update/delete flows.
    """
    with app.app_context():
        note = Note(
            title="Initial Test Note",
            content="# Markdown Heading\n\nThis is a test note with **bold text** and `code`."
        )
        db.session.add(note)
        db.session.commit()
        # Touch attributes to load into memory
        _ = (note.id, note.title, note.content)
        db.session.expunge(note)
        return note
