#!/usr/bin/env python3
"""Calculate and fill ENC1101 syllabus due dates for Summer 2025 session.

Resolves prompt-4fee8317690e (P0/PARTIAL):
"this class runs 5/13/25 to 6/23/25, below is the course syllabus with
placeholders for due dates, please work out the due dates"

Course structure: 6 weeks, Mon-Thu, 5/13/25 to 6/23/25
All assignments due by 11:30 PM on their respective dates.
"""
from __future__ import annotations

import json
from datetime import date, timedelta


def compute_schedule() -> dict:
    """Compute the full course schedule with due dates.

    6-week course: 5/13/2025 to 6/23/2025
    Classes meet Mon-Thu.
    Structure: Orientation + 4 Units (each ~1-1.5 weeks)
    """
    start = date(2025, 5, 13)
    end = date(2025, 6, 23)

    # Generate all class days (Mon-Thu)
    class_days: list[date] = []
    current = start
    while current <= end:
        if current.weekday() < 4:  # Mon=0, Thu=3
            class_days.append(current)
        current += timedelta(days=1)

    # Week boundaries
    weeks: list[list[date]] = []
    week: list[date] = []
    for d in class_days:
        if week and d.weekday() == 0:  # Monday = new week
            weeks.append(week)
            week = []
        week.append(d)
    if week:
        weeks.append(week)

    def fmt(d: date) -> str:
        return d.strftime("%-m/%d")

    # Schedule allocation (6 weeks mapped to course units)
    schedule = {
        "course": "ENC1101 Composition I",
        "term": "Summer 2025",
        "dates": f"{fmt(start)} - {fmt(end)}",
        "weeks": len(weeks),
        "total_class_days": len(class_days),
        "units": [],
    }

    # Week 1 (5/13-5/15): Tue-Thu only. Orientation + Unit 1.1
    w1 = weeks[0]  # 3 days: Tue 5/13, Wed 5/14, Thu 5/15
    schedule["units"].append({
        "name": "Orientation",
        "week": 1,
        "dates": f"{fmt(w1[0])} - {fmt(w1[0])}",
        "assignments": [
            {"name": "Student Introductions", "due": fmt(w1[1]), "type": "discussion"},
            {"name": "Syllabus Quiz", "due": fmt(w1[1]), "type": "assessment"},
        ],
    })

    schedule["units"].append({
        "name": "Unit 1.1 - Email Etiquette",
        "week": 1,
        "dates": f"{fmt(w1[1])} - {fmt(w1[2])}",
        "assignments": [
            {"name": "Unit 1.1 Email Etiquette Self-Assessment", "due": fmt(w1[2]), "type": "assessment"},
            {"name": "Professional E-mail Etiquette Assignment", "due": fmt(weeks[1][0]), "type": "assignment"},
        ],
    })

    # Week 2 (5/19-5/22): Mon-Thu. Unit 1.2-1.4 + Unit 2.1
    w2 = weeks[1]  # 4 days
    schedule["units"].append({
        "name": "Unit 1.2 - Document Formatting",
        "week": 2,
        "dates": f"{fmt(w2[0])}",
        "assignments": [
            {"name": "Unit 1.2 Document Formatting Self-Assessment", "due": fmt(w2[0]), "type": "assessment"},
        ],
    })

    schedule["units"].append({
        "name": "Unit 1.3-1.4 - Plagiarism & Grammar",
        "week": 2,
        "dates": f"{fmt(w2[1])} - {fmt(w2[2])}",
        "assignments": [
            {"name": "Unit 1.4 Academic Dishonesty Self-Assessment", "due": fmt(w2[2]), "type": "assessment"},
        ],
    })

    schedule["units"].append({
        "name": "Unit 2.1 - Narrative Essay Introduction",
        "week": 2,
        "dates": f"{fmt(w2[2])} - {fmt(w2[3])}",
        "assignments": [
            {"name": "Narrative Essay Making Connections and Predictions", "due": fmt(w2[3]), "type": "discussion"},
            {"name": "Narrative Essay Reading Response", "due": fmt(w2[3]), "type": "discussion"},
        ],
    })

    # Week 3 (5/27-5/29): Unit 2.2-2.3 (Note: 5/26 is Memorial Day)
    w3 = weeks[2]
    schedule["units"].append({
        "name": "Unit 2.2 - Narrative Essay Drafting & Peer Review",
        "week": 3,
        "dates": f"{fmt(w3[0])} - {fmt(w3[1])}",
        "assignments": [
            {"name": "Narration Essay Rough Draft & Peer Review", "due": fmt(w3[1]), "type": "discussion"},
        ],
    })

    schedule["units"].append({
        "name": "Unit 2.3 - Narrative Essay Revision & Final",
        "week": 3,
        "dates": f"{fmt(w3[1])} - {fmt(w3[-1])}",
        "assignments": [
            {"name": "Unit 2.3 Revising and Editing Self-Assessment", "due": fmt(w3[2]) if len(w3) > 2 else fmt(w3[-1]), "type": "assessment"},
            {"name": "Narrative Essay Final Draft", "due": fmt(w3[-1]), "type": "assignment"},
        ],
    })

    # Week 4 (6/2-6/5): Unit 3.1-3.2
    w4 = weeks[3]
    schedule["units"].append({
        "name": "Unit 3.1 - Evaluation Essay Introduction",
        "week": 4,
        "dates": f"{fmt(w4[0])} - {fmt(w4[1])}",
        "assignments": [
            {"name": "Evaluation Essay Making Connections and Predictions", "due": fmt(w4[1]), "type": "discussion"},
            {"name": "Evaluation Essay Reading Response", "due": fmt(w4[1]), "type": "discussion"},
        ],
    })

    schedule["units"].append({
        "name": "Unit 3.2 - Evaluation Essay Drafting & Peer Review",
        "week": 4,
        "dates": f"{fmt(w4[2])} - {fmt(w4[3])}",
        "assignments": [
            {"name": "Unit 3.2 Tone and Coherence Self-Assessment", "due": fmt(w4[2]), "type": "assessment"},
            {"name": "Evaluation Essay Rough Draft and Peer Review", "due": fmt(w4[3]), "type": "discussion"},
        ],
    })

    # Week 5 (6/9-6/12): Unit 3.3 + Unit 4.1-4.2
    w5 = weeks[4]
    schedule["units"].append({
        "name": "Unit 3.3 - Evaluation Essay Final",
        "week": 5,
        "dates": f"{fmt(w5[0])}",
        "assignments": [
            {"name": "Evaluation Essay Final Draft", "due": fmt(w5[1]), "type": "assignment"},
        ],
    })

    schedule["units"].append({
        "name": "Unit 4.1 - Research Essay Introduction",
        "week": 5,
        "dates": f"{fmt(w5[1])} - {fmt(w5[2])}",
        "assignments": [
            {"name": "Problem/Solution Essay: Making Connections and Predictions", "due": fmt(w5[2]), "type": "discussion"},
            {"name": "Problem/Solution Essay: Reading Response", "due": fmt(w5[2]), "type": "discussion"},
        ],
    })

    schedule["units"].append({
        "name": "Unit 4.2 - Research Skills",
        "week": 5,
        "dates": f"{fmt(w5[2])} - {fmt(w5[3])}",
        "assignments": [
            {"name": "Unit 4.2 Research Skills Self-Assessment", "due": fmt(w5[3]), "type": "assessment"},
            {"name": "Integrating Evidence from Research Exercise", "due": fmt(w5[3]), "type": "assignment"},
        ],
    })

    # Week 6 (6/16-6/19 + 6/23): Unit 4.3-4.4
    w6 = weeks[5]
    w6_extra = weeks[6] if len(weeks) > 6 else []

    schedule["units"].append({
        "name": "Unit 4.3 - Research Essay Drafting & Peer Review",
        "week": 6,
        "dates": f"{fmt(w6[0])} - {fmt(w6[2])}",
        "assignments": [
            {"name": "Unit 4.3 MEAL Plan Self-Assessment", "due": fmt(w6[1]), "type": "assessment"},
            {"name": "Problem/Solution Essay: Rough Draft and Peer Review", "due": fmt(w6[2]), "type": "discussion"},
        ],
    })

    final_date = w6_extra[0] if w6_extra else w6[-1]
    schedule["units"].append({
        "name": "Unit 4.4 - Research Essay Final & Course Wrap",
        "week": 6,
        "dates": f"{fmt(w6[3])} - {fmt(final_date)}",
        "assignments": [
            {"name": "Problem/Solution Essay Final Draft", "due": fmt(final_date), "type": "assignment"},
        ],
    })

    return schedule


