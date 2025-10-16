"""
Module 2: Goal-Based Planning Engine

- Implements a heuristic, explainable allocation algorithm.
- Sorts goals by priority and urgency, allocates monthly savings.
- Outputs allocation dict and reason tags for XAI.
- Addresses research gap: Dynamic, holistic, goal-oriented planning.
"""

def plan_allocations(goals_df, monthly_savings):
    """
    Heuristic allocation:
    - Sort by priority (desc), then months_left (asc).
    - Allocate up to required_monthly for each goal, until savings depleted.
    - Tag reasons for each allocation.
    Returns:
        allocations: {goal_name: allocation_amount}
        reason_tags: [{goal, tag, allocate, months_left}]
    """
    df = goals_df.copy()
    df = df.sort_values(by=["priority", "months_left"], ascending=[False, True])
    savings_left = monthly_savings
    allocations = {}
    reason_tags = []

    for idx, row in df.iterrows():
        if savings_left <= 0:
            allocations[row["name"]] = 0.0
            continue
        req = row["required_monthly"]
        alloc = min(savings_left, max(0, req))
        allocations[row["name"]] = alloc
        savings_left -= alloc

        # Tagging logic for XAI
        tag = []
        if row["priority"] >= 4:
            tag.append("HIGH_PRIORITY")
        if row["months_left"] <= 3:
            tag.append("DEADLINE_APPROACHING")
        if alloc >= req and req > 0:
            tag.append("ON_TRACK")
        if alloc < req and req > 0:
            tag.append("UNDERFUNDED")
        if req == 0:
            tag.append("GOAL_COMPLETE")
        reason_tags.append({
            "goal": row["name"],
            "tag": "_".join(tag) if tag else "STANDARD",
            "allocate": alloc,
            "months_left": int(row["months_left"])
        })

    return allocations, reason_tags