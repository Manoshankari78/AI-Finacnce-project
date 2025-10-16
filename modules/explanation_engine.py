"""
Module 3: Explanation Engine

- Maps reason tags to natural-language templates for XAI.
- Generates explanations for each goal allocation.
- Addresses research gap: Transparency and user trust via explainability.
"""

TEMPLATES = {
    "HIGH_PRIORITY": "I'm prioritizing {goal} because it's high-priority.",
    "DEADLINE_APPROACHING": "The deadline for {goal} is approaching soon.",
    "HIGH_PRIORITY_DEADLINE_APPROACHING": "I'm prioritizing {goal} because it's high-priority and the deadline is near.",
    "ON_TRACK": "This goal is on track with the current allocation.",
    "UNDERFUNDED": "This goal is underfunded this month due to limited savings.",
    "GOAL_COMPLETE": "{goal} is already fully funded.",
    "STANDARD": "Allocating to {goal} as per your plan."
}

def explain_allocations(reason_tags):
    """
    For each goal, generate a natural-language explanation based on tags.
    Returns: {goal_name: explanation_str}
    """
    explanations = {}
    for tag_info in reason_tags:
        goal = tag_info["goal"]
        tag = tag_info["tag"]
        alloc = tag_info["allocate"]
        months_left = tag_info["months_left"]

        # Pick template (combine if multiple tags)
        template = TEMPLATES.get(tag, TEMPLATES["STANDARD"])
        explanation = template.format(goal=goal)
        if alloc > 0:
            explanation += f" Allocating ${alloc:.2f} ({months_left} months left)."
        elif "GOAL_COMPLETE" in tag:
            explanation += " No allocation needed."
        explanations[goal] = explanation
    return explanations