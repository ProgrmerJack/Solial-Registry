## 2026-09-30 — Substring matching returned the wrong legal article
Tried: locating Article 3 with an unanchored `3-modda.` substring in retrieved legislation.
Failed: the lookup selected Article 83; an anchored lookup demonstrated the mismatch before it was used in the draft.
Rule: anchor article numbers at the start of a text line and verify the complete article heading before citing it.
## 2026-09-30 — Paragraph lookup matched an amendment date
Tried: finding paragraph 21 in Resolution 35 with the anchored pattern `^21\.`.
Failed: it returned the amendment date `21.07.2026`; full-heading inspection caught the mismatch before use.
Rule: require whitespace after the paragraph marker (`^21\.\s`) and verify the heading and next paragraph.
## 2026-09-30 — Equality amendment missed the hardship branch and decree annex
Tried: resolving equality by moving the entire borderline lower bound above P and listing only main category clauses.
Failed: review showed adjusted hardship income exactly P remains admissible under paragraph 35(b), and PF-258 Annex 1 note (a) still uses strict <P.
Rule: reconcile every cross-referenced annex and preserve separate ordinary-income and adjusted-income paths before changing a boundary.
## 2026-09-30 — Presentation layout preceded verification of government drafting format
Tried: publishing the research and draft as one colourful ReportLab document.
Failed: the user identified the inappropriate submission style; current O‘RQ-682 methodology also requires different draft geometry and pagination.
Rule: verify the applicable current instrument first, keep proposed law separate from its research explanation, and use a sober LaTeX layout with disclosed substitutions.
## 2026-09-30 — Operative citation was not checked against reference hierarchy
Tried: naming registered ministerial methodology No. 3620 in a clause proposed for a Cabinet or Presidential act.
Failed: the independent adoption review identified the prohibition on specific lower-ranking references in O‘RQ-682 appended methodology paragraph 11.
Rule: check the final instrument's rank before inserting operative references; keep lower-ranking source details in explanatory material where appropriate.
## 2026-09-30 — Reorganization left a stale prespecification reference
Tried: retaining the paper's PLAN.md reference after moving the plan to docs/analysis_plan.md.
Failed: the independent reviewer demonstrated that PLAN.md no longer exists in the workspace.
Rule: verify every referenced reproduction artifact after restructuring; preserve direct LaTeX editor changes when synchronizing generated sources.
2026-09-30: Editor compilation failed because the paper used external figure, table and bibliography files.
Cause: the built-in LaTeX compiler accepts a standalone source and could not load the external figure PDF.
Correction: embed tables, bibliography and native vector plots in the existing manuscript source.
Prevention: check the maintained standalone source with the built-in compiler before reporting compilation success.
2026-09-30: A single shell invocation for the full Russian manuscript exceeded the process argument limit.
Cause: a large UTF-8 translation was passed as one command argument; the process did not start and wrote nothing.
Correction: write the requested translation in bounded patches, then assemble embedded elements from verified sources.
Prevention: use file patches for large document text rather than an oversized shell command argument.
2026-09-30: The Russian land-result table omitted the domains of its two negative-area inequalities.
Cause: translating the inequalities without the U≤1000 and U>1000 branches misclassified the constructed U=100, B=50 case.
Correction: restore both branch conditions and reread the translation against the piecewise derivation.
Prevention: verify equations together with their domains and counterexamples in every translated results table.
2026-09-30: The initial three-column comparison omitted the statutory change markup.
Cause: paragraph 85 was checked for column structure before its subsequent formatting instructions were applied.
Correction: italic-underline replaced current wording and bold proposed replacements or additions; independently reread both languages.
Prevention: inspect each cited drafting requirement through its complete provision, including instructions after the initial list.
2026-09-30: Successful editor compilation did not reveal terminal layout and package failures.
Cause: the editor supplied packages missing from terminal TeX, while Russian hyphenation and full-size command lines needed separate diagnostics.
Correction: install standard packages project-locally, use Russian Babel and wrap commands; all ten no-PDF layout checks pass.
Prevention: distinguish compiler success from layout verification and record each engine and its package environment.
2026-09-30: The local TeX search helper dropped default paths when a prior custom TEXINPUTS lacked a trailing separator.
Cause: concatenation appended the prior value without guaranteeing a final empty search component.
Correction: append the platform separator and verify kpsewhich article.cls with unset, custom and trailing-separator prior values.
Prevention: test dependency-search helpers with both empty and nonempty existing settings before claiming defaults are retained.

## 2026-09-30 — Undefined institutional shorthand
Tried: used shortened Agency/Ministry names after their full names without an express definition.
Failed: independent review demonstrated the missing first-use parenthesis required by O‘RQ-682 appendix paragraph 9.
Rule: define repeated institutional names in parentheses at the first operative occurrence, or verify an existing definition in the containing act.

## 2026-09-30 — Qualified legal caution became a prohibition in translation
Tried: translated a caution about unconditional recovery promises as a categorical statutory prohibition.
Failed: independent EN/UZ comparison demonstrated a stronger legal claim than the source supported.
Rule: preserve the force and qualifications of legal claims during translation; compare modality as well as numbers.

