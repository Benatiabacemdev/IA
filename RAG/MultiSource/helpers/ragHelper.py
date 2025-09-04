
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter

class RAGHelper:
    def __init__(self):
        self.text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
    
    def get_pdf_text(self, pdf_doc):
        text = ""
        pdf_reader = PdfReader(pdf_doc)
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    def get_text_chunks(self, text):        
        chunks = self.text_splitter.split_text(text)
        return chunks
