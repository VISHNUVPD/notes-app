# 📝 Changelog

All notable changes to the Notes App CI/CD Pipeline are documented here.

## [Staging Build (620028f)] - 2026-09-11 04:55 UTC

**Commit SHA**: `620028f`

### Features
- [`78b3fa3`] feat(prod): add production manual approval workflow and SemVer release tagging
- [`606f568`] feat(cd): add Ansible staging deployment, smoke tests, and auto-rollback
- [`8618d90`] feat(search): add notes keyword search with UI searchbar and tests
- [`fc4b6f0`] feat: initial commit with Flask notes app, Docker, and pytest suite

### CI/CD & DevOps
- [`a4c20d3`] ci: add GitHub Actions workflow for lint, test, and GHCR Docker build

### Security
- [`620028f`] sec: encrypt production credentials with Ansible Vault AES-256

