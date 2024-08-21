import re
import pandas as pd
from fuzzywuzzy import process, fuzz
import pandas as pd

def get_closest_match(x, choices, scorer=fuzz.token_sort_ratio, cutoff=70):
    match = process.extractOne(x, choices, scorer=scorer, score_cutoff=cutoff)
    return match[0] if match else None

def clean_text(text):
    if isinstance(text, str):
        # Standardize newlines and remove unnecessary bullet points and placeholders
        text = re.sub(r'\n+', ' ', text)
        text = text.replace('•', '').replace('□', '')

        # Remove placeholders like underscores
        text = re.sub(r'__+', ' ', text)  # Replace underscores with space to avoid concatenation

        # Remove redundant phrases
        text = re.sub(r'\(End of Text\)', '', text)
        text = re.sub(r'\(End of provision\)', '', text)

        # Correct multiple consecutive spaces down to one
        text = re.sub(r'\s{2,}', ' ', text)

        # Specific corrections for headers involving numbers and letters
        # Adjust spacing around numbers and letters without removing necessary spaces
        text = re.sub(r'(?<=\d) (?=[A-Z])', ' ', text)  # Ensure space between numbers and uppercase letters
        text = re.sub(r'(?<=\D) (?=\d)', ' ', text)  # Ensure space between letters and numbers

        # Remove incorrect single spaces within split uppercase words
        text = re.sub(r'(?<=\b[A-Z]) (?=[A-Z]\b)', '', text)  # Handle "S COPE" -> "SCOPE"
        
        # Normalize whitespace again after all replacements
        text = ' '.join(text.split())

    return text




def parse_ai_response(response_text):
    """
    Parses the text response to extract headers and their descriptions, formatted within the same line.

    Args:
        response_text (str): Text containing headers and their descriptions formatted by AI.

    Returns:
        pd.DataFrame: A DataFrame containing headers and their descriptions.
    """
    headers = []
    descriptions = []

    # Split the text into lines
    lines = response_text.split("\n")

    # Iterate through each line to extract headers and descriptions
    for line in lines:
        line = line.strip()

        # Check if line contains a header indicated by "**"
        if '**' in line:
            # Split the line at "**" and extract relevant parts
            parts = line.split('**')
            if len(parts) >= 3:
                header = parts[1].strip()  # Header is between the first set of "**"
                description = parts[2].strip()  # Description follows after the second "**"

                # Clean up to remove any leading identifiers like numbers from the header
                header = header.split(' ', 1)[-1] if ' ' in header else header

                headers.append(header)
                descriptions.append(description)

    # Create a DataFrame from the collected headers and descriptions
    header_description_df = pd.DataFrame({
        'Headers': headers,
        'Justification': descriptions
    })

    return header_description_df
