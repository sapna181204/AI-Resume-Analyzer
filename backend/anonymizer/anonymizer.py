import re
import spacy

nlp = spacy.load("en_core_web_sm")


def anonymize(text):

    # Emails
    text = re.sub(r'\S+@\S+', 'EMAIL', text)

    # Phone numbers
    text = re.sub(r'\+?\d[\d\s\-]{8,15}', 'PHONE', text)

    # Links
    text = re.sub(r'http\S+|www\S+', 'LINK', text)

    # Named Entity Removal
    doc = nlp(text)
    tokens = []

    for t in doc:
        if t.ent_type_ in ["PERSON"]:
            tokens.append("NAME")
        elif t.ent_type_ in ["ORG"]:
            tokens.append("ORG")
        elif t.ent_type_ in ["GPE", "LOC"]:
            tokens.append("LOCATION")
        else:
            tokens.append(t.text)

    return " ".join(tokens)
