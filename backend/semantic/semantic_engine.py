from sentence_transformers import SentenceTransformer, util
import nltk

model = SentenceTransformer("all-MiniLM-L6-v2")


def semantic_match(resume_text, jd_text):

    if not resume_text:
        return 0.0
    
    if not jd_text.strip():
        return 0.0
    
    sentences = nltk.sent_tokenize(resume_text)

    if not sentences:
        return 0.0

    # 🔥 Encode ALL sentences at once (major speed improvement)
    sentence_embeddings = model.encode(
        sentences,
        convert_to_tensor=True,
        batch_size=32
    )

    # Encode JD once
    jd_embedding = model.encode(
        jd_text,
        convert_to_tensor=True
    )

    # Compute cosine similarities
    scores = util.cos_sim(sentence_embeddings, jd_embedding).squeeze()

    # Convert tensor → python list
    scores = scores.tolist()

    # Take top 5 matches
    top_scores = sorted(scores, reverse=True)[:5]

    final = sum(top_scores) / len(top_scores)

    return round(final * 100, 2)
