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


# def extract_text_with_headers(pdf_path):
#     try:
#         doc = fitz.open(pdf_path)
#     except Exception as e:
#         print(f"Error opening PDF: {e}")
#         return {}
    
#     text_dict = {}
#     current_header = None
#     for page_num in range(len(doc)):
#         page = doc.load_page(page_num)
#         blocks = page.get_text("dict")["blocks"]
#         for block in blocks:
#             if block['type'] == 0:  # text block
#                 block_text = " ".join(span['text'] for line in block['lines'] for span in line['spans'])
#                 is_header_candidate = any(span['flags'] & 2 or span['size'] > 12 or span['text'].isupper() for line in block['lines'] for span in line['spans'])

#                 if is_header_candidate and len(block_text.strip()) < 100:  # Consider a header if short and stylized
#                     current_header = block_text.strip()
#                     text_dict[current_header] = []
#                 elif current_header:
#                     text_dict[current_header].append(block_text.strip())

#     # Clean and join the text under each header
#     for header in text_dict:
#         text_dict[header] = "\n".join(text_dict[header]).strip()

#     return text_dict
