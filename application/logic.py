"""
TIER 2: APPLICATION LAYER — BUSINESS LOGIC
============================================================
No Flask, no SQL. Just the rules for turning raw vote counts
into something meaningful - the same discipline as the grade
calculator app, applied to a different domain.
============================================================
"""


def validate_poll_input(question, options):
    """Basic logic: input validation with multiple conditions."""
    if not question or not question.strip():
        return "'question' is required"
    if not options or len(options) < 2:
        return "a poll needs at least 2 options"
    if any(not (o or "").strip() for o in options):
        return "options cannot be empty"
    if len(options) > 8:
        return "a poll can have at most 8 options"
    return None


def compute_results(options):
    """
    Basic logic: turn raw vote counts into percentages, and figure out
    which option (if any) is currently leading. This is exactly the kind
    of small, testable calculation that belongs in the Application tier,
    not scattered across SQL queries or frontend JavaScript.
    """
    total_votes = sum(o["votes"] for o in options)
    leading_id = None
    if total_votes > 0:
        leading_id = max(options, key=lambda o: o["votes"])["id"]

    results = []
    for o in options:
        pct = round((o["votes"] / total_votes) * 100, 1) if total_votes > 0 else 0.0
        results.append({
            "id": o["id"],
            "option_text": o["option_text"],
            "votes": o["votes"],
            "percentage": pct,
            "is_leading": o["id"] == leading_id and total_votes > 0,
        })
    return {"options": results, "total_votes": total_votes}
