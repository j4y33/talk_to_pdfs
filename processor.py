from langchain.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
import pinecone
import PyPDF2
import os
import click
import config

OPENAI_API_KEY = config.OPENAI_API_KEY
PINECONE_API_KEY = config.PINECONE_API_KEY
PINECONE_API_ENV = config.PINECONE_API_ENV # you can get this on pinecone

def get_page_count(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        page_count = len(reader.pages)
        return page_count

# Get a list of all PDF files in the "PDFs" directory
def process_pdf():
    pdf_directory = "PDFs"
    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]

    # Check if a PDF file exists in the directory
    if pdf_files:
        # Load the PDF file
        file_path = os.path.join(pdf_directory, pdf_files[0])
        loader = UnstructuredPDFLoader(file_path)
        # Now you can use 'loader' to work with the loaded PDF
    else:
        print("No PDF file found in the directory.")

    # Load the data and split it into consumable chunks
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(data)

    return texts


def process_query(texts, query, a): 

    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    # Initialize pinecone
    pinecone.init(
        api_key=PINECONE_API_KEY,  # find at app.pinecone.io
        environment=PINECONE_API_ENV  # next to api key in console
    )
    index_name = "demoindex" # put in the name of your pinecone index here
    
    text_contents = [t.page_content for t in texts]
    docsearch = Pinecone.from_texts(text_contents, embeddings, index_name=index_name)


    # Query the docs to get an answer back
    llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
    chain = load_qa_chain(llm, chain_type="stuff")

    docs = docsearch.similarity_search(query,k=a)
    print(len(docs))
    result = chain.run(input_documents=docs, question=query)

    return result

if __name__ == '__main__': 
    texts = process_pdf()
    
    out = process_query(texts, "what are great data platforms?", 2)
    print(out)
    
