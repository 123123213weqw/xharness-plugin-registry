# documents 0.1.0-beta.1

**Opt-in beta / 用户自选测试版。** Installation does not enable the plugin or install dependencies. Existing user data is not migrated.

Python DOCX/PDF and Node >=20 PPTX/XLSX environments are not bundled and are not auto-installed. Requirements and npm locks are supplied. Word creates/reads/replaces complete runs and normalizes a bounded direct run subset; slides include bounded reorder; PDF includes basic text/create/page operations. OCR, forms, encryption/decryption, advanced conversion, macros and full Office fidelity are not supplied by this release. Rendering must use a user-provisioned renderer. The source reference has conflicting license metadata (frontmatter Proprietary versus retained MIT LICENSE text); both observations are recorded here, not asserted resolved. No third-party dependency binaries or private runtime libraries are shipped.

No full-source parity, statistical improvement or full-platform acceptance is claimed. Keep user edits and authentication separate from plugin code.

The captured Python hashes are Linux-tested dependency selections, not a universal cross-platform wheel lock. Other platforms need separately verified compatible dependency builds; do not silently bypass hash checking. Commands in each Skill are relative to the directory containing that SKILL.md. Resolve the actual installed package location before execution; a text resource is not a successful executable run.
