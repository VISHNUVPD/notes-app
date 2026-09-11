import urllib.request
import urllib.parse
import json

BASE_URL = "http://localhost:5000"


def test_live_docker_stack():
    print("=" * 65)
    print("  VERIFYING LIVE DOCKER STACK (FLASK + POSTGRESQL + MISTUNE)")
    print("=" * 65)

    # 1. Test Health Endpoint
    print("\n[1/4] Querying /health endpoint on Docker container...")
    req = urllib.request.urlopen(f"{BASE_URL}/health", timeout=5)
    assert req.status == 200, f"Health check failed with status {req.status}"
    health_data = json.loads(req.read().decode('utf-8'))
    print(f"      Response: {health_data}")
    assert health_data['status'] == 'healthy'
    assert health_data['database'] == 'connected'
    print("      -> PASS: Web container is healthy and PostgreSQL is connected!")

    # 2. Test Note Creation in Dockerized PostgreSQL
    print("\n[2/4] Testing Note Creation (POST /notes/new)...")
    post_data = urllib.parse.urlencode({
        'title': 'Docker Architecture Notes',
        'content': (
            "## Multi-Container Stack\n"
            "- **Flask**: Port 5000\n"
            "- **PostgreSQL**: Port 5432\n"
            "- **Network**: Bridge `notes-net`"
        )
    }).encode('utf-8')

    create_req = urllib.request.Request(f"{BASE_URL}/notes/new", data=post_data, method='POST')
    with urllib.request.urlopen(create_req) as resp:
        assert resp.status in (200, 302)
        print("      -> PASS: Note created in containerized PostgreSQL!")

    # 3. Test API Notes Listing
    print("\n[3/4] Querying JSON API (/api/notes)...")
    with urllib.request.urlopen(f"{BASE_URL}/api/notes") as resp:
        assert resp.status == 200
        notes = json.loads(resp.read().decode('utf-8'))
        print(f"      Fetched {len(notes)} note(s) from database.")
        assert len(notes) >= 1
        latest_note = notes[0]
        assert latest_note['title'] == 'Docker Architecture Notes'
        assert '<h2>Multi-Container Stack</h2>' in latest_note['rendered_html']
        assert '<li><strong>Flask</strong>: Port 5000</li>' in latest_note['rendered_html']
        print("      -> PASS: Markdown rendered properly inside Docker container!")

    # 4. Test Home Page HTML
    print("\n[4/4] Testing Web UI (GET /)...")
    with urllib.request.urlopen(f"{BASE_URL}/") as resp:
        html = resp.read().decode('utf-8')
        assert 'Docker Architecture Notes' in html
        assert 'Markdown Notes' in html
        print("      -> PASS: UI renders correctly from container!")

    print("\n" + "=" * 65)
    print("  ALL DOCKER INTEGRATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == '__main__':
    test_live_docker_stack()
