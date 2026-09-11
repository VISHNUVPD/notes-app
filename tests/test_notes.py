from app.models import db, Note


def test_health_check(client):
    """Test /health endpoint returns 200 OK and healthy status."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['database'] == 'connected'


def test_index_page_empty(client):
    """Test index page shows empty state message when no notes exist."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"No notes found" in response.data


def test_index_page_with_notes(client, sample_note):
    """Test index page lists existing notes."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Initial Test Note" in response.data


def test_create_note_success(client, app):
    """Test creating a new note via POST /notes/new."""
    response = client.post('/notes/new', data={
        'title': 'New CI/CD Pipeline Note',
        'content': '## Pipeline Steps\n- Build\n- Test\n- Deploy'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Note created successfully!" in response.data
    assert b"New CI/CD Pipeline Note" in response.data

    with app.app_context():
        note = Note.query.filter_by(title='New CI/CD Pipeline Note').first()
        assert note is not None
        assert "## Pipeline Steps" in note.content


def test_create_note_empty_title_validation(client):
    """Test creating a note without a title displays a validation error."""
    response = client.post('/notes/new', data={
        'title': '   ',
        'content': 'Some content'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Title is required!" in response.data


def test_mistune_markdown_rendering(app):
    """Test that Mistune correctly parses various Markdown syntax elements into HTML."""
    raw_markdown = (
        "# Main Heading\n\n"
        "**Bold text** and *italic text* and `inline code`.\n\n"
        "- [x] Completed task\n"
        "- [ ] Pending task\n\n"
        "| Feature | Status |\n"
        "|---|---|\n"
        "| CI/CD | Active |\n\n"
        "```python\nprint('Hello World')\n```"
    )

    note = Note(title="Markdown Test", content=raw_markdown)
    html = note.render_content_html()

    # Verify Markdown conversions
    assert "<h1>Main Heading</h1>" in html
    assert "<strong>Bold text</strong>" in html
    assert "<em>italic text</em>" in html
    assert "<code>inline code</code>" in html
    assert "<table>" in html
    assert "<th>Feature</th>" in html
    assert "<td>CI/CD</td>" in html


def test_view_note(client, sample_note):
    """Test viewing a single note with rendered Markdown."""
    response = client.get(f'/notes/{sample_note.id}')
    assert response.status_code == 200
    assert b"Initial Test Note" in response.data
    assert b"Markdown Heading" in response.data
    assert b"<strong>bold text</strong>" in response.data


def test_view_note_404(client):
    """Test viewing a non-existent note returns HTTP 404."""
    response = client.get('/notes/99999')
    assert response.status_code == 404


def test_edit_note_get(client, sample_note):
    """Test GET /notes/<id>/edit renders the edit form pre-populated."""
    response = client.get(f'/notes/{sample_note.id}/edit')
    assert response.status_code == 200
    assert b"Initial Test Note" in response.data


def test_edit_note_post_success(client, sample_note, app):
    """Test POST /notes/<id>/edit updates note content in the database."""
    response = client.post(f'/notes/{sample_note.id}/edit', data={
        'title': 'Updated Title After Edit',
        'content': 'Updated content with **modified** markdown.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Note updated successfully!" in response.data
    assert b"Updated Title After Edit" in response.data

    with app.app_context():
        updated = db.session.get(Note, sample_note.id)
        assert updated.title == 'Updated Title After Edit'
        assert '<strong>modified</strong>' in updated.render_content_html()


def test_edit_note_empty_title(client, sample_note):
    """Test editing a note with an empty title displays an error."""
    response = client.post(f'/notes/{sample_note.id}/edit', data={
        'title': '   ',
        'content': 'Some content'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Title cannot be empty!" in response.data


def test_delete_note(client, sample_note, app):
    """Test POST /notes/<id>/delete removes note from the database."""
    response = client.post(f'/notes/{sample_note.id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b"Note deleted successfully!" in response.data

    with app.app_context():
        deleted = db.session.get(Note, sample_note.id)
        assert deleted is None


def test_api_get_notes(client, sample_note):
    """Test GET /api/notes returns JSON array with serialized notes and HTML."""
    response = client.get('/api/notes')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['title'] == 'Initial Test Note'
    assert 'rendered_html' in data[0]
    assert '<strong>bold text</strong>' in data[0]['rendered_html']


def test_search_notes(client, app):
    """Test search filtering by title and content keyword."""
    with app.app_context():
        note1 = Note(title='Docker and Kubernetes Notes', content='Container orchestration notes')
        note2 = Note(title='Python Flask Tips', content='Web development guide')
        db.session.add_all([note1, note2])
        db.session.commit()

    # Search for "Docker" in title
    res = client.get('/?q=Docker')
    assert res.status_code == 200
    assert b'Docker and Kubernetes Notes' in res.data
    assert b'Python Flask Tips' not in res.data

    # Search for "guide" in content
    res = client.get('/?q=guide')
    assert res.status_code == 200
    assert b'Python Flask Tips' in res.data
    assert b'Docker and Kubernetes Notes' not in res.data

