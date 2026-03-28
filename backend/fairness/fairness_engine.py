import numpy as np


# =========================================================
# 1️⃣ BIAS DETECTION
# =========================================================
def detect_bias(scores):
    """
    Detect unfair score distribution.
    Returns fairness indicators.
    """

    if not scores:
        return {"bias_detected": False}

    scores = np.array(scores)

    mean = float(np.mean(scores))
    std = float(np.std(scores))

    # Outlier detection
    high_outliers = np.sum(scores > mean + 2 * std)
    low_outliers = np.sum(scores < mean - 2 * std)

    bias_flag = high_outliers > 0 or low_outliers > 0

    return {
        "mean_score": round(mean, 2),
        "std_dev": round(std, 2),
        "high_outliers": int(high_outliers),
        "low_outliers": int(low_outliers),
        "bias_detected": bool(bias_flag)
    }


# =========================================================
# 2️⃣ FAIRNESS ADJUSTMENT
# =========================================================
def fairness_adjust_scores(scores):
    """
    Reduce extreme advantage/disadvantage.
    """

    if not scores:
        return scores

    scores = np.array(scores)

    mean = np.mean(scores)

    # Pull extreme scores toward mean
    adjusted = 0.8 * scores + 0.2 * mean

    return adjusted.tolist()


# =========================================================
# 3️⃣ EXPLAINABILITY
# =========================================================
def generate_explanation(candidate):
    """
    Explain why candidate received score.
    """

    explanation = []

    if candidate["semantic_match"] < 50:
        explanation.append("Low semantic similarity to job description")

    if candidate["skill_match"] < 50:
        explanation.append("Insufficient matching skills")

    if candidate["experience_years"] < 2:
        explanation.append("Limited experience")

    if candidate["ats_score"] < 50:
        explanation.append("Resume structure may not be ATS-friendly")

    if not explanation:
        explanation.append("Strong overall profile")

    return explanation


# =========================================================
# 4️⃣ CONFIDENCE SCORE
# =========================================================
def compute_confidence(candidate):
    """
    Confidence in decision (based on data completeness)
    """

    factors = [
        candidate["semantic_match"],
        candidate["skill_match"],
        candidate["ats_score"]
    ]

    return round(np.mean(factors), 2)


# =========================================================
# 5️⃣ AUDIT LOG ENTRY
# =========================================================
def create_audit_entry(candidate):
    return {
        "candidate": candidate["filename"],
        "score": candidate["hiring_probability"],
        "decision": "Shortlisted"
        if candidate["hiring_probability"] > 60
        else "Rejected"
    }
# =========================================================
# 6️⃣ ADVANCED EXPLANATION ENGINE
# =========================================================
def generate_detailed_explanation(candidate):
    """
    Generate human-readable explanation of decision.
    """

    strengths = []
    weaknesses = []

    # =========================
    # Semantic match
    # =========================
    if candidate["semantic_match"] >= 70:
        strengths.append("Strong alignment with job description")
    elif candidate["semantic_match"] >= 40:
        strengths.append("Moderate relevance to job role")
    else:
        weaknesses.append("Low relevance to job description")

    # =========================
    # Skills
    # =========================
    if candidate["skill_match"] >= 70:
        strengths.append("Most required skills are present")
    elif candidate["skill_match"] >= 40:
        strengths.append("Some required skills are present")
    else:
        weaknesses.append("Few required skills matched")

    # =========================
    # Experience
    # =========================
    if candidate["experience_years"] >= 8:
        strengths.append("Extensive professional experience")
    elif candidate["experience_years"] >= 3:
        strengths.append("Relevant work experience")
    else:
        weaknesses.append("Limited professional experience")

    # =========================
    # ATS score
    # =========================
    if candidate["ats_score"] >= 80:
        strengths.append("Well-structured ATS-friendly resume")
    elif candidate["ats_score"] < 50:
        weaknesses.append("Resume structure may reduce visibility in ATS")

    # =========================
    # Overall assessment
    # =========================
    score = candidate["fairness_adjusted_score"]

    if score >= 75:
        assessment = "Excellent candidate"
    elif score >= 55:
        assessment = "Strong candidate"
    elif score >= 40:
        assessment = "Moderate candidate"
    else:
        assessment = "Weak candidate"

    # =========================
    # Recommendation
    # =========================
    if score >= 60:
        recommendation = "Recommended for interview"
    elif score >= 40:
        recommendation = "Consider for further review"
    else:
        recommendation = "Not recommended"

    return {
        "overall_assessment": assessment,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendation": recommendation
    }

