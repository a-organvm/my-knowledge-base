#!/usr/bin/env python3
"""Generate compensable hours breakdown graph for adjunct faculty work.

Resolves prompt-cd686c8b4751 (P0/PARTIAL):
"Same for this, but can we condense and make into a graph?"

Data from user's tracked Canvas/grading/training hours at St. Paul's
School of Nursing + Broward College adjunct positions (Jan-Mar 2025).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def build_hours_data() -> dict:
    """Structure the compensable hours data."""
    return {
        "title": "Extra Compensable Hours Beyond Classroom Instruction",
        "period": "January-March 2025",
        "categories": [
            {
                "name": "ENG 101 (Composition, 6-week Module)",
                "subcategories": [
                    {"name": "Canvas Time (Outside Class)", "hours": 31.0},
                    {"name": "Grading & Feedback", "hours": 12.0},
                    {"name": "Mid-Module Evaluations", "hours": 2.0},
                    {"name": "Final Grade Submission", "hours": 0.5},
                    {"name": "Course Redesign & Admin", "hours": 10.0},
                    {"name": "Student Correspondence", "hours": 1.0},
                ],
                "total": 25.5,
                "note": "Subtracted 35 hrs in-class Canvas usage from 66 hrs total",
            },
            {
                "name": "ENG 204 (Literature, 15-week Course)",
                "subcategories": [
                    {"name": "Canvas Time (Outside Class)", "hours": 33.0},
                    {"name": "Canvas Course Redesign", "hours": 20.0},
                    {"name": "Grading & Weekly Feedback", "hours": 50.0},
                    {"name": "Student Correspondence", "hours": 1.0},
                ],
                "total": 71.0,
                "note": "Subtracted 10 hrs in-class usage from 43 hrs total",
            },
            {
                "name": "Additional ENG 101 (First 3 Weeks)",
                "subcategories": [
                    {"name": "Grading & Feedback", "hours": 6.0},
                    {"name": "Admin & Course Adjustments", "hours": 3.0},
                ],
                "total": 9.0,
                "note": "Took over mid-course due to faculty departure",
            },
            {
                "name": "Mandatory Trainings & Meetings",
                "subcategories": [
                    {"name": "Faculty Development (FDP300)", "hours": 6.0},
                    {"name": "Title IX Training", "hours": 0.5},
                    {"name": "Cybersecurity Training", "hours": 0.5},
                    {"name": "Drugs & Alcohol Training", "hours": 0.5},
                    {"name": "Sexual Harassment Prevention", "hours": 0.5},
                    {"name": "Faculty Observation", "hours": 1.0},
                    {"name": "Faculty Friday Meeting", "hours": 1.0},
                ],
                "total": 10.0,
                "note": "Required but unpaid under hourly model",
            },
        ],
        "grand_total": 115.5,
        "comparison": [
            {"institution": "CUNY", "model": "Flat rate ($100/hr)", "for_60hrs": "$6,000"},
            {"institution": "Wagner College", "model": "$46-86/hr (avg $66)", "for_60hrs": "$3,960"},
            {"institution": "Rutgers", "model": "$2,400-2,700/credit", "for_60hrs": "$7,200-$8,100"},
        ],
    }


def render_text_graph(data: dict) -> str:
    """Render a text-based horizontal bar chart."""
    lines: list[str] = []
    lines.append(f"{'=' * 72}")
    lines.append(f"  {data['title']}")
    lines.append(f"  Period: {data['period']}")
    lines.append(f"{'=' * 72}")
    lines.append("")

    max_hours = max(c["total"] for c in data["categories"])
    bar_width = 40

    for cat in data["categories"]:
        lines.append(f"  {cat['name']}")
        lines.append(f"  {'─' * 60}")

        for sub in cat["subcategories"]:
            bar_len = int((sub["hours"] / max_hours) * bar_width)
            bar = "█" * bar_len
            lines.append(f"    {sub['name']:<35} {bar} {sub['hours']:>5.1f}h")

        lines.append(f"    {'':35} {'─' * 45}")
        lines.append(f"    {'SUBTOTAL':<35} {'':>40} {cat['total']:>5.1f}h")
        if cat.get("note"):
            lines.append(f"    Note: {cat['note']}")
        lines.append("")

    lines.append(f"  {'═' * 60}")
    lines.append(f"  {'GRAND TOTAL':<35} {'':>18} {data['grand_total']:>5.1f}h")
    lines.append(f"  {'═' * 60}")
    lines.append("")

    # Comparison table
    lines.append("  Adjunct Compensation Comparison (for 60 contact hours):")
    lines.append(f"  {'─' * 55}")
    lines.append(f"    {'Institution':<20} {'Pay Model':<22} {'Amount':<15}")
    lines.append(f"    {'─' * 50}")
    for comp in data["comparison"]:
        lines.append(
            f"    {comp['institution']:<20} {comp['model']:<22} {comp['for_60hrs']:<15}"
        )
    lines.append(f"  {'─' * 55}")
    lines.append("")

    return "\n".join(lines)


def render_html_graph(data: dict) -> str:
    """Render an HTML bar chart for the hours breakdown."""
    max_hours = max(c["total"] for c in data["categories"])

    colors = ["#4A90D9", "#D95B43", "#6AB187", "#C7B42C"]

    rows = []
    for i, cat in enumerate(data["categories"]):
        color = colors[i % len(colors)]
        pct = (cat["total"] / data["grand_total"]) * 100

        sub_rows = []
        for sub in cat["subcategories"]:
            sub_pct = (sub["hours"] / max_hours) * 100
            sub_rows.append(
                f'<tr><td style="padding-left:2em;font-size:0.9em;">{sub["name"]}</td>'
                f'<td style="width:50%"><div style="background:{color};opacity:0.7;'
                f'width:{sub_pct:.0f}%;height:20px;border-radius:3px;"></div></td>'
                f'<td style="text-align:right;font-weight:bold;">{sub["hours"]:.1f}h</td></tr>'
            )

        rows.append(
            f'<tr style="background:#f0f0f0;"><td colspan="2"><strong>{cat["name"]}</strong></td>'
            f'<td style="text-align:right;font-weight:bold;font-size:1.1em;">{cat["total"]:.1f}h '
            f'({pct:.0f}%)</td></tr>'
        )
        rows.extend(sub_rows)

    comp_rows = []
    for comp in data["comparison"]:
        comp_rows.append(
            f'<tr><td>{comp["institution"]}</td>'
            f'<td>{comp["model"]}</td>'
            f'<td style="text-align:right;font-weight:bold;">{comp["for_60hrs"]}</td></tr>'
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{data['title']}</title>
<style>
body {{ font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 800px; margin: 2em auto; padding: 0 1em; }}
h1 {{ font-size: 1.4em; border-bottom: 2px solid #333; padding-bottom: 0.5em; }}
table {{ width: 100%; border-collapse: collapse; margin: 1em 0; }}
td {{ padding: 6px 8px; border-bottom: 1px solid #ddd; }}
.total {{ background: #333; color: white; font-size: 1.2em; }}
</style>
</head>
<body>
<h1>{data['title']}</h1>
<p>Period: {data['period']}</p>

<table>
{''.join(rows)}
<tr class="total"><td colspan="2"><strong>GRAND TOTAL</strong></td>
<td style="text-align:right;font-weight:bold;font-size:1.3em;">{data['grand_total']:.1f}h</td></tr>
</table>

<h2>Adjunct Pay Comparison (60 contact hours)</h2>
<table>
<tr style="background:#f0f0f0;font-weight:bold;"><td>Institution</td><td>Pay Model</td><td style="text-align:right;">Amount</td></tr>
{''.join(comp_rows)}
</table>

<p style="font-size:0.8em;color:#666;">Note: St. Paul's requires hourly clock-in/out rather than per-course salary.
Canvas time tracked automatically. Grand total represents work beyond compensated classroom hours.</p>
</body>
</html>"""


def main() -> None:
    data = build_hours_data()

    # Always print text version
    print(render_text_graph(data))

    # Write JSON data
    json_path = Path(__file__).parent / "compensable_hours_data.json"
    json_path.write_text(json.dumps(data, indent=2))
    print(f"JSON data written to: {json_path}")

    # Write HTML version
    html_path = Path(__file__).parent / "compensable_hours_graph.html"
    html_path.write_text(render_html_graph(data))
    print(f"HTML graph written to: {html_path}")


if __name__ == "__main__":
    main()
