---
name: docx
description: Create bounded Word reports, inspect text and tables, replace one complete text run, and merge direct adjacent same-format text runs into exclusively published separate outputs.
---

# Independent Word operations, revision 12

Use scripts/docx_tool.py with a separately provisioned pinned Python environment. This is an independently authored practical candidate, not an executable copy of the reference scripts. No production installation, model use or full-package acceptance is implied.

Commands:

    python scripts/docx_tool.py create --input plan.json --output new.docx
    python scripts/docx_tool.py inspect --input new.docx
    python scripts/docx_tool.py merge-runs --input split-runs.docx --output normalized.docx
    python scripts/docx_tool.py replace --input new.docx --output changed.docx --old "Pending review" --new "Review approved"

Plan keys are title, introduction and blocks, with optional author, page_numbers and footer_label. Blocks support paragraph(text), heading(text, level 1..3), list(items, ordered), table(headers, rows, widths_inches summing to 6.5), and page_break. Ordinary Unicode punctuation in titles and headings is supported; bounds and XML serialization still apply. Output is Letter portrait, one-inch margins, editable native tables/lists, and optional PAGE fields.

Create, replace and merge-runs serialize into a private sibling temporary file, validate it, and exclusively publish through an atomic hard link. There is no replacing fallback. Existing outputs, including a name created during serialization, are refused. Temporary files are cleaned on serialization, validation or publication failure. The guarantee concerns exclusive final-name publication inside the isolated owned directory; it is not a general hostile-filesystem or crash-durability guarantee.

Inspect returns real artifact bytes/SHA, paragraph/table text, part names, tracked-revision counts, and external relationships marked not executed. It is not a visual verifier or tracked-change-view reader. Replace accepts exactly one complete matching text run, refuses tracked revisions, and preserves the other uncompressed package parts; split-run phrases are unsupported.

Before accepting any output, compare requested fields independently, render every page with an available renderer (for example LibreOffice plus Poppler), and inspect every resulting PNG. A valid package can have the wrong content. This beta has bounded task/CLI checks only; unsupported source-wide and platform behavior remains unverified.

Not implemented: conversion, comments, tracked-change authoring/acceptance, TOC refresh, images, hyperlinks/bookmarks, equations, signed/macro documents, full XSD repair, arbitrary Word fidelity or autonomous model use. Read only the original source for attribution, never execute it. Retained original license is licenses/source-docx-LICENSE.txt; new support code uses MIT.

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

For memos and reports, neutral introduction text is sufficient when the source has only headings and table rows. Do not invent a reporting period, approval, cause or resolved risk; keep table status wording exactly supported.

## Adjacent run normalization (new finite subset)

`merge-runs` joins consecutive direct pure-text runs within ordinary body/table paragraphs only when run attributes and canonical run properties are identical. It preserves literal text and marks the combined text xml:space=preserve; other uncompressed package parts are verified unchanged before exclusive publication. Missing-vs-empty properties and differing styles/attributes are not equated. Fields/tabs/drawings/comments/bookmark boundaries, hyperlinks, textboxes, content controls and other nested wrappers are not traversed as bridges; tracked text/style changes are refused. Header/footer and other part normalization, Word repair/schema fidelity and arbitrary fragmented replacement are not implemented. This beta has seven actual remote DOCX CLI checks and independent saved-package/all-page rendering review for this finite subset only.

## Installed package paths

Commands above are relative to the directory containing this SKILL.md. Dependency locks/package.json and licenses are at the plugin root, not the Skill root. The Host must expose an executable path or usable provisioned backend before running code; reading a resource does not execute it. Do not assume a private renderer or library environment is bundled.
