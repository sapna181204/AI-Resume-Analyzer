import re


def normalize_text(text: str) -> str:
    """
    Normalize resume text for robust skill matching
    """

    text = text.lower()

    # Replace hyphens with spaces
    text = re.sub(r"[-–—]", " ", text)

    # Replace hyphens and slashes with space
    text = re.sub(r"[-_/]", " ", text)

    # Remove punctuation
    text = re.sub(r"[^\w\s]", " ", text)

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_skill(skill: str) -> str:
    """
    Normalize skill phrase
    """

    skill = skill.lower()

    skill = re.sub(r"[-–—]", " ", skill)
    skill = re.sub(r"[^\w\s]", " ", skill)
    skill = re.sub(r"\s+", " ", skill)
    skill = re.sub(r"[^a-z0-9]", "", skill)

    return skill.strip()






