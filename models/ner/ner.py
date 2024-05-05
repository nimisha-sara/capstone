import spacy

class CustomNER:
    """
    Class for custom Named Entity Recognition (NER) using SpaCy.
    """

    def __init__(self):
        self.model_path = './models/ner/model-best'
        self.nlp = spacy.load(self.model_path)

    def process_text(self, text: str) -> dict:
        """
        Process the input text with the custom NER model and extract entities

        Args:
            text (str): Input text to be processed

        Returns:
            dict: A dictionary containing recognized entities and their labels
        """
        doc = self.nlp(text)
        entities = {}
        for ent in doc.ents:
            entities[ent.text] = ent.label_
        entities = {
            key.lower(): [k.title() for k, v in entities[0].items() if v == key]
            for key in set(entities[0].values())
        }
        return entities
