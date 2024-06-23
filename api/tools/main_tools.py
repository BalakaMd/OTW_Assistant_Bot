from textwrap import dedent

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from api.tasks import add_data_to_faiss
from api.models import CustomerContext, Contact, Lead
from api.tools.db_templates import all_meetings

embeddings = OpenAIEmbeddings()


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
        return f"Number of vectors after removing data from FAISS: {vectorstore.index.ntotal}"
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

    add_data_to_faiss(document=meeting_document, chunk_size=10000, chunk_overlap=200, path="db/meetings",
                      is_rewrite=True)


