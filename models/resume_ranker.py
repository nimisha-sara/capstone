from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


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
        return sentence_embeddings

    def calculate_similarity_score(self, sentence_embeddings: list) -> list:
        """
        Calculate the similarity score between the job description and resumes

        Args:
            sentence_embeddings (list): List of sentence embeddings

        Returns:
            list: List of similarity scores
        """
        similarity_scores = cosine_similarity([sentence_embeddings[0]], sentence_embeddings[1:])[0]
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
        scores = {k: v for k, v in sorted(scores.items(), key=lambda item: item[1])}
        return scores


# Example usage:
if __name__ == "__main__":
    checker = ResumeRanker()
    job_description = "Software Engineer with experience in Python and machine learning."
    resumes = ["Experienced software developer with expertise in Python and Java.",
               "Data scientist skilled in machine learning algorithms and data analysis."]

    similarity_scores = checker.get_similarity(job_description, resumes)
    print("Similarity Scores:", similarity_scores)

