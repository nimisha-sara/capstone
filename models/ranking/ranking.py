from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def sentence_embedding(job_description: str, resumes: list[str]):
    model = SentenceTransformer('bert-base-nli-mean-tokens')

    sentences = [job_description].extend(resumes)
    sentence_embeddings = model.encode(sentences)
    return sentence_embeddings


def calculate_similarity_score(sentence_embeddings: list):
    # The result will be a list of similarity scores between the first sentence and each of the other sentences
    similarity_scores = cosine_similarity([sentence_embeddings[0]], sentence_embeddings[1:])
    return [round(float(score) * 100, 2) for score in similarity_scores]


def get_similarity(job_description: str, resumes: list[str]):
    sentence_embeddings = sentence_embedding(job_description, resumes)
    return calculate_similarity_score(sentence_embeddings)