## 2026-09-30 — Bold formula silently used a regular math font
Tried: marked proposed formula changes with boldmath while the math font supplied no bold shape.
Failed: XeLaTeX diagnostics disclosed regular-font substitution in all three comparison tables.
Rule: verify changed-word emphasis in compiler diagnostics; use an available bold text font for this simple formula without changing its algebra.
2026-10-01: A multilingual patch failed its Uzbek heading check and wrote no files.
Cause: the patch used a translated heading without checking the exact maintained wording.
Correction: search the existing subsection headings and retry against the actual source.
Prevention: verify every language-specific patch anchor before batching translated edits.
2026-10-01: Two English passages attributed an existing statutory duty to the institution rather than its officials.
Cause: a compressed paraphrase dropped the personally responsible subject in Resolution 35 annex 1 paragraph 46.
Correction: restore the responsible officials in the English request and explanatory note, matching Uzbek and Russian.
Prevention: compare the actor bearing a duty, not only the duty itself, against the opened provision in every translation.
2026-10-01: Two bounded LaTeX patches were rejected before mutation.
Cause: a partial paragraph-line hunk and an invalid file marker failed validation.
Correction: use verified whole-line anchors and valid generated patch markers; neither rejected call wrote files.
Prevention: verify exact maintained lines and patch syntax before multilingual mutation.
2026-10-01: A new necessity paragraph overstated Resolution 35 annex 1 paragraph 49.
Cause: its oversight duty was expanded into an uncited proposal duty in three languages.
Correction: reread the operative paragraph and restore oversight only; independent reviewer verified all three.
Prevention: trace each asserted duty and actor to the precise operative provision, not a summary.
2026-10-01: Some note wording implied global unavailability of the 2027 score specification.
Cause: project nonreceipt and unsuccessful searches were generalized into publication status.
Correction: state that the official specification has not been obtained for this project.
Prevention: distinguish missing project evidence from verified nonexistence or nonpublication.
2026-10-01: A review-report tool script failed JavaScript parsing before execution.
Cause: Markdown backticks inside an unescaped template literal terminated it.
Correction: construct valid string content; the rejected script performed no file mutations.
Prevention: escape Markdown delimiters or use structured strings before executing report-writing code.

Date: 2026-10-01 — independent checker accepted incomplete or coerced case inventories.
Failure: Iteration-only checks accepted empty grids; int coercion and bool/int equality concealed changed case inputs.
Cause: No frozen identity/multiplicity guard or strict input-type check before independent algebra.
Fix: Match frozen inventories, check exact integers/booleans and income predicates; six new regressions pass with unchanged numerical findings.

2026-10-01 — A multilingual editorial batch halted after earlier files had been saved.
Cause: a translated paragraph anchor was inferred rather than matched to its current text.
Correction: inspect exact paragraphs, finish bounded edits and scan all language versions independently.
Prevention: prevalidate every target and anchor before any batch write; include intros, conclusions and outcome recipes.

2026-10-01 — A publisher guard check failed under the system Python.
Cause: its Markdown dependency is installed in the existing project environment, not system Python.
Correction: run the guard and Markdown parsing with .venv/bin/python; all checks passed.
Prevention: use the documented project environment for publication modules; the calculation engine remains standard-library only.

2026-10-01 — Optional terminal layout checks omitted the existing project TeX search environment.
Cause: bare XeLaTeX could not find project-local ulem and Russian language packages.
Correction: use build_documents.compiler_environment() and the docs working directory; native-editor compilation had succeeded.
Prevention: reuse the established compiler environment for diagnostics; distinguish environment failures from source errors.

2026-10-01 — A new operative cost clause named a Cabinet act while the proposed adopting instrument remained unspecified.
Cause: a verified costing source was inserted into normative text without checking the possible rank of the final act.
Correction: the clause now requires identification of applicable costing rules; the exact Cabinet citation stays in explanatory material.
Prevention: apply O‘RQ-682 appended methodology paragraph 11 to normative references before inserting a verified source.

2026-10-01 — The first launch reserve excluded a missing approved rule and could replay the old equality gap.
Cause: its trigger assumed an approved new rule; the preserved ordinary category condition remained strict at D=P.
Correction: include rule absence, specify inclusive ordinary primary and strict ordinary former-primary boundaries, preserve the special hardship route, and require a lawful verified reserve answer.
Prevention: check no-approved-rule, new-applicant D=P, former-category D=P and adjusted-hardship A=P cases before claiming a complete fallback.

2026-10-01 — A multilingual edit precheck matched two Uzbek resource headings and saved no files.
Cause: a broad translated substring selected both alternatives and implementation subsections.
Correction: select the exact maintained implementation heading and complete the scoped batch only after every anchor validates.
Prevention: validate every translated anchor before any write; preserve the existing source when validation fails.

2026-10-01 — Preparatory dates were placed in provisions proposed for the later adopting act.
Cause: duties before submission of the principal draft were copied into its prospective operative clauses.
Correction: operative reconciliation and resource duties now apply before first use; pre-submission preparation remains in the explanatory material under existing procedures.
Prevention: distinguish the developer's current preparation from duties created by the future act before assigning a deadline.

2026-10-01 — Public operational sources could not establish verification-module feasibility.
Cause: service counters lack accumulation periods and handling times; general budget/project provisions do not establish module-specific staff or funds.
Correction: reuse existing release controls, withdraw the unfunded manual/Presidential reserve and mandatory new report; do not claim measured capacity or cost.
Prevention: require dated workload, time, contract and funding evidence before asserting incremental operational feasibility.

2026-10-01 — Scoped multilingual patch selectors failed on differing maintained wording.
Cause: differing Russian prefixes stopped the first batch after its English save; later selector prechecks prevented further partial saves.
Correction: inspect exact maintained lines, validate all selectors and complete bounded replacements in each language.
Prevention: retain a recoverable edit command and validate exact language-specific anchors before mutation.
