---
name: pdf
description: Create bounded Latin-text PDF reports, inspect pages and metadata, select or merge pages, and rotate pages into separate outputs.
---

# Independent PDF operations, revision 3

Use scripts/pdf_tool.py with the isolated pinned requirements.pdf.lock environment. This independently authored support code uses ReportLab and pypdf. It does not execute source vendor scripts, embedded content, subprocesses or network requests. A successful operation is not a visual/content acceptance result.

    python scripts/pdf_tool.py create --input plan.json --output new.pdf
    python scripts/pdf_tool.py inspect --input new.pdf
    python scripts/pdf_tool.py select --input new.pdf --pages 2 --output selected.pdf
    python scripts/pdf_tool.py merge --input new.pdf selected.pdf --output merged.pdf
    python scripts/pdf_tool.py rotate --input selected.pdf --angle 90 --output rotated.pdf

Create plan keys: title, author, pages. Each page has heading and paragraphs, with optional table(headers, rows, widths_points summing to 468). Text is bounded Latin U+0000..U+00FF excluding unsupported control characters, not arbitrary multilingual content. Logical pages are explicit; unexpected pagination fails validation before final output publication. The layout is Letter portrait, Helvetica, editable PDF text and real page-number text.

Inspect returns actual bytes/SHA, page text, rotation, media boxes, metadata and basic form-field type/value information. It is not OCR, table extraction, complete widget/appearance validation or a renderer. Select uses one-based page numbers; merge preserves supplied file order; rotate supports 90/180/270. Inputs are never changed. Outputs serialize to a private sibling, validate, then publish by exclusive atomic hard link without a replacing fallback; occupied names are refused and temporary files cleaned. Use only isolated owned directories.

Bounds include 10 MiB file size, 50 read pages, 10 authored pages, 256 KiB JSON and bounded tables/text. Encrypted PDFs are rejected. These are resource controls, not proof that arbitrary hostile PDFs are fully safe to parse. Use only owned test inputs in this acceptance lane.

This beta has finite Linux create/read task checks, not general PDF or source-wide acceptance. Before delivery, independently compare fields/order/rotations, render every actual PDF page with official Poppler tools, and inspect every PNG. Deliberately wrong-date outputs must fail the business oracle even if creation succeeds.

Not implemented: OCR, image extraction, arbitrary font/language embedding, form filling, coordinate form analysis, encryption/decryption, attachments, full table extraction, conversion, accessibility/tagging, signatures, annotation editing, fullsource quality or autonomous model use. Original terms are retained in licenses/source-pdf-LICENSE.txt; new support code is MIT.

## Source facts, proposals and assumptions

For a document based on supplied business information, separate three classes of
content before authoring: (1) facts established by a specific input field or
provided evidence, (2) proposed actions or recommendations, and (3) unverified
assumptions. Keep source names, numbers, dates, units, uncertainty and status
faithful. A date, target or plan does not establish execution, readiness, approval
or successful completion. Do not infer an empirical state from a requested
heading, a visual theme, a computed metric or a missing field.

Use only supported facts for factual narrative. When the source is sparse, keep
the artifact concise; use neutral descriptions of the supplied information
rather than adding plausible business circumstances. Additional proposals must
be clearly labeled as proposals, not described as completed actions. Omit an
unnecessary assumption; if necessary, label it as unverified and identify the
confirmation needed. Ask for missing facts when they are essential instead of
inventing them. Creative fictional content is appropriate only when the user
explicitly asks for fiction or hypothetical examples, and it must stay labeled.

Before saving and again after inspection, map every new business-world assertion
(including titles, body, tables, notes, chart labels and metadata) to its source
or to its explicit proposal/assumption label. Preserve that distinction in the
artifact itself, not just in the final chat. Verify completed-artifact statements
against actual file bytes and observed tool results; do not claim an independent
oracle, general fidelity or broader task success that was not observed. This is
a guidance requirement, not a claim that the finite CLI can automatically prove
the truth of arbitrary prose.

For PDF narrative and form fields, a searchable text layer establishes extractability, not the truth of its contents. Do not invent signers, evidence, event outcomes or procedural completion to fill white space.

## Installed package paths

Commands above are relative to the directory containing this SKILL.md. Dependency locks/package.json and licenses are at the plugin root, not the Skill root. The Host must expose an executable path or usable provisioned backend before running code; reading a resource does not execute it. Do not assume a private renderer or library environment is bundled.
