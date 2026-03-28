import numpy as np


# =========================================================
# RESEARCH + INDUSTRY LEVEL FAIR HIRING MODEL
# =========================================================
def hiring_probability(
    semantic,
    skill_match,
    experience,
    ats
):
    """
    Advanced fairness-aware hiring score.

    Inputs:
        semantic, skill_match, ats : 0–100
        experience : years

    Output:
        Fair probability score (0–100)
    """

    # =====================================================
    # 1️⃣ Normalize experience
    # =====================================================
    exp_norm = min(experience / 10, 1.0) * 100


    # =====================================================
    # 2️⃣ Base performance score (balanced weights)
    # =====================================================
    weights = {
        "semantic": 0.30,
        "skills": 0.30,
        "experience": 0.20,
        "ats": 0.20
    }

    base_score = (
        weights["semantic"] * semantic +
        weights["skills"] * skill_match +
        weights["experience"] * exp_norm +
        weights["ats"] * ats
    )


    # =====================================================
    # 3️⃣ Imbalance penalty
    # Penalizes one-dimensional candidates
    # =====================================================
    factors = np.array([semantic, skill_match, exp_norm, ats])

    variance = np.var(factors)

    imbalance_penalty = min(variance / 180, 18)


    # =====================================================
    # 4️⃣ Risk penalty (weak factors detection)
    # Penalize if ANY critical dimension is very low
    # =====================================================
    weak_count = np.sum(factors < 30)

    risk_penalty = weak_count * 2.5


    # =====================================================
    # 5️⃣ Consistency bonus
    # Reward well-rounded profiles
    # =====================================================
    std_dev = np.std(factors)

    consistency_bonus = max(0, (20 - std_dev) * 0.3)


    # =====================================================
    # 6️⃣ Combine fairness adjustments
    # =====================================================
    fair_score = (
        base_score
        - imbalance_penalty
        - risk_penalty
        + consistency_bonus
    )


    # =====================================================
    # 7️⃣ Saturation control
    # Prevent extreme scores dominating rankings
    # =====================================================
    if fair_score > 85:
        fair_score = 85 + (fair_score - 85) * 0.25


    # =====================================================
    # 8️⃣ Clamp to valid range
    # =====================================================
    fair_score = max(0, min(100, fair_score))


    return round(fair_score, 2)
