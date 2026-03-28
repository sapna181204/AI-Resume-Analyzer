import numpy as np


# =========================================================
# DATASET-LEVEL FAIRNESS NORMALIZATION
# =========================================================

def normalize_scores(scores):
    """
    Normalize scores relative to batch distribution.
    Prevents skew from unusually strong or weak candidates.
    """

    if not scores:
        return scores

    arr = np.array(scores)

    mean = np.mean(arr)
    std = np.std(arr)

    if std == 0:
        return scores

    normalized = 50 + (arr - mean) / std * 15
    normalized = np.clip(normalized, 0, 100)

    return normalized.tolist()


# =========================================================
# OUTLIER SMOOTHING
# =========================================================

def smooth_extremes(scores):
    """
    Compress extreme values to prevent dominance.
    """

    arr = np.array(scores)

    q1 = np.percentile(arr, 25)
    q3 = np.percentile(arr, 75)
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    arr = np.clip(arr, lower, upper)

    return arr.tolist()


# =========================================================
# FINAL DATASET FAIR ADJUSTMENT
# =========================================================

def dataset_fair_adjustment(scores):
    scores = smooth_extremes(scores)
    scores = normalize_scores(scores)
    return scores