def build_summary_prompt(document_text: str) -> str:
    return (
        "You are a helpful assistant. Summarize the document below in 3-5 concise sentences. "
        "Use only the provided document content. Do not invent or assume any facts.\n\n"
        "Document:\n"
        f"{document_text}"
    )


def build_chat_prompt(document_text: str, question: str) -> str:
    return (
        "You are a helpful assistant. Answer the question using only the provided document content. "
        "If the answer is not in the document, say you do not know. Never invent information.\n\n"
        "Document:\n"
        f"{document_text}\n\n"
        "Question:\n"
        f"{question}"
    )
