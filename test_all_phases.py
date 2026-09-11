import subprocess
import sys
import time

TEST_STAGES = [
    ("Phase 1: Flask CRUD & Mistune", [sys.executable, "verify_phase1.py"]),
    ("Phase 3: Pytest Unit & Integration Suite (14 Tests)", [sys.executable, "-m", "pytest", "-v"]),
    ("Phase 5: Static Analysis & Linting (Flake8)", [sys.executable, "-m", "flake8", "."]),
    ("Phase 6: Staging Deployment & Auto-Rollback", [sys.executable, "verify_staging_rollback.py"]),
    ("Phase 7: Production Release & SemVer Tagging", [sys.executable, "verify_production_release.py"]),
    ("Phase 8: Ansible Vault Security & Secret Hygiene", [sys.executable, "verify_vault_security.py"]),
    ("Phase 9: CHANGELOG Automation", [sys.executable, "scripts/update_changelog.py"]),
]


def run_master_test_suite():
    print("=" * 75)
    print("    MASTER END-TO-END VERIFICATION: PROJECT 07 FULL CI/CD PIPELINE")
    print("=" * 75)

    passed_count = 0
    start_time = time.time()

    for idx, (title, cmd) in enumerate(TEST_STAGES, 1):
        print(f"\n[{idx}/{len(TEST_STAGES)}] Running: {title}...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"      -> SUCCESS: {title} PASSED")
            passed_count += 1
        else:
            print(f"      -> FAILED: {title}")
            print(f"         Error Output:\n{res.stderr}\n{res.stdout}")
            sys.exit(1)

    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 75)
    print(f"    ALL {passed_count}/{len(TEST_STAGES)} PHASES VERIFIED SUCCESSFULLY IN {elapsed}s!")
    print("=" * 75)


if __name__ == '__main__':
    run_master_test_suite()
