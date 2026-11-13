#!/usr/bin/env python3
"""Generate evidence tables and site/README summaries from data/reported-evidence.json."""
import argparse
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ['selection', 'activation', 'attribution', 'improvement']
BADGE = {'C': '✅', 'O': '◐', 'N': '—', 'X': 'n/a'}


def load_evidence():
    data = json.loads((ROOT / 'data/reported-evidence.json').read_text(encoding="utf-8"))
    methods = data['methods']
    assert len({r['key'] for r in methods}) == len(methods), 'Duplicate method key'
    for row in methods:
        assert all(row[c] in BADGE for c in CLAIMS), row['key']
        assert all(row[c] == 'X' for c in CLAIMS) or all(row[c] != 'X' for c in CLAIMS), row['key']
        assert row['basis'] and (row['headline'] or row['selection'] == 'X'), row['key']
    scored = [r for r in methods if r['selection'] != 'X']
    per = [{code: sum(r[c] == code for r in scored) for code in 'CON'} for c in CLAIMS]
    joint = [sum(sum(r[c] == 'C' for c in CLAIMS) == k for r in scored) for k in range(5)]
    return data, scored, per, joint


def table(per, zh=False):
    lines = ['| Claim | ✅ '+('满足' if zh else 'Met')+' | ◐ '+('部分' if zh else 'Partial')+' | — '+('未满足' if zh else 'Not met')+' |', '|---|---:|---:|---:|']
    for name, counts in zip(CLAIMS, per):
        lines.append('| '+name.capitalize()+' | '+' | '.join(str(counts[c]) for c in 'CON')+' |')
    return '\n'.join(lines)


def summary(data, scored, per, joint, zh=False, compact=True):
    total, n = len(data['methods']), len(scored)
    if zh:
        intro = f'两个更新对象分支共收录 {total} 个方法，其中 {total-n} 个没有实证评测。下表依据其余 {n} 份报告的主要比较，分别判定四项 claims 的证据。'
        all_four = '没有报告四项均满足' if joint[4] == 0 else f'{joint[4]} 份报告四项均满足'
        finding = f'同一项比较中，{joint[3]} 份报告满足三项 evidence criteria，{all_four}。各项标准与覆盖范围不同，数量不能直接用于比较方法质量。'
        links = '各方法的比较设置、判定与来源见[完整结果](docs/reported-evidence.md)，具体要求见[判定标准](docs/evidence-criteria.md)。'
    else:
        intro = f'The two update-target branches contain {total} methods; {total-n} report no empirical evaluation. The counts below cover the other {n} reports, using one primary comparison per report for all four claims.'
        all_four = 'none meet all four criteria' if joint[4] == 0 else f'{joint[4]} meet all four criteria'
        finding = f'Within one comparison, {joint[3]} reports meet three criteria and {all_four}. Criteria and coverage differ across claims, so these counts do not rank method quality.'
        links = 'See the [full results](docs/reported-evidence.md) for comparisons, judgments, and sources, and the [criteria](docs/evidence-criteria.md) for their definitions.'
    parts = [intro, table(per, zh), finding]
    if compact:
        intro = (
            f'四项 claims 的证据分布，依据 {n} 份报告各自的主要比较；另有 {total-n} 个方法未报告实证评测。'
            if zh else
            f'Evidence for the four claims across {n} primary reported comparisons; {total-n} methods without empirical evaluation are excluded.'
        )
        alt = '四项 claims 的证据分布与整体覆盖情况' if zh else 'Evidence by claim and overall coverage'
        figure = f'[![{alt}](assets/reported-evidence.png)](assets/reported-evidence.png)'
        finding = (
            '最常见的证据组合满足 Selection 与 task-distance 标准，而 Activation 和 Attribution 仅部分满足：报告往往在留出任务上评测，但较少确认 accepted update 在计分运行中实际执行，也较少将其效果与运行波动及额外推理开销区分开。'
            if zh else
            'The most common evidence profile meets Selection and task distance, with partial Activation and Attribution: reports often evaluate on held-out tasks, but less often confirm that accepted updates execute in scored runs or separate their effects from run variation and extra inference compute.'
        )
        parts = [intro, figure, finding, links]
    else:
        parts.extend([
            'Number of criteria met within one primary comparison. A report with none may still provide partial evidence.',
            '| 0 | 1 | 2 | 3 | 4 |\n|---:|---:|---:|---:|---:|\n| ' + ' | '.join(map(str, joint)) + ' |',
            'The most common profile meets the Selection and task-distance criteria, with partial Activation and Attribution. Activation can rest on one confirmed scored-run case, with coverage recorded separately. Improvement grades task distance alone. Four-of-four is not a universal requirement for a final-state comparison.',
        ])
    return '\n\n'.join(parts)


def prose(text):
    """Keep source comparisons such as < and > visible in Markdown."""
    return html.escape(' '.join(text.split()), quote=False)


def render_basis(row):
    if row['selection'] == 'X':
        return prose(row['basis'])
    parts = re.split(r'(?:^|;)\s*(SEL|ACT|ATT|IMP):\s*', row['basis'])
    assert not parts[0].strip() and parts[1::2] == ['SEL', 'ACT', 'ATT', 'IMP'], row['key']
    labels = {'C': 'Criterion met', 'O': 'Partly met', 'N': 'Not met'}
    return '\n\n'.join(
        f'**{claim.capitalize()} ({labels[row[claim]]}).** {prose(basis)}'
        for claim, basis in zip(CLAIMS, parts[2::2])
    )


