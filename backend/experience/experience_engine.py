import re


def extract_experience(text):

    matches = re.findall(r'(\d+)\s+years?', text.lower())

    return max([int(x) for x in matches], default=0)
