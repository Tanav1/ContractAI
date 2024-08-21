import streamlit as st
import os
from pdf_utils import extract_text_with_headers
from text_processing import clean_text, parse_ai_response, get_closest_match
from generative_model import setup_model, setup_model_key_insights
from fuzzywuzzy import process, fuzz
import pandas as pd

def home():
    st.title('Welcome to ContractAI')

    st.write("""
    **Understanding Your Contracts with AI Technology**

    ContractAI is built to assist you in navigating the detailed content of contract documents. By using advanced technology to extract and analyze information from PDFs, this tool aims to simplify the process, allowing you to focus on what's important.
    """)

    st.header('Features of ContractAI')
    st.write("""
    - **Efficient Processing**: Upload your contract documents and quickly see key information extracted and organized for review.
    - **High Accuracy**: Reduce the risk of human error with AI-driven data extraction that highlights essential details.
    - **Insightful Analysis**: Gain insights into your contracts with analyses that highlight crucial clauses and requirements.
    """)

    st.header('Using ContractAI')
    st.write("""
    1. **Upload Your PDF**: Start by uploading your contract document directly into the application.
    2. **Automatic Extraction**: Our system will analyze your document, identifying and extracting key information.
    3. **Review Your Data**: Look over the extracted information and utilize the insights provided to better understand your contract's content.
    """)

    st.header('A Supplement for Proposal Writers')
    st.write("""
    ContractAI is designed as a powerful supplement for proposal writers working across various sectors, including government contracting, legal affairs, and commercial procurement. By automating the extraction and analysis of key contractual elements, proposal writers can:
    
    - **Enhance Efficiency**: Streamline the initial review of complex documents, allowing more time to focus on strategic aspects of proposal writing.
    - **Improve Accuracy**: Minimize the risk of overlooking critical details that could impact the success of a proposal.
    - **Gain Competitive Edge**: Quickly identify clauses and requirements that are crucial for crafting a compelling proposal.
    """)

    st.header('Getting Started')
    st.write("""
    To begin, simply upload a document. The application is designed to handle structured PDF documents effectively. For the best results, ensure your PDFs are not encrypted and are in good condition.

    **Note**: The tool is optimized for clarity and ease of use, helping you decipher complex contracts with less effort.
    """)



def about():
    st.title('About ContractAI')

    st.write("""
    ### Technical Overview of ContractAI

    **Technology and Libraries**:
    ContractAI leverages a combination of Python libraries and advanced AI algorithms to process and analyze contract documents effectively. Key technologies include:

    - **PyPDF2 and PyMuPDF (fitz)**: Used for reading and extracting text from PDF files.
    - **Pandas**: Employs this data manipulation library to handle and organize extracted data efficiently.
    - **FuzzyWuzzy**: Utilizes fuzzy logic for matching text, which is crucial for aligning and comparing document headers.
    - **Google's Generative AI**: Interacts with Google Gemini 1.5 Pro's advanced model to generate insights and summarize content.

    **AI and Machine Learning**:
    The backbone of ContractAI involves generative AI models hosted by Google that interpret and analyze text. These models are configured to:

    - Identify key headers and content within contracts.
    - Provide justifications for why specific sections are important using natural language processing techniques.

    **Architecture**:
    ContractAI operates on a streamlined architecture designed for scalability and efficiency:
    
    - **Extraction Layer**: Extracts text from PDFs and identifies headers using style and text analysis.
    - **Processing Layer**: Cleans and preprocesses text data, making it ready for analysis.
    - **AI Layer**: Utilizes configured AI models to interpret extracted data and generate actionable insights.
    - **User Interface**: Built using Streamlit, the interface provides an easy-to-use platform for users to interact with the tool, upload documents, and receive outputs.

    """)

    st.subheader("System Architecture")
    st.image("assets/ContractAI-Architecture.png", caption='System Architecture Diagram', use_column_width=True)


def analyze_pdf():
    st.title('ContractAI')

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        save_path = 'uploaded_files'
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        file_path = os.path.join(save_path, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            text_dict = extract_text_with_headers(file_path)
            #st.text(text_dict)
            #cleaned_data = {header: clean_text(content) for header, content in text_dict.items()}
            cleaned_data = {clean_text(header): clean_text(content) for header, content in text_dict.items()}
            df = pd.DataFrame(list(cleaned_data.items()), columns=['Headers', 'Content'])
            df.dropna(inplace=True)

            if not df.empty:
                st.write("Extracted and Cleaned Headers and Content:")
                #df = df[df['Content'].notna() & (df['Content'] != '')]
                df = df[df['Content'].notna() & (df['Content'] != '') & (df['Content'].str.len() >= 30)]
                st.dataframe(df)

                # Get API key from user
                api_key = st.text_input("Enter your API key for AI model:", type="password")
                if api_key and st.button('Analyze Headers'):
                    # Call the AI model
                    important_headers = setup_model(api_key, df['Headers'].tolist())
                    important_headers_string = str(important_headers)
                    #st.text(important_headers_string)
                    header_justification_df = parse_ai_response(important_headers_string)
                    st.write("Most Important Headers + Justification from RFP:")
                    st.dataframe(header_justification_df)
                    
                    header_justification_df['Headers'] = header_justification_df['Headers'].str.replace(':', '', regex=False)            

                    # Merge the dataframes on the 'Header' and 'Headers' columns (case-insensitive)
                    header_justification_df['matched_header'] = header_justification_df['Headers'].apply(
                    lambda x: get_closest_match(x, df['Headers'])
                                                    )

                    #missing_headers = header_justification_df[~header_justification_df['Headers'].isin(merged_df['Headers_y'])]['Headers']

                # Merge based on the matched headers
                    merged_df = pd.merge(header_justification_df, df, left_on='matched_header', right_on='Headers', how='left')
                    merged_df = merged_df.replace('', pd.NA)  # Optional: convert empty strings to NaN
                    merged_df = merged_df.dropna(how='any')
                    #st.dataframe(merged_df)

                    key_insights = setup_model_key_insights(merged_df, api_key)  # Adjust API key if different
                    st.write("Generated Key Insights from RFP:")
                    st.text(key_insights)

        except Exception as e:
            st.error(f"Failed to process PDF file: {str(e)}")
            st.error("Make sure the PDF is not encrypted or corrupt.")


def main():
    st.sidebar.title('Navigation')
    choice = st.sidebar.radio("Go to", ('Home', 'Analyze PDF', 'About'))
    if choice == 'Home':
        home()
    elif choice == 'Analyze PDF':
        analyze_pdf()
    elif choice == 'About':
        about()

if __name__ == "__main__":
    main()
