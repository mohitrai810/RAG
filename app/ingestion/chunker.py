from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentChunker:
    def __init__(self,chunk_size = 800 , chunk_overlap = 120):
        if chunk_size <= 0: raise ValueError("Chunk_size must be greater than 0")
        if chunk_overlap <0: raise ValueError("chunk_overlap must be greater than 0")
        if chunk_overlap>chunk_size: raise ValueError("Chunk_size should be greater than chunk_overlap")

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

        
    def split(self,document:list[Document]):
        return self.splitter.split_documents(document)
    