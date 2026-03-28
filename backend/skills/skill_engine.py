from sentence_transformers import SentenceTransformer, util
import re

# =====================================================
# LOAD SEMANTIC MODEL (once)
# =====================================================

model = SentenceTransformer("all-MiniLM-L6-v2")


# =====================================================
# TEXT NORMALIZATION
# =====================================================

def normalize_phrase(text: str) -> str:
    """
    Normalize skill phrases for matching
    """
    text = text.lower()
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text.strip()


# =====================================================
# SIMPLE SKILL EXTRACTION (you can improve later)
# =====================================================

def extract_skills(text: str):

    skills = []

    for line in text.split("\n"):
        line = line.strip()
        if 1 < len(line) < 40:
            skills.append(line.lower())

    return list(set(skills))


# =====================================================
# 🔥 HYBRID SKILL MATCHING (BEST VERSION)
# =====================================================

def semantic_skill_match(resume_skills, jd_skills, threshold=0.6):

    matched = []
    missing = []

    if not jd_skills:
        return matched, missing, 0.0

    jd_embeddings = model.encode(jd_skills, convert_to_tensor=True)

    for jd_skill, jd_emb in zip(jd_skills, jd_embeddings):

        jd_norm = normalize_phrase(jd_skill)

        found = False
        best_score = 0

        for r_skill in resume_skills:

            r_norm = normalize_phrase(r_skill)

            # =================================================
            # 1️⃣ EXACT MATCH
            # =================================================
            if jd_norm == r_norm:
                found = True
                break

            # =================================================
            # 2️⃣ SUBSTRING MATCH
            # =================================================
            if jd_norm in r_norm or r_norm in jd_norm:
                found = True
                break

            # =================================================
            # 3️⃣ SEMANTIC MATCH
            # =================================================
            r_emb = model.encode(r_skill, convert_to_tensor=True)
            score = util.cos_sim(r_emb, jd_emb).item()

            best_score = max(best_score, score)

        if found or best_score >= threshold:
            matched.append(jd_skill)
        else:
            missing.append(jd_skill)

    match_percent = (len(matched) / len(jd_skills)) * 100

    return matched, missing, round(match_percent, 2)
