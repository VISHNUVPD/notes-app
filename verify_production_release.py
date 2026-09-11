import subprocess
import time
import urllib.request
import json

PROD_URL = "http://localhost:5000/health"


def run_cmd(cmd, check=True):
    print(f"   [EXEC] {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and res.returncode != 0:
        print(f"   [ERROR] Command failed with code {res.returncode}:\n{res.stderr}")
        raise RuntimeError(res.stderr)
    return res


def test_production_release():
    print("=" * 70)
    print("  PHASE 7: PRODUCTION RELEASE & SEMVER TAGGING VERIFICATION")
    print("=" * 70)

    # 1. Tag Image with Semantic Version and Latest
    print("\n[STEP 1] Tagging Verified Image with SemVer (:v1.0.0 and :latest)...")
    run_cmd("docker tag notes-app:latest notes-app:v1.0.0")
    run_cmd("docker tag notes-app:latest notes-app:prod-latest")
    print("   -> PASS: Tagged image as notes-app:v1.0.0 and notes-app:prod-latest")

    # 2. Deploy Production Composition
    print("\n[STEP 2] Deploying Production Stack (Port 5000 with compose.prod.yml)...")
    run_cmd("docker compose -f docker-compose.yml -f compose.prod.yml down", check=False)
    run_cmd("docker compose -f docker-compose.yml -f compose.prod.yml up -d")

    # 3. Verify Production Health Endpoint
    print("\n[STEP 3] Probing Production /health Endpoint...")
    time.sleep(3)
    is_healthy = False
    health_data = {}
    for _ in range(10):
        try:
            req = urllib.request.urlopen(PROD_URL, timeout=3)
            if req.status == 200:
                health_data = json.loads(req.read().decode('utf-8'))
                if health_data.get('status') == 'healthy':
                    is_healthy = True
                    break
        except Exception:
            pass
        time.sleep(1)

    assert is_healthy, "Production stack failed health probe!"
    print(f"   -> PASS: Production is live and healthy! Response: {health_data}")
    assert health_data.get('environment') == 'production'

    # 4. Verify Docker Images Listed
    print("\n[STEP 4] Inspecting Local Docker Image Tags...")
    res = run_cmd("docker images notes-app")
    print(res.stdout)

    print("=" * 70)
    print("  PRODUCTION RELEASE & SEMVER TAGGING VERIFIED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == '__main__':
    test_production_release()
