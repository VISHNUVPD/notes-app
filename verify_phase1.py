import os

# Configure in-memory SQLite for self-contained testing
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

# Imports after environment configuration
from app.app import create_app  # noqa: E402
from app.models import db, Note  # noqa: E402


def run_tests():
    print("=" * 60)
    print("  RUNNING PHASE 1 VERIFICATION TESTS")
    print("=" * 60)

    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    client = app.test_client()

    with app.app_context():
        # Test 1: Health Check Endpoint
        res = client.get('/health')
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        assert res.json['status'] == 'healthy'
        print(" [PASS] 1. /health endpoint returned HTTP 200 (healthy)")

        # Test 2: Note Creation via POST
        res = client.post('/notes/new', data={
            'title': 'DevOps Pipeline Architecture',
            'content': (
                "# CI/CD Overview\n\n"
                "**Flask + Postgres** with `mistune`.\n\n"
                "| Phase | Tool |\n"
                "|---|---|\n"
                "| CI | GitHub Actions |"
            )
        }, follow_redirects=True)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        print(" [PASS] 2. Note creation (POST /notes/new) succeeded")

        # Test 3: Note Retrieval & Mistune Markdown Rendering
        note = Note.query.first()
        assert note is not None, "Note was not saved to database!"
        assert note.title == 'DevOps Pipeline Architecture'
        html = note.render_content_html()
        assert '<h1>CI/CD Overview</h1>' in html, "Heading was not rendered properly"
        assert '<strong>Flask + Postgres</strong>' in html, "Bold was not rendered properly"
        assert '<code>mistune</code>' in html, "Inline code was not rendered properly"
        assert '<table>' in html, "Markdown table plugin was not rendered properly"
        print(" [PASS] 3. Mistune Markdown rendering verified (H1, Bold, Inline Code, Table)")

        # Test 4: View Route (GET /notes/<id>)
        res = client.get(f'/notes/{note.id}')
        assert res.status_code == 200
        assert b'DevOps Pipeline Architecture' in res.data
        print(f" [PASS] 4. Note view page (GET /notes/{note.id}) rendered correctly")

        # Test 5: Note Update via POST
        res = client.post(f'/notes/{note.id}/edit', data={
            'title': 'Updated DevOps Architecture',
            'content': 'Updated content with *italics*'
        }, follow_redirects=True)
        assert res.status_code == 200
        updated_note = db.session.get(Note, note.id)
        assert updated_note.title == 'Updated DevOps Architecture'
        assert '<em>italics</em>' in updated_note.render_content_html()
        print(" [PASS] 5. Note update (POST /notes/<id>/edit) verified")

        # Test 6: Note Deletion via POST
        res = client.post(f'/notes/{note.id}/delete', follow_redirects=True)
        assert res.status_code == 200
        assert Note.query.count() == 0
        print(" [PASS] 6. Note deletion (POST /notes/<id>/delete) verified")

    print("=" * 60)
    print("  ALL PHASE 1 CAPABILITIES TESTED & VERIFIED!")
    print("=" * 60)


if __name__ == '__main__':
    run_tests()
