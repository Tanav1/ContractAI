from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBox, LTTextLine, LTTextContainer

def extract_text_with_headers(pdf_path):
    text_dict = {}
    current_header = None

    # Iterate over each page in the PDF
    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                text = element.get_text()
                # Assuming headers are uppercase and possibly larger in size; adjust as needed
                if text.isupper():
                    current_header = text.strip()
                    text_dict[current_header] = []
                elif current_header:
                    text_dict[current_header].append(text.strip())

    # Combine the text pieces under each header
    for header in text_dict:
        text_dict[header] = " ".join(text_dict[header]).strip()

    return text_dict

