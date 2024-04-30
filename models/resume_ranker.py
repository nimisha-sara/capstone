from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from ner.ner import CustomNER


class ResumeRanker:
    """
    Class to calculate the similarity score between a job description and multiple resumes.
    """

    def __init__(self, model_name='bert-base-nli-mean-tokens'):
        """
        Initialize the ResumeSimilarityChecker with a pre-trained SentenceTransformer model.

        Args:
        model_name (str): Name of the SentenceTransformer model to be used. Defaults to 'bert-base-nli-mean-tokens'.
        """
        self.model = SentenceTransformer(model_name)

    def sentence_embedding(self, job_description: str, resumes: list[str]) -> list:
        """
        Generate sentence embeddings for the job description and resumes

        Args:
            job_description (str): Job description text
            resumes (list): List of resume texts

        Returns:
            list: List of sentence embeddings.
        """
        sentences = [job_description] + resumes
        sentence_embeddings = self.model.encode(sentences)
        return sentence_embeddings # type: ignore

    def calculate_similarity_score(self, sentence_embeddings: list) -> list:
        """
        Calculate the similarity score between the job description and resumes

        Args:
            sentence_embeddings (list): List of sentence embeddings

        Returns:
            list: List of similarity scores
        """
        similarity_scores = cosine_similarity([sentence_embeddings[0]], sentence_embeddings[1:])[0] # type: ignore
        return [round(float(score) * 100, 2) for score in similarity_scores]

    def get_similarity(self, job_description: str, resumes: list[str]) -> dict:
        """
        Get the similarity scores between the job description and resumes.

        Args:
            job_description (str): Job description text.
            resumes (list): List of resume texts.

        Returns:
            dict: Dictionary containing similarity scores with resume indices as keys.
        """
        sentence_embeddings = self.sentence_embedding(job_description, resumes)
        scores = self.calculate_similarity_score(sentence_embeddings)

        scores = {index + 1: item for index, item in enumerate(scores)}
        scores = {k: {"match": v, "ner": resumes[k - 1]} for k, v in sorted(scores.items(),
                                          key=lambda item: item[1], reverse=True)}
        return scores
