# Manuscript synchronization

Latest update: [13 November 2026](#pluginrsi-discussion-update--13-november-2026). Earlier revisions are retained below for provenance.

## Initial synchronization — 17 October 2026

The full report and short paper are separate source projects. Their current sources were synchronized from Overleaf; the public OpenReview and arXiv URLs remain the publication links and are not assumed to serve these exact builds.

| Artifact | Source commit | Local verification build |
|---|---|---|
| [Full report](../paper/harness-self-evolution.pdf) | `75a40cdb3bcc0045518be84acc85ca5ae0d8d05c` | 66 pages, 262 bibliography entries |
| [Short paper](../paper/self-evolving-agent-harness.pdf) | `fd8ad5c518f5372f66df6857d5339814ddb6037a` | 18 pages, 85 bibliography entries |

Source and PDF hashes are recorded in [source-snapshot.json](../data/source-snapshot.json). Bibliographies are copied verbatim from the respective sources: [full](../paper/harness-self-evolution-references.bib) and [short](../paper/self-evolving-agent-harness-references.bib).

## Changes reflected in the companion materials

- Replace the website abstract with the current full-report abstract; align the Chinese author list with all eight manuscript authors.
- Refresh the evaluation diagram and manuscript-derived tables and taxonomy, including current citation numbering.
- Clarify activation's carried grade: downstream runtime decisions and outputs count alongside model-input propagation and interpreted-guidance adherence. This is a terminology clarification, not a recoding of primary comparisons.
- Reflect the expanded discussion of runtime composition, medical tool admission, environment design, compositional contracts, dynamic evaluation, and authorization boundaries.
- Preserve the short paper's case-study qualifications: unmatched-cost model crossovers, inconsistent first-task and cumulative EIP costs, and fixed-deployment latency evidence.

The 95-method scope, 93 scored comparisons, raw audit records, and verdicts are unchanged. The evidence date remains 10 October 2026 and the literature cutoff remains 8 October; the synchronization date does not imply a new literature search or audit.

## Verification

At the 17 October synchronization, both PDFs were built locally with `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` from the recorded source commits. Builds resolve citations and references without overfull boxes. The full report retains font-size substitution and caption/hypcap warnings; these were not source edits. Local compilation does not verify Overleaf cloud compilation or update the external publication PDFs.

## Full-report PDF update — 18 October 2026

The distributed [full-report PDF](../paper/harness-self-evolution.pdf) was replaced with the user-provided `HarnessOpt_survey (4).pdf` (66 pages). The README and project-page full-version links now open the GitHub PDF. Its SHA-256 is recorded as `sha256.main.pdf` in [source-snapshot.json](../data/source-snapshot.json). The source snapshot and short paper remain unchanged; correspondence between the replacement PDF and the recorded source commit has not been verified. The local-build verification above describes the earlier PDFs.

## Harness-Zero citation update — 23 October 2026

Added [Harness-Zero](https://arxiv.org/abs/2609.24974) to the full report's Model–Harness–Environment Co-Evolution subsection and the short paper's Model–Harness Co-Design subsection. Both describe distillation into model weights while retaining a minimal target harness, and connect it to future harness evolution.

| Artifact | Source commit | Local verification build |
|---|---|---|
| [Full report](../paper/harness-self-evolution.pdf) | `e76b3ffafba3aa6fe4548539e785090e57a0c1a6` | 66 pages, 263 bibliography entries |
| [Short paper](../paper/self-evolving-agent-harness.pdf) | `ff66a471e3f0fe07c9e35bd0c0147fd74af7a8e8` | 18 pages, 86 bibliography entries |

Both distributed PDFs and bibliography files now match these source revisions; this supersedes the 18 October PDF provenance caveat. Builds resolve all citations and references without overfull boxes. The new paragraphs and bibliography entries were visually inspected. Existing full-report font substitution and caption/hypcap warnings remain. Overleaf cloud compilation has not been verified. No audit entries or verdicts were changed, and arXiv has not been updated.

## Compositional safety update — 1 November 2026

Added [Compositional Safety Failures in Harness Evolution](https://arxiv.org/abs/2609.33123) to the short paper's §6.5 Safety Boundaries for Self-Modifying Systems and the full report's §8.4 Privacy, Security, and Systemic Stability. The short paper cites runtime monitoring and its coverage limits; the full report adds the observed pairwise and irreducible three-way failures. The bilingual reading lists and website explorer include the work as a regular entry under Attribution Controls. The taxonomy image was regenerated to keep its citation numbers aligned with the updated bibliography.

| Artifact | Source commit | Local verification build |
|---|---|---|
| [Full report](../paper/harness-self-evolution.pdf) | `10c71251f211457a7d6ea2d5c19c7f6f3501191d` | 66 pages, 264 bibliography entries |
| [Short paper](../paper/self-evolving-agent-harness.pdf) | `cc57cd278cf6962a18fa88b96d7500c6095c3c02` | 18 pages, 87 bibliography entries |

Both source commits were pushed to Overleaf and verified against its remote main branches. Distributed PDFs and bibliographies are copied from the same locally verified revisions. Both PDFs compile without unresolved references or overfull boxes, retain their page counts, and have been visually checked at the changed passages and bibliography entries. Existing full-report font substitution and caption/hypcap warnings remain; Overleaf cloud compilation and external publication PDFs have not been updated or verified by this synchronization.

This targeted citation update adds no audit verdicts and changes neither the 95-method scope nor the 93 scored comparisons. The audit date remains 10 October 2026 and the literature cutoff remains 8 October 2026.

## PluginRSI discussion update — 13 November 2026

Added [PluginRSI](https://arxiv.org/abs/2609.32423) to the full report's §4.3 Everything Is a Plugin and §9.3 Synthesis and Reuse of Harness Plugins, and to the short paper's §3.3 Everything Is a Plugin. The discussion distinguishes interpreted instructions from executable implementations and describes library reuse as support for further optimization. The bilingual reading lists link to the [official implementation](https://github.com/syr-cn/PluginRSI).

| Artifact | Source commit | Local verification build |
|---|---|---|
| [Full report](../paper/harness-self-evolution.pdf) | `681687fc24502a2fab84ef1a450c597202ef7666` | 66 pages, 265 bibliography entries |
| [Short paper](../paper/self-evolving-agent-harness.pdf) | `f7a748e946518077947d8ee895949ca98de981cc` | 18 pages, 88 bibliography entries |

Both source commits were pushed to Overleaf and checked against its remote main branches. The distributed PDFs are the previously compiled and visually checked builds from these commits; their hashes were verified before publication. Bibliographies are copied from the same revisions. The taxonomy and evaluation-controls excerpts were refreshed only to align citation numbering with the full report. Builds have no unresolved references or overfull boxes; existing full-report font substitution and caption/hypcap warnings remain. Overleaf cloud compilation has not been verified, and the external arXiv and OpenReview PDFs were not updated.

The audit records, verdicts, statistical figures, 95-method scope, and 93 scored comparisons remain unchanged. This discussion-only addition does not change the audit date (10 October 2026) or literature cutoff (8 October 2026).
