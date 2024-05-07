from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

import re

from models import CustomNER
from . import GitHubStatistics


class ResumeRanker:
    """
    Class to calculate the similarity score between a job description and multiple resumes.
    """

    def __init__(self, model_name="bert-base-nli-mean-tokens"):
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
        return sentence_embeddings  # type: ignore

    def calculate_similarity_score(self, sentence_embeddings: list) -> list:
        """
        Calculate the similarity score between the job description and resumes

        Args:
            sentence_embeddings (list): List of sentence embeddings

        Returns:
            list: List of similarity scores
        """
        similarity_scores = cosine_similarity([sentence_embeddings[0]], sentence_embeddings[1:])[0]  # type: ignore
        return [round(float(score) * 100, 2) for score in similarity_scores]

    def get_similarity(self, job_description: str, resumes: list[dict]) -> dict:
        """
        Get the similarity scores between the job description and resumes.

        Args:
            job_description (str): Job description text.
            resumes (list): List of resume texts.

        Returns:
            dict: Dictionary containing similarity scores with resume indices as keys.
        """
        resume_text = [resume["text"] for resume in resumes]
        sentence_embeddings = self.sentence_embedding(job_description, resume_text)
        scores = self.calculate_similarity_score(sentence_embeddings)

        scores = {index + 1: item for index, item in enumerate(scores)}
        scores = {
            k: {
                "match": v,
                "ner": CustomNER().process_text(resume_text[k - 1]),
                "links": resumes[k - 1]["links"],
            }
            for k, v in sorted(scores.items(), key=lambda item: item[1], reverse=True)
        }

        for key, value in scores.items():
            scores[key]["github"] = []
            if "link" in value["ner"]:
                scores[key]["links"] = value["ner"]["link"] + value["links"]

            for link in value["links"]:
                match = re.match(r"https?://(?:www\.)?github\.com/([^/]+)/?", link)
                if match:
                    username = match.group(1)
                    scores[key]["github"].append(username)
        return scores
