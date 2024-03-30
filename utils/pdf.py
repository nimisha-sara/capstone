import fitz
import re
from tqdm import tqdm


class PDF:
    """
    input: 
        file_paths: list (file paths of pdf files)

    """
    def __init__(self, file_paths: list):
        self.file_paths = file_paths
        self.output_text = []
    
    def read_pdf(self, file: str) -> str:
        file_text = ""

        with fitz.open(file) as doc:
            for page in doc:
                text = page.get_text()
                file_text += text
        return self.clean_text(file_text)

    def clean_text(self, text: str) -> str:
        lines = text.split('\n')
        non_empty_lines = ' '.join(filter(lambda line: line.strip() != '', lines))
        for char in ['(', ')', ',', '[', ';', '|']:
            non_empty_lines = non_empty_lines.replace(char, " ")
        non_empty_lines = non_empty_lines.replace("  ", " ")
        return self.handle_unicode_confusions(non_empty_lines)
    
    def handle_unicode_confusions(self, text: str) -> str:
        replacements = {
            # Unicode characters and their replacements
            "\u2013": "-",   # En Dash
            "\u2014": "--",  # Em Dash
            "\u2026": "...", # Ellipsis
            "\u2018": "'",   # Left Single Quotation Mark
            "\u2019": "'",   # Right Single Quotation Mark
            "\u201C": '"',   # Left Double Quotation Mark
            "\u201D": '"',   # Right Double Quotation Mark
            "\u00A0": " ",   # Non-breaking Space
            "\u201a": ",",   # Single Low-9 Quotation Mark
            "\u201e": '"',   # Double Low-9 Quotation Mark
            "\u2022": "-",   # Bullet
            "\u2013": "-",   # En Dash
            "\u2014": "--",  # Em Dash
            "\u2015": "--",  # Horizontal Bar
            "\u2212": "-",   # Minus Sign
        }

        pattern = re.compile("|".join(re.escape(key) for key in replacements.keys()))
        processed_text = pattern.sub(lambda match: replacements[match.group(0)], text)
        return processed_text
    
    def process_pdf(self):
        for file in tqdm(self.file_paths):
            if file.split('.')[-1] == 'pdf':
                try:
                    self.output_text.append({"status": True, "text": self.read_pdf(file)})
                except Exception as e:
                    self.output_text.append({"status": False, "text": e})
            else:
                self.output_text.append({"status": False, "text": "not a .pdf file"})
        return self.output_text
