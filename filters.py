"""
filters.py
Shared logic for deciding whether a posting looks entry-level.
"""

ENTRY_KEYWORDS = ["entry level", "entry-level", "junior", "graduate", "new grad", "intern", "associate", "trainee"]
SENIOR_KEYWORDS = ["senior", "sr.", "lead", "principal", "staff", "manager", "head of", "director", "architect"]


def is_entry_level(title, description=""):
    text = f"{title} {description}".lower()

    if any(word in text for word in SENIOR_KEYWORDS):
        return False

    if any(word in text for word in ENTRY_KEYWORDS):
        return True

    # No explicit senior markers and no explicit entry markers -> treat as unclear/ok to include
    return True
