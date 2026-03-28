from sentence_transformers import SentenceTransformer, util

# Use lightweight model (already downloaded in your project)
model = SentenceTransformer("all-MiniLM-L6-v2")


def semantic_skill_match(resume_text, jd_skills, threshold=0.5):
    """
    Semantic matching between JD skills and resume text
    """

    resume_text = resume_text.lower()

    # Encode resume once
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)

    matched = []
    missing = []

    for skill in jd_skills:

        skill_embedding = model.encode(skill, convert_to_tensor=True)

        similarity = util.cos_sim(skill_embedding, resume_embedding).item()

        if similarity >= threshold:
            matched.append(skill)
        else:
            missing.append(skill)

    skill_match_score = (
        len(matched) / len(jd_skills) * 100
        if jd_skills else 0
    )

    return matched, missing, skill_match_score
