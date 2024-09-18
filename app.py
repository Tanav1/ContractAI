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
    **Understanding Government Request for Proposals (RFP) with AI Technology**

    ContractAI is built to assist proposal writers in navigating the detailed content of U.S. government contract documents. By using advanced technology to extract and analyze information from RFP PDFs, this tool aims to simplify the process, allowing you to focus on crafting winning proposals.
    """)

    st.header('Features of ContractAI')
    st.write("""
    - **Efficient Processing**: Upload your Request for Proposal (RFP) document and quickly see key information extracted and organized for review.
    - **High Accuracy**: Reduce the risk of human error with AI-driven data extraction that highlights essential details relevant to government contracts.
    - **Insightful Analysis**: Gain insights into your RFPs with analyses that highlight crucial clauses and requirements specific to government bids.
    """)

    st.header('Using ContractAI')
    st.write("""
    1. **Upload Your RFP PDF**: Start by uploading your government RFP document directly into the application.
    2. **Automatic Extraction**: Our system will analyze your document, identifying and extracting key information.
    3. **Review Your Data**: Look over the extracted information and utilize the insights provided to better understand the requirements and stipulations of the RFP.
    """)

    st.header('Demo Video')
    demo_video_path = "assets/ContractAI.mp4" 
    if os.path.exists(demo_video_path):
        st.video(demo_video_path)
    else:
        st.write("Demo video not found.")




    st.header('A Supplement for Government Proposal Writers')
    st.write("""
    ContractAI is designed as a powerful supplement for proposal writers working specifically on U.S. government contracts. By automating the extraction and analysis of key contractual elements, proposal writers can:
    
    - **Enhance Efficiency**: Streamline the initial review of complex RFP documents, allowing more time to focus on strategic aspects of proposal writing.
    - **Improve Accuracy**: Minimize the risk of overlooking critical details that could impact the success of a government bid.
    - **Gain Competitive Edge**: Quickly identify clauses and requirements that are crucial for crafting a compelling government proposal.
    """)

    st.header('Getting Started')
    st.write("""
    To begin, simply upload an RFP document. The application is designed to handle structured PDF documents effectively, especially those issued by the U.S. government. For the best results, ensure your PDFs are not encrypted and are in good condition.

    **Note**: The tool is optimized for clarity and ease of use, helping you decipher complex government contracts with less effort.
    """)




def about():
    st.title('About ContractAI')

    st.write("""
    ### Technical Overview of ContractAI for Government RFPs

    **Technology and Libraries**:
    ContractAI leverages a combination of Python libraries and advanced AI algorithms to process and analyze U.S. government RFP documents effectively. Key technologies include:

    - **PDF Processing Libraries (PDFMiner)**: Used for reading and extracting text from PDF files, which are commonly used for RFPs.
    - **Pandas**: Employs this data manipulation library to handle and organize extracted data efficiently.
    - **FuzzyWuzzy**: Utilizes fuzzy logic for matching text, crucial for aligning and comparing document headers within RFPs.
    - **Google's Generative AI**: Interacts with Google Gemini 1.5 Pro's advanced model to generate insights and summarize content relevant to proposal writing.

    **AI and Machine Learning**:
    The backbone of ContractAI involves generative AI models hosted by Google that interpret and analyze text specifically tailored to government RFPs. These models are configured to:

    - Identify key headers and content within government contracts.
    - Provide justifications for why specific sections are important using natural language processing techniques.

    **Architecture**:
    ContractAI operates on a streamlined architecture designed for scalability and efficiency:
    
    - **Extraction Layer**: Extracts text from RFP PDFs and identifies headers using style and text analysis.
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
            with st.spinner('Loading. Please Wait...'):
                text_dict = extract_text_with_headers(file_path)
                cleaned_data = {clean_text(header): clean_text(content) for header, content in text_dict.items()}
                df = pd.DataFrame(list(cleaned_data.items()), columns=['Headers', 'Content'])
                df.dropna(inplace=True)

            if not df.empty:
                st.write("Extracted and Cleaned Headers and Content:")
                df = df[df['Content'].notna() & (df['Content'] != '') & (df['Content'].str.len() >= 30)]
                st.dataframe(df)

                api_key = st.secrets["API_KEY"]
                if api_key and st.button('Analyze Headers'):
                    with st.spinner('Analyzing headers using AI model...'):
                        important_headers = setup_model(api_key, df['Headers'].tolist())
                        important_headers_string = str(important_headers)
                        header_justification_df = parse_ai_response(important_headers_string)
                        st.write("Most Important Headers + Justification from RFP:")
                        st.dataframe(header_justification_df)
                    
                        header_justification_df['Headers'] = header_justification_df['Headers'].str.replace(':', '', regex=False)            
                        header_justification_df['matched_header'] = header_justification_df['Headers'].apply(
                            lambda x: get_closest_match(x, df['Headers'])
                        )

                    with st.spinner('Merging data and generating insights...'):
                        merged_df = pd.merge(header_justification_df, df, left_on='matched_header', right_on='Headers', how='left')
                        merged_df = merged_df.replace('', pd.NA)
                        merged_df = merged_df.dropna(how='any')
                        key_insights = setup_model_key_insights(merged_df, api_key)
                        st.write("Generated Key Insights from RFP:")
                        st.markdown(key_insights)

                        st.download_button(
                            label="Download Report as Text",
                            data=key_insights,
                            file_name="ContractAI_Report.txt",
                            mime="text/plain")

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
