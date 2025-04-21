from langchain_ollama import ChatOllama


def answer_question(model_name: str, question: str, document_text: str) -> str:
    """Answer a question based on the provided file.

    :param model_name: The model name running locally on Ollama
    :param question: Free flow question
    :param document_text: Document text
    :return:
    """
    llm = ChatOllama(model=model_name)
    prompt = f"Answer the following question based on the document: {document_text}\n\nQuestion: {question}\nAnswer:"
    response = llm.invoke(prompt)
    return response.content


def summarize_text(model_name: str, text: str) -> str:
    """Summarise the text and return it.
    :param model_name: The model name running locally on Ollama
    :param text: The text to summarise
    :return:
    """
    llm = ChatOllama(model=model_name)
    prompt = f"Summarize the following text:\n\n{text}"
    response = llm.invoke(prompt)

    return response.content
