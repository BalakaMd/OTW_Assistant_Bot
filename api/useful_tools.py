import os
import re

import environ
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from langchain_google_vertexai import ChatVertexAI

from langchain_anthropic import ChatAnthropic

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from api.models import ChatsHistory, ModelSettings
from api.db_templates import end_conference, start_conference

env = environ.Env(
    OPENAI_API_KEY=str,
    ANTHROPIC_API_KEY=str,
    GOOGLE_API_KEY=str
)

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


def send_question_to_llm(question, chat_id, customer_id=None):
    model_settings = ModelSettings.objects.get(settings_id=1)
    system_prompt = model_settings.system_prompt
    model_name = model_settings.model_name
    model_temperature = model_settings.temperature
    number_of_qa_history = model_settings.number_of_QA_history
    number_of_chunks = model_settings.number_of_chunks

    llm = create_llm(model_name, model_temperature)

    customer_vectorstore = FAISS.load_local("db/customers_contexts", embeddings,
                                            allow_dangerous_deserialization=True)
    contacts_vectorstore = FAISS.load_local("db/contacts", embeddings, allow_dangerous_deserialization=True)
    customer_vectorstore.merge_from(contacts_vectorstore)

    search_kwargs = {"k": number_of_chunks, 'score_threshold': 0.6}
    if customer_id:
        search_kwargs["filter"] = {"customer_id": customer_id}

    chat_history = []

    user_messages, created = ChatsHistory.objects.get_or_create(chat_id=chat_id)

    for message in user_messages.messages:
        chat_history.append(("human", message['human']))
        chat_history.append(("ai", message['assistant']))

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
        ]
    )

    retriever = customer_vectorstore.as_retriever(query=question, search_type="similarity_score_threshold",
                                                  search_kwargs=search_kwargs)

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    response = rag_chain.invoke({"input": question,
                                 "chat_history": chat_history[-number_of_qa_history:]})
    answer = response["answer"]

    user_messages.messages.append({'human': question, 'assistant': answer})
    user_messages.save()

    chat_history = user_messages.messages

    return answer, chat_history, response


def clean_text(context, metadata):
    cleaned_text = re.sub(r'\u200e', '', context)
    cleaned_text = re.sub(r'(\r\n)+', '\r\n', cleaned_text)
    cleaned_text = re.sub(r'_{3,}', '', cleaned_text)
    if metadata["contact_id"]:
        cleaned_text = cleaned_text.replace('\\', '')
        cleaned_text = cleaned_text.replace('"', '')

    return cleaned_text


def create_document(context, metadata, is_decorated=False):
    cleaned_text = clean_text(context, metadata)
    if is_decorated:
        cleaned_text = start_conference + cleaned_text + end_conference
    return [Document(page_content=cleaned_text, metadata=metadata)]


def create_llm(model_name, model_temperature, project_id=None):
    if model_name in ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo']:
        return ChatOpenAI(model=model_name, temperature=model_temperature)
    elif model_name == 'gemini-pro':
        return ChatVertexAI(
            model=model_name,
            temperature=model_temperature,
            project=project_id
        )
    elif model_name == 'claude-3-haiku-20240307':
        return ChatAnthropic(model=model_name, temperature=model_temperature)
    else:
        raise ValueError(f"Unsupported model name: {model_name}")
