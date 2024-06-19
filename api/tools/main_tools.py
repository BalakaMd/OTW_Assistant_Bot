from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from api.models import CustomerContext, Contact
from api.tools.db_templates import all_meetings

embeddings = OpenAIEmbeddings()


def add_data_to_faiss(document, chunk_size, chunk_overlap, path="db/customers_contexts", is_rewrite=False):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap,
                                                   separators=["\n\n", "\n", " ", ""],
                                                   add_start_index=True)
    docs = text_splitter.split_documents(document)
    if is_rewrite:
        vectorstore = FAISS.from_documents(docs, embeddings)
        vectorstore.save_local(path)
        print("Number of vectors after rewriting data in FAISS: ", vectorstore.index.ntotal)
    else:
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


def remove_data_from_faiss(data_id, metadata_tag, path):
    try:
        vectorstore = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
        ids_to_remove = []
        for doc_id, doc in vectorstore.docstore._dict.items():
            if int(doc.metadata.get(metadata_tag)) == int(data_id):
                ids_to_remove.append(doc_id)
        if ids_to_remove:
            vectorstore.delete(ids_to_remove)
            vectorstore.save_local(path)
            print(f"Data with ID {data_id} removed from FAISS index.")
        print("Number of vectors after removing data from FAISS:", vectorstore.index.ntotal)
    except Exception as e:
        print(f"Error occurred while removing data for customer_id: {data_id} from FAISS:", str(e))


# def clean_text(context, metadata):
#     cleaned_text = re.sub(r'\u200e', '', context)
#     cleaned_text = re.sub(r'(\r\n)+', '\r\n', cleaned_text)
#     cleaned_text = re.sub(r'_{3,}', '', cleaned_text)
#     if metadata.get('contact_id'):
#         cleaned_text = cleaned_text.replace('\\', '')
#         cleaned_text = cleaned_text.replace('"', '')
#
#     return cleaned_text


def create_document(context, metadata):
    return [Document(page_content=context, metadata=metadata)]


def pull_data_from_crm(customer_id):
    return ['Hello! Оливер Суцкин любит красное вино с сахаром']


def update_meetings():
    meetings = CustomerContext.objects.all()
    data = []

    for meeting in meetings:
        meeting_info = {
            "title": meeting.title,
            "date": meeting.date.isoformat(),
            "client_email_1": meeting.client_email_1,
            "client_email_2": meeting.client_email_2,
            "client_email_3": meeting.client_email_3
        }
        data.append(meeting_info)

    texts = [
        (
            f"Title: {item['title']}\nDate: {item['date']}\nClient Emails: {item['client_email_1']},"
            f"{item['client_email_2']},{item['client_email_3']}."
        ) for item in data
    ]

    meeting_document = create_document(f'{all_meetings}{texts}', metadata={'meeting': "all_meetings"})

    add_data_to_faiss(meeting_document, chunk_size=10000, chunk_overlap=200, path="db/meetings", is_rewrite=True)


def get_contact_id_by_emails(emails):
    for email in emails:
        try:
            contact = Contact.objects.get(email=email)
            return contact.contact_id
        except Contact.DoesNotExist:
            continue
    return None
