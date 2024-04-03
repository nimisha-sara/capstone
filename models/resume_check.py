import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
import language_tool_python


nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')


class ResumeChecker:
    def __init__(self):
        self.tool = language_tool_python.LanguageTool('en-US')

        self.strong_action_verbs = [
            "Accelerated", "Achieved", "Attained", "Completed", "Conceived", "Convinced", "Discovered",
            "Doubled", "Effected", "Eliminated", "Expanded", "Expedited", "Founded", "Improved",
            "Increased", "Initiated", "Innovated", "Introduced", "Invented", "Launched", "Mastered",
            "Overcame", "Overhauled", "Pioneered", "Reduced", "Resolved", "Revitalized", "Spearheaded",
            "Strengthened", "Transformed", "Upgraded", "Tripled", "Oversaw", "Lead", "Implemented",
            "Negotiated", "Transformed", "Engineered", "Achieved", "Forecasted", "Administered",
            "Analyzed", "Generated", "Devised", "Cultivated", "Coached", "Trained", "Guided",
            "Directed", "Converted", "Created", "Designed", "Outlined", "Established", "Built",
            "Constructed", "Collaborated", "Gathered", "Performed", "Executed", "Delivered", "Improved"
        ]

        self.personal_pronouns = [
            "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",
            "my", "your", "his", "her", "its", "our", "their", "mine", "yours", "hers", "ours", "theirs"
        ]

    def grammar_check(self, text: str) -> list:
        """
        Check grammar and spelling in the text

        Args:
            text (str): Text to perform grammar and spelling check on.

        Returns:
            list: List of detected grammar and spelling errors.
        """
        matches = self.tool.check(text)
        errors = [match.msg for match in matches]
        return errors

    def check_action_verbs(self, text: str) -> dict:
        """
        Check for action verbs in the text.

        Args:
            text (str): Text to check for action verbs.

        Returns:
            dict: Dictionary containing all action verbs found in the text and all strong action verbs.
        """
        verbs = []
        tagged_words = pos_tag(word_tokenize(text))
        for word, pos in tagged_words:
            if pos.startswith('VB'):
                verbs.append(word)
        strong_verbs = [verb for verb in verbs if verb in self.strong_action_verbs]
        return {"verbs": verbs, "strong_verbs": strong_verbs}

    def check_passive_language(self, text: str) -> list:
        """
        Check for passive language in the text

        Args:
            text (str): Text to check for passive language.

        Returns:
            list: List of sentences containing passive language.
        """
        sentences = sent_tokenize(text)
        passive_sentences = []
        for sentence in sentences:
            tagged_words = pos_tag(word_tokenize(sentence))
            for i in range(len(tagged_words) - 1):
                if tagged_words[i][1] == 'VBN' and tagged_words[i+1][0] == 'by':
                    passive_sentences.append(sentence)
                    break
        return passive_sentences

    def check_digital_footprint_links(self, text: str) -> list:
        """
        Check for digital footprint links in the text.

        Args:
            text (str): Text to check for digital footprint links.

        Returns:
            list: List of digital footprint links found in the text.
        """
        platforms = ["linkedin", "github", "medium", "stackoverflow", "codechef", "codeforces"]
        pattern = "|".join(platforms)
        urls = re.findall(r'\b(?:https?://)?(?:www\.)?\w+\.(?:com|net|org|io)/?\S*\b', text)
        footprint_links = [url for url in urls if re.search(pattern, url, re.IGNORECASE)]
        return footprint_links

    def check_unprofessional_email(self, email: str) -> bool:
        """
        Check for unprofessional email ID patterns.

        Args:
            email (str): Email ID to check.

        Returns:
            bool: True if the email is unprofessional, False otherwise.
        """
        unprofessional_patterns = ["partygirl", "studmuffin", "cuteguy", "hotbabe", "lovesex", "420", "69"]
        pattern = "|".join(unprofessional_patterns)
        if re.search(pattern, email, re.IGNORECASE):
            return True
        return False

    def check_personal_pronouns(self, text: str) -> list:
        """
        Check for personal pronouns in the text.

        Args:
            text (str): Text to check for personal pronouns.

        Returns:
            list: List of personal pronouns found in the text.
        """
        words = word_tokenize(text.lower())
        pronouns = [word for word in words if word in self.personal_pronouns]
        return pronouns

    def check_references_section(self, text: str) -> bool:
        """
        Check for the presence of a references section in the text.

        Args:
            text (str): Text to check for the references section.

        Returns:
            bool: True if a references section is found, False otherwise.
        """
        if re.search(r'\bReferences\b|\bReferees\b', text, re.IGNORECASE):
            return True
        return False


# Example usage:
if __name__ == "__main__":
    checker = ResumeChecker()

    sample_text = """
    The cake was eaten by John. The report will be submitted tomorrow.
    """
    print("Passive Language:", checker.check_passive_language(sample_text))

    sample_text = """
    John implemented a new software system. Mary developed a marketing strategy. The team managed the project effectively.
    """
    all_verbs, strong_verbs = checker.check_action_verbs(sample_text)
    print("Action Verbs:", all_verbs)
    print("Strong Action Verbs:", strong_verbs)

    sample_text = """
    John's LinkedIn profile: https://www.linkedin.com/in/john-doe. GitHub: https://github.com/johndoe.
    """
    print("Digital Footprint Links:", checker.check_digital_footprint_links(sample_text))

    print("Unprofessional Email Check:", checker.check_unprofessional_email("hotbabe123@gmail.com"))

    sample_text = """
    I am writing my resume. You should proofread it. He has experience in software development.
    She is a skilled project manager. They are seeking new opportunities.
    """
    print("Personal Pronouns:", checker.check_personal_pronouns(sample_text))

    sample_text = """
    References:
    1. XYZ person
    2. Abc Person
    """
    print("References Section Check:", checker.check_references_section(sample_text))
