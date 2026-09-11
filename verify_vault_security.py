import os
import re

VAULT_FILE = os.path.join("vault", "secrets.yml")


def test_vault_and_secrets_security():
    print("=" * 70)
    print("  PHASE 8: SECURITY & ANSIBLE VAULT SECRETS VERIFICATION")
    print("=" * 70)

    # 1. Verify Ansible Vault Header
    print("\n[CHECK 1] Inspecting vault/secrets.yml encryption header...")
    assert os.path.exists(VAULT_FILE), "vault/secrets.yml does not exist!"

    with open(VAULT_FILE, 'r', encoding='utf-8') as f:
        content = f.read().strip()

    assert content.startswith("$ANSIBLE_VAULT;1.1;AES256"), "File is not encrypted with AES-256 Ansible Vault!"
    print("   -> PASS: vault/secrets.yml is encrypted with AES-256 ($ANSIBLE_VAULT;1.1;AES256).")

    # 2. Verify No Plaintext Leaks in Vault File
    print("\n[CHECK 2] Scanning vault/secrets.yml for plaintext leakage...")
    assert "ProdPostgresSecurePassword" not in content, "Plaintext password found in secrets.yml!"
    assert "vault_postgres_password:" not in content, "Unencrypted variable names found in secrets.yml!"
    print("   -> PASS: Zero plaintext leakage in encrypted vault file.")

    # 3. Scan Entire Codebase for Hard-Coded Production Secrets
    print("\n[CHECK 3] Scanning application files for hardcoded production secrets...")
    suspicious_patterns = [
        re.compile(r'postgres://.*:.*@.*prod', re.IGNORECASE),
        re.compile(r'ProdPostgresSecurePassword', re.IGNORECASE),
        re.compile(r'AKIA[0-9A-Z]{16}'),  # AWS Key pattern
    ]

    files_scanned = 0
    for root, dirs, files in os.walk('.'):
        if any(ignored in root for ignored in ['.git', '.venv', '__pycache__', 'node_modules']):
            continue
        for file in files:
            if file.endswith(('.py', '.yml', '.yaml', '.html', '.sh', '.md')):
                filepath = os.path.join(root, file)
                files_scanned += 1
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    file_text = f.read()
                    for pattern in suspicious_patterns:
                        match = pattern.search(file_text)
                        if match and "verify_vault_security" not in file:
                            raise AssertionError(f"Hardcoded secret pattern detected in {filepath}!")

    print(f"   -> PASS: Scanned {files_scanned} source files. Zero hardcoded secrets found!")

    print("\n" + "=" * 70)
    print("  ALL ANSIBLE VAULT SECURITY CHECKS PASSED WITH ZERO LEAKS!")
    print("=" * 70)


if __name__ == '__main__':
    test_vault_and_secrets_security()
