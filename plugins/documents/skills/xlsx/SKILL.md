---
name: xlsx
description: Create bounded typed workbooks with numeric or boolean formula caches, inspect cells, or change primitive inputs and recalculate a supported formula subset including lazy IF using portable ExcelJS.
---

# Portable workbook operations

This independently authored plugin candidate uses public pinned ExcelJS 4.4.0 and the exact package-lock.json, not a private Codex installation. Install into an isolated owned Node runtime with scripts disabled. This beta supports only the documented bounded formula subset. Independent saved-workbook and rendering checks remain necessary for each artifact; finite Linux evidence is not source-wide or platform acceptance.

    node scripts/xlsx_tool.mjs create --input plan.json --output /owned/output/new.xlsx
    node scripts/xlsx_tool.mjs inspect --input /owned/output/new.xlsx
    node scripts/xlsx_tool.mjs set-cells --input /owned/output/new.xlsx --plan changes.json --output /owned/output/edited.xlsx

Create plan keys: title, author, sheets. Every sheet has name, rectangular values and widths. Optional formulas are cell/formula pairs with leading =; formats are range/code pairs, with optional header_row and freeze_rows. Cells are strings, finite numbers, booleans, null, or a date object with yyyy-mm-dd date. Numbers/dates remain typed. Formula cells contain both a real formula and a computed numeric or boolean cache, without replacing the formula with a hardcoded result.

ExcelJS itself does not calculate formula results. The included independently authored bounded AST parser supports numeric/boolean nonblank references, quoted/unquoted cross-sheet references, bounded aggregate ranges, parentheses, TRUE/FALSE literals, numeric unary signs, + - * / and SUM/MIN/MAX/AVERAGE. Comparisons =, <>, ==, !=, <, <=, >, >= return boolean caches; operands must have the same numeric or boolean type, and ordering is numeric only. Excel = and <> are preferred; == and != are narrow aliases, not promises of unrestricted Excel interoperability. Arithmetic/aggregates do not coerce booleans, blanks, dates or strings to numbers.

IF(condition, true_value, false_value) requires exactly three scalar arguments. A finite numeric condition uses zero=false/nonzero=true; boolean conditions are direct. Both branches are parsed and syntax-checked, but only the selected branch reads cells or evaluates arithmetic. Thus =IF(A2=0,0,(A2-B2)/A2) computes zero safely when A2=0 while still refusing a selected division by zero. Unsupported functions or malformed syntax in an unselected branch are rejected, not ignored. Unselected blank/missing-sheet/self-reference expressions are not read; separately defined invalid formula cells still fail whole-workbook recalculation. All caches are staged and assigned only after the entire calculation succeeds.

Unsupported functions, evaluated blank/text/date inputs, cycles, selected division by zero, external-workbook syntax, nonfinite results or resource bounds fail before publication. Limits include formula length1000, tokens400, syntax/dependency depth below100 and 200000 evaluation steps per recalculation, in addition to workbook bounds. This subset is not a general Excel engine. Formula/cache numeric and boolean storage types must be independently compared with expected results and saved OOXML; helper tests are not saved-workbook acceptance.

The changes plan contains sheet and changes with cell, old and value. Old must exactly match the current primitive value; formula/rich/date cells are not modified through this operation. Other formula caches recalculate. The input file remains unchanged, but arbitrary imported-workbook feature fidelity is not promised: separately compare every tab and all unrelated values/formulas/styles requested for preservation.

Input bounds are A1:L99, five worksheets, 10 MiB archive/25 MiB expanded/512 members, bounded JSON/text/formulas. ZIP deflation, CRC and member paths are checked. Macros/signatures are refused. Output uses sibling serialization and exclusive atomic linking, with no overwrite fallback. No provider, network, shell or input script execution is part of a CLI operation.

Inspect returns actual file SHA/size and typed cell values/formulas/caches/formats and views. Before acceptance, independently verify raw XML and typed values/caches, render every worksheet's populated range with the available independent reader/renderer and inspect every PNG. A wrong capacity can form a valid workbook and still fail the business oracle.

Not implemented: unrestricted formulas, shared/array formulas, charts, pivot tables, structured tables, comments, image objects, XLS/CSV conversions, encryption, arbitrary workbook fidelity, fullsource parity or autonomous model use. Codex artifact-tool is QA-only and is not redistributed. Original license is retained in licenses/source-xlsx-LICENSE.txt; new support is MIT.

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

For workbooks, preserve units and provenance of input values. A formula result is a derived value, not evidence of a real-world approval, causal conclusion or future outcome. Distinguish sourced inputs, calculated cells and explicitly labeled scenario assumptions.

## Installed package paths

Commands above are relative to the directory containing this SKILL.md. Dependency locks/package.json and licenses are at the plugin root, not the Skill root. The Host must expose an executable path or usable provisioned backend before running code; reading a resource does not execute it. Do not assume a private renderer or library environment is bundled.
