---
name: pptx
description: Create bounded editable presentations and tables, inspect ordinary slide text/notes, replace one complete text run, or reorder an entire existing slide list using a portable public Node backend.
---

# Portable presentation operations

This independently authored plugin candidate uses public pinned PptxGenJS 4.0.1, JSZip and fast-xml-parser, not private Codex dependencies. Provision the exact package-lock.json in a separate owned runtime with install scripts disabled. Finite Linux CLI and saved-package/rendering checks do not establish full source or platform acceptance.

    node scripts/pptx_tool.mjs create --input plan.json --output /owned/output/new.pptx
    node scripts/pptx_tool.mjs inspect --input /owned/output/new.pptx
    node scripts/pptx_tool.mjs replace --input /owned/output/new.pptx --output /owned/output/edited.pptx --old "Pending review" --new "Review approved"

Create plan keys: title, author, slides; optional font. Each slide has title and paragraphs, optional notes and table(headers, rows, widths_inches summing to 12). A new editable widescreen deck uses bounded title/body boxes and native tables. There is no user-supplied shell, executable script, media URL or image-loading path. Requested font availability remains a separate QA obligation.

Inspect follows the actual presentation relationship list, returning artifact bytes/SHA, ordered slide text runs, native-table counts and notes. Narrow p:/a: namespace spellings are supported. It is not a renderer, arbitrary XML namespace normalizer or complete object extractor. Replace accepts exactly one complete matching a:t text run, changes that slide XML only, and preserves every other uncompressed package-part byte. Split-run text is unsupported; signatures and macros are refused.

ZIP directory sizes, bounded deflation, CRC, member paths/counts and required parts are checked before input consumption. DTD/entities/CDATA are outside narrow inspection scope. Output is serialized to a private sibling temporary file and exclusively linked to a new absolute output name; existing names are never replaced and temporary files are cleaned. Use an isolated owned directory; no hostile-parent or crash-durability claim is made.

Authoring limits: 10 slides, four bounded paragraphs per slide, six table columns/rows. Input package limits: 10 MiB compressed, 25 MiB expanded, 512 members, 20 inspected slides. These limits are not full hostile-document parser verification. Rendering and independent business-field checks must cover every actual exported slide, including deliberately wrong-date negative artifacts. Codex's official artifact tool may serve as an independent read/render oracle, not a production dependency or bundled public runtime.

Not implemented: arbitrary templates/master editing, charts, images, animation, narration/video, themes beyond a font choice, comments, slide insertion/deletion/duplication, conversions, full XSD auto-repair, fullsource parity, application fidelity or autonomous model use. Original license is retained in licenses/source-pptx-LICENSE.txt; independently authored support is MIT.

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

For decks, slide titles, speaker notes and supporting bullets obey the same source rule. Put optional action ideas under an explicit Proposed actions label. Visual polish and launch dates do not establish operational status.

## Finite reorder subset

    node scripts/pptx_tool.mjs reorder --input /owned/input/deck.pptx --output /owned/output/reordered.pptx --order 2,1

Order is a complete unique 1-based permutation of all existing slides (maximum
20). Ordinary p:/r: namespace spellings, unique IDs, internal slide relationship
types and standard PPTX content type are required; unsupported or ambiguous
lists are refused. Only ppt/presentation.xml changes its slide-list order. All
other uncompressed part bytes, IDs, relationships, notes, media and shared
objects are preserved, not rebuilt. Verify saved relationship order, complete
part identities and unchanged source before exclusive publication.

This does not delete/duplicate slides, repair graphs or normalize XML namespaces.
Existing visible slide-number shapes are not renumbered. Archive compression
bytes can differ. Input shared graph validity and Office application fidelity
are not automatically certified. Every actual reordered slide still needs
independent saved-XML and rendered visual QA; helper unit tests are not that QA.

## Installed package paths

Commands above are relative to the directory containing this SKILL.md. Dependency locks/package.json and licenses are at the plugin root, not the Skill root. The Host must expose an executable path or usable provisioned backend before running code; reading a resource does not execute it. Do not assume a private renderer or library environment is bundled.
