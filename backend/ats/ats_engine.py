import re


def ats_score(text):

    score = 0
    checks = 6
    t = text.lower()

    if "education" in t: score += 1
    if "experience" in t: score += 1
    if "skills" in t: score += 1
    if "projects" in t: score += 1

    if re.search(r'\S+@\S+', text): score += 1
    if re.search(r'\+?\d[\d\s\-]{8,15}', text): score += 1

    return round((score / checks) * 100, 2)
