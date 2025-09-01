from openai import OpenAI
from api.conf import settings
from Core.vector_store import get_retriever
from Core.summary_tool import get_summary_by_title
from Core.filter import contains_offensive_language

client = OpenAI(api_key=settings.OPENAI_API_KEY)
retriever = get_retriever()

def ask_agent(user_query: str) -> str:
    if settings.LANGUAGE_FILTER_ENABLED and contains_offensive_language(user_query):
        return "Reformuleaza intrebarea: continut nepotrivit detectat."

    docs = retriever.get_relevant_documents(user_query)
    context = "\n---\n".join([f"{doc.metadata['title']}: {doc.page_content}" for doc in docs])

    prompt = f"""
    Am urmatoarele rezumate de carti:

    {context}

    Un utilizator a intrebat: '{user_query}'

    Bazandu-te pe continutul de mai sus, recomanda o singura carte si explica pe scurt de ce.
    Intoarce doar: TITLU + explicatia.
    """


    response = client.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    answer = response.choices[0].message.content.strip()


    title_line = answer.split("\n")[0]
    title = title_line.split("–")[0].strip() if "–" in title_line else title_line.strip()

    try:
        full_summary = get_summary_by_title(title)
        final_response = f"{answer}\n\nRezumat detaliat:\n{full_summary}"
    except KeyError:
        final_response = f"{answer}\n\nNu am gasit un rezumat detaliat pentru aceasta carte."

    return final_response
