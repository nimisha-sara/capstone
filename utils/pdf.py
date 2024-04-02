import re
import fitz
from tqdm import tqdm


class PDF:
    """
    Class to read and process PDF files.

    Args:
        file_paths (list): List of file paths of PDF files.
    """

    def __init__(self, file_paths: list):
        self.file_paths = file_paths
        self.output_text = []

    def read_pdf(self, file: str) -> str:
        """
        Read text from a PDF file.

        Args:
            file (str): Path to the PDF file.

        Returns:
            str: Text extracted from the PDF.
        """
        file_text = ""

        with fitz.open(file) as doc:
            for page in doc:
                text = page.get_text()
                file_text += text
        return self.clean_text(file_text)

    def clean_text(self, text: str) -> str:
        """
        Clean the extracted text from a PDF.

        Args:
            text (str): Text extracted from the PDF.

        Returns:
            str: Cleaned text.
        """
        lines = text.split("\n")
        non_empty_lines = "\n".join(filter(lambda line: line.strip() != "", lines))
        for char in ["(", ")", ",", "[", ";", "|"]:
            non_empty_lines = non_empty_lines.replace(char, " ")
        non_empty_lines = non_empty_lines.replace("  ", " ")
        return self.handle_unicode(non_empty_lines)

    def get_hyperlinks(self, pdf_file: str) -> list:
        """
        Get hyperlinks from a PDF file

        Args:
            pdf_file (str): Path to the PDF file

        Returns:
            list: List of hyperlinks found in the PDF
        """
        pdf_document = fitz.open(pdf_file)
        hyperlinks = []

        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            annotations = page.links()

            for annotation in annotations:
                hyperlink = annotation.get("uri")
                if hyperlink:
                    hyperlinks.append(hyperlink)

        pdf_document.close()
        return hyperlinks

    def handle_unicode(self, text: str) -> str:
        """
        Replace Unicode characters with their respective symbols.

        Args:
            text (str): Text to process.

        Returns:
            str: Processed text with Unicode characters replaced.
        """
        replacements = {
            "\u2013": "-", "\u2014": "--", "\u2026": "...", "\u2018": "'", "\u2019": "'",
            "\u201C": '"', "\u201D": '"', "\u00A0": " ", "\u201a": ",", "\u201e": '"',
            "\u2022": "-", "\u2013": "-", "\u2014": "--", "\u2015": "--", "\u2212": "-"
        }

        pattern = re.compile("|".join(re.escape(key) for key in replacements.keys()))
        processed_text = pattern.sub(lambda match: replacements[match.group(0)], text)
        return processed_text

    def process_pdf(self):
        """
        Process PDF files.

        Returns:
            list: List containing dictionaries with status, text, and links for each processed PDF.
        """
        for file in tqdm(self.file_paths):
            if file.split(".")[-1] == "pdf":
                try:
                    self.output_text.append(
                        {
                            "status": True,
                            "text": self.read_pdf(file),
                            "links": self.get_hyperlinks(file),
                        }
                    )
                except Exception as e:
                    self.output_text.append({"status": False, "text": str(e)})
            else:
                self.output_text.append({"status": False, "text": "Not a .pdf file"})
        return self.output_text
