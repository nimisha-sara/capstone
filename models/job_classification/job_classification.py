import pickle


class JobClassifier:
    """
    Class to classify job roles using a pre-trained model.
    """

    def __init__(self):
        self.model_file = "./models/job_classification/job_role_model.pkl"
        self.label_mapping = {
            6: "Data Science", 14: "HR", 0: "Advocate", 1: "Arts",
            33: "Web Designing", 19: "Mechanical Engineer", 28: "Sales",
            16: "Health and fitness", 5: "Civil Engineer", 17: "Java Developer",
            4: "Business Analyst", 27: "SAP Developer", 2: "Automation Testing",
            12: "Electrical Engineering", 22: "Operations Manager", 25: "Python Developer",
            9: "DevOps Engineer", 20: "Network Security Engineer", 23: "PMO",
            7: "Database", 15: "Hadoop", 11: "ETL Developer", 10: "DotNet Developer",
            3: "Blockchain", 32: "Testing", 26: "Python_Developer", 18: "Java_Developer",
            13: "Front_End_Developer", 21: "Network_Administrator", 24: "Project_manager",
            29: "Security_Analyst", 30: "Software_Developer", 31: "Systems_Administrator",
            34: "Web_Developer", 8: "Database_Administrator",
        }
        self.loaded_model, self.loaded_vectorizer = self._load_model()

    def _load_model(self):
        """
        Load the model and vectorizer from the pickle file

        Returns:
            tuple: Tuple containing the loaded model and vectorizer
        """
        with open(self.model_file, "rb") as f:
            loaded_model, loaded_vectorizer = pickle.load(f)
        return loaded_model, loaded_vectorizer

    def predict_job_role(self, text: str) -> str:
        """
        Predict the job role category for the given text

        Args:
            text (str): Input text to classify

        Returns:
            str: Predicted job role category
        """
        vectorized_text = self.loaded_vectorizer.transform([text])
        prediction = self.loaded_model.predict(vectorized_text)
        return self.label_mapping[prediction[0]]


if __name__ == "__main__":
    # Define the path to the model pickle file

    # Create an instance of JobClassifier
    classifier = JobClassifier()

    # Example text for prediction
    new_text = "Python Developer ksjdljqlwdjladjl"

    # Make prediction
    predicted_job_role = classifier.predict_job_role(new_text)
    print("Predicted job role:", predicted_job_role)
