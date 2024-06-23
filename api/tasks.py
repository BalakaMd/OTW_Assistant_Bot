import logging

from textwrap import dedent

from celery import shared_task
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from api.tools.db_templates import end_conference, start_conference, recap_of_meetings

from api.models import CustomerContext, Contact, Lead

embeddings = OpenAIEmbeddings()

logger = logging.getLogger(__name__)


@shared_task
def add_data_to_faiss(chunk_size, chunk_overlap, path, is_rewrite=False, context_id=None, document=None):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap,
                                                   separators=["\n\n", "\n", " ", ""],
                                                   add_start_index=True)
    if context_id:
        document_context = CustomerContext.objects.get(id=context_id)
        client_email_1 = document_context.client_email_1
        client_email_2 = document_context.client_email_2
        client_email_3 = document_context.client_email_3
        client_id = get_contact_id_by_emails([client_email_1, client_email_2, client_email_3])
        context_recap = generate_recap(document_context.transcript)

        metadata = {
            'context_id': context_id,
            'title': document_context.title,
            'date': document_context.date,
            'client_id': client_id,
            'client_email_1': client_email_1,
            'client_email_2': client_email_2,
            'client_email_3': client_email_3,
            'transcript_url': document_context.transcript_url,
            'audio_url': document_context.audio_url,
            'video_url': document_context.video_url,
        }

        content = (
            f"Title: {metadata['title']}\n"
            f"Date: {metadata['date']}\n"
            f"Client ID: {metadata['client_id']}\n"
            f"Client Email 1: {metadata['client_email_1']}\n"
            f"Client Email 2: {metadata['client_email_2']}\n"
            f"Client Email 3: {metadata['client_email_3']}\n"
            f"Transcript URL: {metadata['transcript_url']}\n"
            f"Audio URL: {metadata['audio_url']}\n"
            f"Video URL: {metadata['video_url']}\n"
            f"Transcript: {start_conference}{document_context.transcript}{end_conference}\n"
            f"Conversation Recap :{recap_of_meetings}{metadata['date']}{context_recap}\n"
        )

        document = create_document(content, metadata)

    docs = text_splitter.split_documents(document)
    if context_id:
        for doc in docs:
            doc.page_content = generate_tags(doc.page_content)
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


def generate_tags(transcription):
    llm_prompt = dedent("""You are an intelligent assistant designed to analyze and process conversation transcripts. 
    Your main task is to read the text and add tags at the beginning of the whole text to indicate the topics and actions 
    discussed. Use the tag {question ask} if a question is asked in the text. Return the original text with the added 
    tags at the beginning of whole text.
    Here is an example to guide you:
    Input:
    "How can I reset my password? I have tried several times, but it doesn't work."
    Output:
    {question ask}{problem with password reset}{several unsuccessful attempts}
    How can I reset my password? I have tried several times, but it doesn't work.
    Ensure that you preserve the original text and correctly place the tags to reflect the content accurately.""")
    client = OpenAI()
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": llm_prompt},
            {"role": "user", "content": transcription}
        ],
        model="gpt-4o",
    )

    return response.choices[0].message.content


def create_document(context, metadata):
    return [Document(page_content=context, metadata=metadata)]


def generate_recap(transcription):
    llm_prompt = dedent("""
    Please read the following transcript of a conversation and provide a detailed summary. Include the main topics 
    discussed, important points, and key takeaways. Pay attention to the mentioned details and provide a concise 
    overview of the conversation's content.
""")
    client = OpenAI()
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": llm_prompt},
            {"role": "user", "content": transcription}
        ],
        model="gpt-4o",
    )

    return response.choices[0].message.content


def get_contact_id_by_emails(emails):
    for email in emails:
        try:
            contact = Contact.objects.get(email=email)
            return contact.contact_id
        except Contact.DoesNotExist:
            try:
                lead = Lead.objects.get(email=email)
                return lead.lead_id
            except Lead.DoesNotExist:
                continue
    return None