def render_schedule(schedule: dict) -> str:
    """Render the schedule as readable text."""
    lines: list[str] = []
    lines.append(f"{'=' * 70}")
    lines.append(f"  {schedule['course']} -- {schedule['term']}")
    lines.append(f"  {schedule['dates']}")
    lines.append(f"  {schedule['total_class_days']} class days across {schedule['weeks']} weeks")
    lines.append(f"{'=' * 70}")
    lines.append("")

    for unit in schedule["units"]:
        lines.append(f"  Week {unit['week']}: {unit['name']}")
        lines.append(f"  Dates: {unit['dates']}")
        for a in unit["assignments"]:
            icon = {"discussion": "D", "assessment": "Q", "assignment": "A"}.get(a["type"], "?")
            lines.append(f"    [{icon}] {a['name']:<55} due {a['due']} @ 11:30 PM")
        lines.append("")

    return "\n".join(lines)


def generate_date_mapping(schedule: dict) -> str:
    """Generate a simple placeholder-to-date mapping for the HTML syllabus."""
    lines: list[str] = []
    lines.append("ENC1101 Syllabus Date Placeholders -> Resolved Dates")
    lines.append("=" * 55)
    lines.append("")

    for unit in schedule["units"]:
        lines.append(f"--- {unit['name']} ---")
        for a in unit["assignments"]:
            lines.append(f"  {a['name']}")
            lines.append(f"    xx/xx -> {a['due']}")
            lines.append(f"    x/xx  -> {a['due']}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    schedule = compute_schedule()

    # Print readable schedule
    print(render_schedule(schedule))

    # Print date mapping
    print()
    print(generate_date_mapping(schedule))

    # Write JSON
    from pathlib import Path

    out = Path(__file__).parent / "enc1101_schedule.json"
    out.write_text(json.dumps(schedule, indent=2))
    print(f"\nJSON schedule written to: {out}")


if __name__ == "__main__":
    main()
