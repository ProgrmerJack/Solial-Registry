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

2026-10-01 — Spent three attempts guessing the consultation-portal API before finding it already documented.
Cause: regulation.adliya.uz paths were guessed from its JS bundle; the working read-only endpoint /api/api/aux-jk/v1/open/project was already recorded in docs/analysis_plan.md.
Correction: used the documented endpoint; all 40 drafts published 11 Sep–1 Oct 2026 checked, none is the PF-193 para 14 act.
Prevention: grep the repo (plans, logs, FAILURES.md) for previously found endpoints before probing an external service.

## 2026-10-05 — Verification safeguards did not fully match operative wording
Tried: relying on hierarchy-only reasoning, retained grounds and general coverage/confirmation clauses in the submission.
Failed: source comparison showed omitted favourable interpretation, undisclosed legal grounds, a narrower launch condition and unbounded internal diagnosis.
Rule: resolve the legal baseline explicitly; align disclosure and full required-case coverage; bound diagnosis while preserving complaint deadlines.
## 2026-10-05 — Electronic supplement omitted publication sources
Tried: supplying the full reproduction pipeline in the supplement without its maintained LaTeX sources or vendored TeX packages.
Failed: checked_sources against the archive raised FileNotFoundError for docs/normative_act_draft_ru.tex.
Rule: include every required source and dependency file, verify archive members against workspace hashes, and run reproduction from the extracted bundle.

## 2026-10-05 — Translation converted a drafting mandate into completed submission
Tried: translating “already mandated draft” into the Uzbek objection-response table.
Failed: fresh-context review found “allaqachon topshirilgan loyiha”, which states that submission already occurred.
Rule: distinguish an instruction to prepare a draft from completion or submission; verify temporal state as well as legal modality across editions.

## 2026-10-05 — Page-number conditional consumed the number as part of its comparison
Tried: rendering the shared header with \ifnum\value{page}>1\thepage\fi.
Failed: visual review and PDF header extraction found no page numbers in any of the nine documents.
Rule: terminate the comparison number with \relax before outputting \thepage; verify the first-page omission and later-page header values in rendered PDFs.

## 2026-10-05 — PDF header check ignored the current transformation matrix
Tried: locating headers using only pypdf visitor text-matrix coordinates.
Failed: the first check rejected a visibly numbered PDF because the coordinates were relative to the translated current matrix.
Rule: transform visitor coordinates to page space before comparing positions; confirm extracted header text against the rendered page.

## 2026-10-06 — Missing-data pause protected the clock but not benefit commencement
Tried: automatically pausing assessment for up to ten working days while leaving benefit-calendar rules unchanged.
Failed: APL36–38 require lawful suspension and notices; Resolution35 Annex1(16) is shorter and Annex3(10,11,18) can defer a qualifying first applicant’s payment month.
Rule: subordinate verification to the applicable deadline, require lawful suspension/resumption, and align all benefit-date clauses; document original eligibility before paying elapsed eligible periods.

## 2026-10-06–07 — Sequential patch hunks returned to an earlier source position
Tried: applying validated explanatory-note hunks after later-position headings or bibliography edits, including a return to the edition line on 7 October.
Failed: the patch tool rejected the batches because its sequential search could not return to an earlier source position; no file was written by either rejected batch.
Rule: order bounded hunks by their positions in the maintained source before applying them, then verify every target passage.

## 2026-10-06 — New payment safeguard outgrew the attached program’s stated scope
Tried: retaining the general claim that the attached program counts families affected by every amendment after adding benefit-date protection.
Failed: the maintained program contains income-rule calculations, not the processing-date and original-eligibility review required for the new safeguard.
Rule: distinguish computed income effects from separate administrative date and eligibility review; state when no affected-family count or payment-cost estimate is supplied.

## 2026-10-06 — Source revisions did not refresh exported papers
Tried: checking the nine revised sources in the native compiler without refreshing the saved publication package.
Failed: the saved submission PDFs and supplement still contained the 5 October edition while the sources contained the 6 October revision.
Rule: export all nine papers, refresh their submission copies and supplement, compare source/PDF/archive hashes, and reproduce from the extracted bundle.

## 2026-10-06 — Protected payment commencement left the benefit window unresolved
Tried: aligning benefit consideration and payment start through Annex 3 paragraphs 10, 11 and 18 alone.
Failed: paragraph 13 and PF-258(5)(v)(i) retain a category-entry clock, while paragraphs 12, 23 and 26 use its expiry; late detection can extend the proposed window.
Rule: align the protected entry date, single six-month window, original-request cutoff, arrears and fixed termination across both ranks, with explicit prospective scope and pre-use resource duties.

## 2026-10-07 — Quotation check selected an earlier section with reused numbering
Tried: extracting benefit amendments from the first occurrence of the paragraph-six marker.
Failed: section numbering restarts, so the check selected Section I and counted unrelated quotations.
Rule: anchor the section first, verify the expected quotation count, and inspect each language’s actual table labels before comparing full concatenated wording.

## 2026-10-07 — Piecewise domain omitted from affected-plot selector
Tried: describing the second negative-area branch as QM > UM − 200 without limiting it to plots larger than 1,000 m².
Failed: the selector admits UM = 100, QM = 0 although the literal area is positive (80 m²); it disagrees with 81 of the 4,105 existing constructed cases.
Rule: retain each piecewise branch’s domain in candidate filters and verify the combined predicate against every existing constructed case.

## 2026-10-07 — Table labels separated from their content after reflow
Tried: retaining an external Table 4 caption and an ordinary comparison-group row break while adding explanatory paragraphs.
Failed: the Russian caption moved to page 33 after its table on page 32; Uzbek section 12 and the Annex 3 group heading were also separated from their tables by page breaks.
Rule: keep captions inside the table, protect group-heading row breaks, reserve space before section headings that precede tables, and re-render affected pages after text revisions.

## 2026-10-07 — Starred longtable row did not protect a group heading
Tried: adding a starred row break before the booktabs rule after the Uzbek Annex 3 comparison heading.
Failed: compilation passed but rendered page 36 still ended with the heading while its first content row began page 37.
Rule: use an explicit table-page break before this annex group and verify the rendered heading and first row together; successful compilation does not establish pagination.

## 2026-10-07 — Render comparison assumed a fixed page-number width
Tried: finding every earlier page image with a two-digit page-number suffix.
Failed: cover-letter renders use one-digit suffixes, so comparison stopped after the three draft PDFs; numerical page matching confirmed all cover-letter pages unchanged.
Rule: match rendered pages by their parsed page number rather than assuming the renderer's filename padding.

## 2026-10-07 — Safeguard expansion turned the proposal into a rejectable package
Tried: adding a benefit-date module (Annex 3, PF-258 amendment), continuity/resource duties for the Ministry, an Art. 22 inclusion request and "necessity is not proven" caveats (Material 1 7→13 pages, Material 2 28→50).
Failed: scope left the PF-193 ¶14 subject, duties fell outside the Agency's competence, and the text supplied ready-made rejection wording; Art. 22 contradicted the user's proposal-only decision.
Rule: keep each norm within the ordered act and the addressee's competence, state limits once without conceding necessity, and check every edit against the standing submission decisions.