def render_doc(data, scored, per, joint):
    methods = sorted(data['methods'], key=lambda row: row['name'].lower())
    by_key = {row['key']: row for row in methods}
    out = [
        '# Reported Evidence',
        'Evidence for Selection, Activation, Attribution, and Improvement in each method’s primary reported comparison. The [criteria](evidence-criteria.md) define the judgments; the [reading list](../README.md#evidence) gives a short summary.',
        '[Summary](#summary) · [By update target](#by-update-target) · [Verdicts](#verdicts) · [Method details](#method-details) · [Other protocols](#other-protocols)',
        '## Summary',
        summary(data, scored, per, joint, compact=False),
        '![Reported evidence from the companion manuscript](../assets/reported-evidence.png)',
        '## By update target',
    ]
    rows = ['| Update target | Reports | Sel. ✅ | Act. ✅ | Att. ✅ | Imp. ✅ |', '|---|---:|---:|---:|---:|---:|']
    for sub in dict.fromkeys(row['sub'] for row in data['methods']):
        group = [row for row in scored if row['sub'] == sub]
        counts = [sum(row[claim] == 'C' for row in group) for claim in CLAIMS]
        rows.append('| ' + sub + ' | ' + ' | '.join(map(str, [len(group), *counts])) + ' |')
    out.extend(['\n'.join(rows), '## Verdicts', '✅ Criterion met · ◐ Partly met · — Not met · n/a No empirical evaluation. All four cells refer to the same primary comparison. Open a method’s details for the supporting passages and coverage.'])
    rows = ['| Method · primary report | Update target · details | Sel. | Act. | Att. | Imp. |', '|---|---|:-:|:-:|:-:|:-:|']
    for row in methods:
        rows.append(
            f'| [**{row["name"]}**]({row["url"]}) <sub>`{row["venue"]}`</sub> | '
            f'{row["branch"].split()[0]} · {row["mechanism"]} · [details](#{row["key"]}) | '
            + ' | '.join(BADGE[row[claim]] for claim in CLAIMS) + ' |'
        )
    out.extend(['\n'.join(rows), '## Method details', 'Expand a method to read its primary comparison and the basis for each claim. Section, table, and figure references refer to the linked primary report. Calculations and coverage come from the manuscript’s per-method records.'])
    for row in methods:
        headline = prose(row['headline']) if row['headline'] else 'No empirical evaluation.'
        out.append(
            f'<a id="{row["key"]}"></a>\n\n<details>\n'
            f'<summary><strong>{html.escape(row["name"])}</strong></summary>\n\n'
            f'[Primary report]({row["url"]})\n\n**Primary comparison.** {headline}\n\n'
            + render_basis(row) + '\n\n</details>'
        )
    out.extend(['## Other protocols', 'These secondary experiments are recorded separately and excluded from the totals above.'])
    for row in data['secondary']:
        out.append(
            f'### {by_key[row["key"]]["name"]}\n\n'
            f'**Protocol.** {prose(row["protocol"])}\n\n'
            f'Selection: {BADGE[row["selection"]]} · Improvement: {BADGE[row["improvement"]]}\n\n'
            f'{prose(row["basis"])}'
        )
    out.extend([
        '## Data and reproduction',
        '[Evidence data](../data/reported-evidence.json) · [Taxonomy](../data/taxonomy.json) · [Manuscript snapshot](../data/source-snapshot.json). This document is generated by `python3 scripts/build_evidence.py`; see [Contributing](../CONTRIBUTING.md) for corrections.',
    ])
    return '\n\n'.join(out) + '\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    data,scored,per,joint=load_evidence()
    expected={ROOT/'docs/reported-evidence.md':render_doc(data,scored,per,joint)}
    for lang,path in [('en','README.md'),('zh','README_zh.md')]:
        target=ROOT/path
        replacement='<!-- evidence-summary:start -->\n\n'+summary(data,scored,per,joint,lang=='zh')+'\n\n<!-- evidence-summary:end -->'
        text,count=re.subn(r'<!-- evidence-summary:start -->.*?<!-- evidence-summary:end -->',lambda _:replacement,target.read_text(encoding="utf-8"),flags=re.S)
        assert count==1,path
        expected[target]=text
    target = ROOT / 'index.html'
    total, n = len(data['methods']), len(scored)
    population = (
        f'{total} methods in scope; {n} primary comparisons are scored. '
        f'{total-n} methods without empirical evaluation are excluded. '
        'Criteria describe reported evidence within its recorded coverage.'
    )
    text, count = re.subn(
        r'(<p class="sec-sub" id="evidence-population">).*?(</p>)',
        lambda match: match[1] + population + match[2], target.read_text(encoding="utf-8"), flags=re.S,
    )
    assert count == 1, 'index.html: missing or duplicate evidence population'
    expected[target] = text
    stale=[str(p.relative_to(ROOT)) for p,text in expected.items() if not p.exists() or p.read_text(encoding="utf-8")!=text]
    if args.check:
        if stale:raise SystemExit('Evidence artifacts are stale: '+', '.join(stale))
    else:
        for path,text in expected.items():path.write_text(text, encoding="utf-8")
    print(f'Evidence: {len(data["methods"])} methods, {len(scored)} scored; '+('checked' if args.check else 'generated'))

if __name__=='__main__':
    main()
