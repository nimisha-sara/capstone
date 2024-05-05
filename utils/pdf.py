"""This file if for pdf file or url processing"""

import re
import fitz
import requests


class PDF:
    """
    Class to read and process PDF files.

    Args:
        file_paths (list): List of file paths of PDF files.
    """

    def __init__(self, file_paths: list):
        self.file_paths = file_paths
        self.output_text = []

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

    def handle_unicode(self, text: str) -> str:
        """
        Replace Unicode characters with their respective symbols.

        Args:
            text (str): Text to process.

        Returns:
            str: Processed text with Unicode characters replaced.
        """
        replacements = {
            "\u2013": "-",
            "\u2014": "--",
            "\u2026": "...",
            "\u2018": "'",
            "\u2019": "'",
            "\u201C": '"',
            "\u201D": '"',
            "\u00A0": " ",
            "\u201a": ",",
            "\u201e": '"',
            "\u2022": "-",
            "\u2015": "--",
            "\u2212": "-",
        }

        pattern = re.compile("|".join(re.escape(key) for key in replacements.keys()))
        processed_text = pattern.sub(lambda match: replacements[match.group(0)], text)
        return processed_text

    def read_pdf(self, file_path: str, path_type: str = "file") -> str:
        """
        Read text from a PDF file.

        Args:
            file_path (str): Path to the PDF file.
            path_type (str): Type of file to be processed - 'file'(default), 'url'

        Returns:
            str: Text extracted from the PDF.
        """
        file_text = ""
        if path_type == "file":
            doc = fitz.open(filename=file_path, filetype="pdf")
        elif path_type == "url":
            res = requests.get(file_path, timeout=10)
            doc = fitz.open(stream=res.content, filetype="pdf")
        for page in doc:
            text = page.get_text()
            file_text += text
        return self.clean_text(file_text)

    def get_hyperlinks(self, file_path: str, path_type: str = "file") -> list:
        """
        Get hyperlinks from a PDF file

        Args:
            file_path (str): Path to the PDF file
            type (str): Type of File to be processed - 'file'(default), 'url'

        Returns:
            list: List of hyperlinks found in the PDF
        """
        if path_type == "file":
            doc = fitz.open(filename=file_path, filetype="pdf")
        elif path_type == "url":
            res = requests.get(file_path, timeout=10)
            doc = fitz.open(stream=res.content, filetype="pdf")

        hyperlinks = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            annotations = page.links()

            for annotation in annotations:
                hyperlink = annotation.get("uri")
                if hyperlink:
                    hyperlinks.append(hyperlink)

        doc.close()
        return hyperlinks

    def process_pdf(self, path_type: str = "file"):
        """
        Process PDF files.

        Args:
            path_type (str): Type of file to be processed - 'file'(default), 'url'

        Returns:
            list: List containing dictionaries with status, text, and links for each processed PDF.
        """
        for file in self.file_paths:
            if path_type == "url":
                if "/file/" in file and "/view" in file:
                    fileid = re.findall(pattern='[-\w]{25,}', string=file)[0]
                    file = f"https://drive.google.com/uc?id={fileid}"
                else:
                    return {
                        "status": False,
                        "text": "Not a valid URL. Ensure that it is a drive link and has view access",
                        "filename": file,
                    }
            try:
                self.output_text.append(
                    {
                        "status": True,
                        "text": self.read_pdf(file_path=file, path_type=path_type),
                        "links": self.get_hyperlinks(
                            file_path=file, path_type=path_type
                        ),
                    }
                )
            except Exception as e:
                self.output_text.append(
                    {"status": False, "text": str(e), "filename": file}
                )
        return self.output_text
