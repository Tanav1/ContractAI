import PyPDF2
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text


def extract_text_with_headers(pdf_path):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return {}
    
    text_dict = {}
    current_header = None
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block['type'] == 0:  # text block
                block_text = " ".join(span['text'] for line in block['lines'] for span in line['spans'])
                is_header_candidate = any(span['flags'] & 2 or span['size'] > 12 or span['text'].isupper() for line in block['lines'] for span in line['spans'])

                if is_header_candidate and len(block_text.strip()) < 100:  # Consider a header if short and stylized
                    current_header = block_text.strip()
                    text_dict[current_header] = []
                elif current_header:
                    text_dict[current_header].append(block_text.strip())

    # Clean and join the text under each header
    for header in text_dict:
        text_dict[header] = "\n".join(text_dict[header]).strip()

    return text_dict
