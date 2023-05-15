import streamlit as st
import os
import json
import PyPDF2
import time
from tqdm import tqdm
import sys

from processor import process_pdf, process_query


def upload_file():
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        # Save the uploaded file to the "pdfs" directory
        with open(os.path.join("PDFs", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success("File uploaded successfully!")

        # Set file_uploaded to True
        st.session_state.file_uploaded = True

        st.write("Start building index... please standby")

        return uploaded_file  # Return the uploaded file


def get_page_count(uploaded_file):
    with open(os.path.join("PDFs", uploaded_file.name), "rb") as file:
        reader = PyPDF2.PdfReader(file)
        page_count = len(reader.pages)
        return page_count


def question(uploaded_file, count):
    # Only show the chat interface if file_uploaded is True
    if st.session_state.file_uploaded:
        if 'queries_answers' not in st.session_state:
            st.session_state['queries_answers'] = {}  # Initialize queries_answers with an empty dictionary

        queries_answers = st.session_state['queries_answers']

        query = st.text_input(f"Pose your question (clear input for next one)", key="query")

        submit_button = st.button("Submit", key="submit")

        # Check if the user has submitted a query
        if submit_button:
            # Display a waiting logo while waiting for the answer
            waiting_message = st.empty()
            waiting_message.text("Waiting for answer...")
            with st.spinner():
                # Pass the user's query to another app to get the answer
                answer = process_query(st.session_state.texts, query, count)

            # Display the answer to the user
            st.write(answer)

            # Add the query and answer to the list of queries
            queries_answers[query] = answer
            st.session_state['queries_answers'] = queries_answers

        # Check if the user has clicked the "Save and Terminate?" button
        if st.button("Save and Terminate", key="terminate"):
            json_object = json.dumps(queries_answers, indent=8)

            with open("sample.json", "w") as outfile:
                outfile.write(json_object)

            # Display a message to the user that the conversation has been terminated and the queries have been saved
            st.success("Conversation terminated. Queries saved.")

            # Delete the PDF file
            pdf_path = os.path.join("pdfs", uploaded_file.name)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                st.success("PDF file deleted.")

            # Remove the session state
            st.session_state.file_uploaded = False
            del st.session_state['queries_answers']
            del st.session_state['texts']


    else:
        st.warning("Please upload a PDF file first.")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    else:
        count = 4  # Set the default value as 3 if no command line argument is provided
    st.set_page_config(page_title='PDF Chatbot', page_icon=':books:')
    if "file_uploaded" not in st.session_state:
        st.session_state.file_uploaded = False

    uploaded_file = upload_file()

    # Process the PDF only once when the file is uploaded
    if st.session_state.file_uploaded and 'texts' not in st.session_state:
        page_count = get_page_count(uploaded_file)  # Pass the uploaded_file to get_page_count

        st.write(f"[this process will take around {page_count*1.5} seconds]")
        texts = process_pdf()
        st.success("Done processing PDF!")
        st.session_state.texts = texts

    question(uploaded_file, count)