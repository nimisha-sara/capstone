import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
import language_tool_python

# from spellchecker import SpellChecker

nltk.download("averaged_perceptron_tagger")
nltk.download("punkt")


class ResumeChecker:
    def __init__(self):
        self.tool = language_tool_python.LanguageTool("en-US")

        self.strong_action_verbs = [
            "Accelerated",
            "Achieved",
            "Attained",
            "Completed",
            "Conceived",
            "Convinced",
            "Discovered",
            "Doubled",
            "Effected",
            "Eliminated",
            "Expanded",
            "Expedited",
            "Founded",
            "Improved",
            "Increased",
            "Initiated",
            "Innovated",
            "Introduced",
            "Invented",
            "Launched",
            "Mastered",
            "Overcame",
            "Overhauled",
            "Pioneered",
            "Reduced",
            "Resolved",
            "Revitalized",
            "Spearheaded",
            "Strengthened",
            "Transformed",
            "Upgraded",
            "Tripled",
            "Oversaw",
            "Lead",
            "Implemented",
            "Negotiated",
            "Transformed",
            "Engineered",
            "Achieved",
            "Forecasted",
            "Administered",
            "Analyzed",
            "Generated",
            "Devised",
            "Cultivated",
            "Coached",
            "Trained",
            "Guided",
            "Directed",
            "Converted",
            "Created",
            "Designed",
            "Outlined",
            "Established",
            "Built",
            "Constructed",
            "Collaborated",
            "Gathered",
            "Performed",
            "Executed",
            "Delivered",
            "Improved",
        ]

        self.personal_pronouns = [
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
            "my",
            "your",
            "his",
            "her",
            "its",
            "our",
            "their",
            "mine",
            "yours",
            "hers",
            "ours",
            "theirs",
        ]

    def grammar_check(self, text: str) -> list:
        """
        Check grammar in the text

        Args:
            text (str): Text to perform grammar check on.

        Returns:
            list: List of detected grammatical errors.
        """
        matches = self.tool.check(text)
        errors = []
        for match in matches:
            match = list(match)
            if (
                match[0] != "MORFOLOGIK_RULE_EN_US"
                and "whitespace" not in match[1]
                and "consecutive spaces" not in match[1]
            ):
                if "Did you mean" in match[1]:
                    if '"' in match[1].split("Did you mean")[-1]:
                        message = match[1].split("Did you mean")[0]
                else:
                    message = match[1]
                errors.append(
                    {
                        "message": message,
                        "suggestions": match[2][:5],
                        "error_start": match[3],
                        "error_end": match[3] + match[6],
                        "text": match[4],
                    }
                )
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
            if pos.startswith("VB"):
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
                if tagged_words[i][1] == "VBN" and tagged_words[i + 1][0] == "by":
                    passive_sentences.append(sentence)
                    break
        return passive_sentences

    def check_digital_footprint_links(self, text: str) -> dict:
        """
        Check for digital footprint links in the text.

        Args:
            text (str): Text to check for digital footprint links.

        Returns:
            dict: Dictionary with platform name as key and link as value.
        """
        platforms = [
            "linkedin",
            "github",
            "medium",
            "stackoverflow",
            "codechef",
            "codeforces",
            "dribble",
            "hackerrank",
        ]
        platform_links = {}
        for platform in platforms:
            pattern = rf"\b(?:https?://)?(?:www\.)?{platform}\.com/\S*"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                platform_links[platform] = match.group(0)
        return platform_links

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
        if re.search(r"\bReferences\b|\bReferees\b", text, re.IGNORECASE):
            return True
        return False

    def perform_all_checks(self, text: str) -> dict:
        """
        Perform all checks on the given text.

        Args:
            text (str): Text to perform checks on.

        Returns:
            dict: Dictionary containing the results of all checks.
        """
        return {
            "grammar": self.grammar_check(text),
            "action_verbs": self.check_action_verbs(text),
            "passive_language": self.check_passive_language(text),
            "footprint_links": self.check_digital_footprint_links(text),
            "personal_pronouns": self.check_personal_pronouns(text),
            "references_section": self.check_references_section(text),
        }
