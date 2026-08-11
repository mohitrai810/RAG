from pathlib import Path
from langchain_core.documents import Document

from langchain_community.document_loaders import PyPDFLoader,TextLoader

supported_ex = {".pdf",".txt",".md"}

def load_document(file_path:str):
    path = Path(file_path)
    if not path.exists():raise FileNotFoundError("File empty")

    ex = path.suffix.lower()
    if ex not in supported_ex:raise ValueError(f"Unsupported document : {ex}")

    if ex == ".pdf":loader = PyPDFLoader(str(path))
    else : loader = TextLoader(str(path),encoding = "utf-8")
    return loader.load()

