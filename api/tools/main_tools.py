import re

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from api.tools.db_templates import end_conference, start_conference

embeddings = OpenAIEmbeddings()


def add_data_to_faiss(document, chunk_size=500, chunk_overlap=100, path="db/customers_contexts"):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap,
                                                   add_start_index=True)
    docs = text_splitter.split_documents(document)
    temporary_db = FAISS.from_documents(docs, embeddings)
    try:
        old_db = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
        old_db.merge_from(temporary_db)
        old_db.save_local(path)
        print("Number of vectors after adding data to FAISS: ", old_db.index.ntotal)

    except RuntimeError:
        temporary_db.save_local(path)
        print(f"New FAISS DB was created. Path: {path}")
        print("Number of vectors after adding data to FAISS::", temporary_db.index.ntotal)


def remove_data_from_faiss(data_id, metadata_tag="customer_id", path="db/customers_contexts"):
    try:
        vectorstore = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
        ids_to_remove = []
        for doc_id, doc in vectorstore.docstore._dict.items():
            if doc.metadata.get(metadata_tag) == data_id:
                ids_to_remove.append(doc_id)
        if ids_to_remove:
            vectorstore.delete(ids_to_remove)
            vectorstore.save_local(path)
            print(f"Data with ID {data_id} removed from FAISS index.")
        print("Number of vectors after removing data from FAISS:", vectorstore.index.ntotal)
    except Exception as e:
        print(f"Error occurred while removing data for customer_id: {data_id} from FAISS:", str(e))


def clean_text(context, metadata):
    cleaned_text = re.sub(r'\u200e', '', context)
    cleaned_text = re.sub(r'(\r\n)+', '\r\n', cleaned_text)
    cleaned_text = re.sub(r'_{3,}', '', cleaned_text)
    if metadata.get('contact_id'):
        cleaned_text = cleaned_text.replace('\\', '')
        cleaned_text = cleaned_text.replace('"', '')

    return cleaned_text


def create_document(context, metadata, is_decorated=False):
    cleaned_text = clean_text(context, metadata)
    if is_decorated:
        cleaned_text = start_conference + cleaned_text + end_conference
    return [Document(page_content=cleaned_text, metadata=metadata)]


def pull_data_from_crm(customer_id):
    return ['Hello! Оливер Суцкин любит красное вино с сахаром']
