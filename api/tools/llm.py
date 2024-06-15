import environ
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_vertexai import ChatVertexAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from api.models import ChatsHistory, ModelSettings
from api.tools.main_tools import pull_data_from_crm

env = environ.Env(
    OPENAI_API_KEY=str,
    ANTHROPIC_API_KEY=str,
    GOOGLE_API_KEY=str
)

embeddings = OpenAIEmbeddings()


def send_question_to_llm(question, chat_id, customer_id=None):
    model_settings = ModelSettings.objects.get(settings_id=1)
    system_prompt = model_settings.system_prompt
    model_name = model_settings.model_name
    model_temperature = model_settings.temperature
    number_of_qa_history = model_settings.number_of_QA_history
    number_of_chunks = model_settings.number_of_chunks

    chat_history = []
    whatsapp_chat_history = []

    llm = create_llm(model_name=model_name, model_temperature=model_temperature)

    # FAISS management
    customer_vectorstore = FAISS.load_local("db/customers_contexts", embeddings,
                                            allow_dangerous_deserialization=True)
    contacts_vectorstore = FAISS.load_local("db/contacts", embeddings, allow_dangerous_deserialization=True)
    customer_vectorstore.merge_from(contacts_vectorstore)

    search_kwargs = {"k": number_of_chunks, 'score_threshold': 0.6}

    # Current chat history management
    user_messages, created = ChatsHistory.objects.get_or_create(chat_id=chat_id)

    if customer_id > 0:
        # search_kwargs["filter"] = {"customer_id": customer_id}
        whatsapp_chat_history = pull_data_from_crm(customer_id=customer_id)
        user_messages.whatsapp_chat_history = whatsapp_chat_history
        user_messages.save()

    for message in user_messages.messages:
        chat_history.append(("human", message['human']))
        chat_history.append(("ai", message['assistant']))

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("placeholder", "{chat_history}"),
            ("placeholder", "{whatsapp_chat_history}"),
            ("human", "{input}"),
        ]
    )

    limited_chat_history = chat_history[-number_of_qa_history:]
    retriever = customer_vectorstore.as_retriever(query=question + str(limited_chat_history),
                                                  search_type="similarity_score_threshold",
                                                  search_kwargs=search_kwargs)

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    response = rag_chain.invoke({"input": question,
                                 "chat_history": limited_chat_history,
                                 "whatsapp_chat_history": whatsapp_chat_history})
    answer = response["answer"]

    user_messages.messages.append({'human': question, 'assistant': answer})
    user_messages.save()

    chat_history = user_messages.messages
    questions_asked = f'{len(limited_chat_history)}/{number_of_qa_history}'

    return answer, chat_history, questions_asked, response


def create_llm(model_name, model_temperature, project_id=None):
    if model_name in ['gpt-3.5-turbo', 'gpt-4o', 'gpt-4-turbo']:
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
