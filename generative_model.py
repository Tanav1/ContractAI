import google.generativeai as genai

def setup_model(api_key, headers):
    """Setup and interact with a generative model to identify important headers."""
    genai.configure(api_key=api_key)  # Replace with your actual API key
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 0,
        "max_output_tokens": 8192,
    }
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
    system_instruction = f"""
    The following are headers extracted from a government contract request for proposal (RFP). 
    Please identify and return the top 20 most important headers that would be helpful for a proposal writer. 
    For each header, provide a justification explaining why it is important. 
    These headers are crucial for understanding the requirements, terms, and conditions of the RFP. 
    Please use the following format for each header and justification: 'Header: Justification'. 
    The list of headers is as follows: {', '.join(headers)}
    """
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        generation_config=generation_config,
        system_instruction=system_instruction,
        safety_settings=safety_settings
    )
    response = model.generate_content(system_instruction)
    return response.text  # Extract text from the response appropriately

def setup_model_key_insights(merged_df, api_key):
    """Setup and interact with a generative model to generate key insights based on merged data."""
    genai.configure(api_key=api_key)  # Replace with your actual API key
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 0,
        "max_output_tokens": 8192,
    }
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
    formatted_headers_justification_content = []
    for index, row in merged_df.iterrows():
        formatted_headers_justification_content.append(
            f"Header: {row['Headers_x']}\nJustification: {row['Justification']}\nContent: {row['Content']}\n"
        )
    headers_justification_content_str = "\n".join(formatted_headers_justification_content)
    system_instruction_2 = f"""
    The following are headers, justifications, and content extracted from a government contract request for proposal (RFP). 
    Please take this information and generate a report with vital information for a proposal writer. Try to use as much information as possible that is fed, and also if you think something is missing and important, add it in.
    The report should be formatted well and easy to read. Make sure to cite where exactly the information is coming from in the corpus.
    The headers, justifications, and content are as follows:
    {headers_justification_content_str}
    """
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        generation_config=generation_config,
        system_instruction=system_instruction_2,
        safety_settings=safety_settings
    )
    prompted_key_insights = model.generate_content(system_instruction_2)
    return prompted_key_insights.text  # Extract text from the response appropriately

# Example usage code is omitted for brevity. Can be added based on context where this module is used.
