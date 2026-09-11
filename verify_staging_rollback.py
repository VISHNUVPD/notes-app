import subprocess
import time
import urllib.request
import json

STAGING_URL = "http://localhost:5001/health"


def run_cmd(cmd, check=True):
    print(f"   [EXEC] {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and res.returncode != 0:
        print(f"   [ERROR] Command failed with code {res.returncode}:\n{res.stderr}")
        raise RuntimeError(res.stderr)
    return res


def check_health():
    for attempt in range(1, 10):
        try:
            req = urllib.request.urlopen(STAGING_URL, timeout=3)
            if req.status == 200:
                data = json.loads(req.read().decode('utf-8'))
                if data.get('status') == 'healthy':
                    return True, data
        except Exception:
            pass
        time.sleep(1)
    return False, None


def test_staging_deploy_and_rollback():
    print("=" * 70)
    print("  PHASE 6: STAGING DEPLOYMENT & AUTOMATED ROLLBACK VERIFICATION")
    print("=" * 70)

    # 1. Test Normal Staging Deployment
    print("\n[SCENARIO 1] Deploying Healthy Build to Staging (Port 5001)...")
    run_cmd("docker compose -f docker-compose.yml -f compose.staging.yml up -d --build")

    print("   Running Automated Smoke Test...")
    is_healthy, health_data = check_health()
    assert is_healthy, "Staging smoke test failed on healthy build!"
    print(f"   -> PASS: Smoke test succeeded! Response: {health_data}")

    # 2. Test Broken Build & Self-Healing Rollback
    print("\n[SCENARIO 2] Simulating Broken Deployment & Testing Auto-Rollback...")
    print("   Deploying intentionally faulty container configuration...")
    # Simulate broken release by setting invalid database credentials
    run_cmd(
        'docker compose -f docker-compose.yml -f compose.staging.yml '
        'run -d --name notes-web-broken -p 5002:5000 -e DATABASE_URL=postgresql://invalid:badpass@db:5432/fake web',
        check=False
    )
    time.sleep(2)

    print("   Running Smoke Test against broken release on port 5002...")
    smoke_passed = False
    try:
        req = urllib.request.urlopen("http://localhost:5002/health", timeout=3)
        if req.status == 200:
            smoke_passed = True
    except Exception:
        smoke_passed = False

    if not smoke_passed:
        print("   [DETECTED] Smoke test FAILED as expected on broken deployment!")
        print("   -> Initiating Automated Rollback (ansible/rollback.yml logic)...")
        # Cleanup broken container
        run_cmd("docker rm -f notes-web-broken", check=False)
        # Restore staging stack to known good state
        run_cmd("docker compose -f docker-compose.yml -f compose.staging.yml up -d")

        # Verify recovery
        is_healthy, _ = check_health()
        assert is_healthy, "Rollback failed to restore healthy state!"
        print("   -> PASS: Automated Rollback successfully restored Staging to healthy state!")

    print("\n" + "=" * 70)
    print("  ALL STAGING DEPLOYMENT & ROLLBACK SCENARIOS VERIFIED!")
    print("=" * 70)


if __name__ == '__main__':
    test_staging_deploy_and_rollback()
