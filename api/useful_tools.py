import re

import dotenv
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from api.models import ChatsHistory
from api.db_templates import end_conference, start_conference

dotenv.load_dotenv()

embeddings = OpenAIEmbeddings()
llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
system_prompt = ("""You are an assistant for question-answering tasks. Use the following pieces of retrieved context and 
chat history to answer the question. If you don't know the answer, just say that you don't know. Use timestamps and 
quotes from context if necessary.. Answer in the language in which the question was asked.
Context: {context}
""")


def add_data_to_faiss(document, chunk_size=2000, chunk_overlap=200, path="db/customers_contexts"):
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
    customer_vectorstore = FAISS.load_local("db/customers_contexts", embeddings,
                                            allow_dangerous_deserialization=True)
    contacts_vectorstore = FAISS.load_local("db/contacts", embeddings, allow_dangerous_deserialization=True)
    customer_vectorstore.merge_from(contacts_vectorstore)

    if customer_id:
        retriever = customer_vectorstore.as_retriever(search_type="similarity",
                                             search_kwargs={"k": 6, "filter": {"customer_id": customer_id}})
    else:
        retriever = customer_vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})

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

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    response = rag_chain.invoke({"input": question,
                                 "chat_history": chat_history})
    answer = response["answer"]

    user_messages.messages.append({'human': question, 'assistant': answer})
    user_messages.save()

    chat_history = user_messages.messages

    return answer, chat_history, response


def clean_text(context):
    cleaned_text = re.sub(r'\u200e', '', context)
    cleaned_text = re.sub(r'(\r\n)+', '\r\n', cleaned_text)
    cleaned_text = re.sub(r'_{3,}', '', cleaned_text)

    return cleaned_text


def create_document(context, metadata, is_decorated=False):
    cleaned_text = clean_text(context)
    if is_decorated:
        cleaned_text = start_conference + cleaned_text + end_conference
    return [Document(page_content=cleaned_text, metadata=metadata)]
