from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI
import difflib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Website to fetch content from
FIXED_URL = "https://dollarstoresupplies.com/"

# Function to extract website text
def fetch_website_text(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=". ").strip()
        return text
    except Exception as e:
        return f"Error fetching website content: {e}"

# Function to find relevant context from website content
def find_relevant_text(text, query):
    sentences = text.split(". ")
    query_words = set(query.lower().split())
    relevant_sentences = []

    for idx, sentence in enumerate(sentences):
        if any(word in sentence.lower() for word in query_words):
            relevant_sentences.append(sentence)
            relevant_sentences.extend(sentences[idx + 1:idx + 3])
            break

    if not relevant_sentences:
        matches = difflib.get_close_matches(query, sentences, n=1, cutoff=0.4)
        if matches:
            idx = sentences.index(matches[0])
            relevant_sentences.append(matches[0])
            relevant_sentences.extend(sentences[idx + 1:idx + 3])

    return ". ".join(relevant_sentences) if relevant_sentences else ""

# Main route
@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    error = ""
    website_content = fetch_website_text(FIXED_URL)

    if website_content.startswith("Error"):
        error = website_content

    if request.method == 'POST':
        query = request.form.get('query', '')
        if query:
            context = find_relevant_text(website_content, query)
            if not context:
                result = "Sorry, no relevant content found on the site."
            else:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are a helpful assistant. Use ONLY the provided CONTEXT to answer briefly."),
                    ("user", "CONTEXT: {context}\nQUESTION: {question}")
                ])
                output_parser = StrOutputParser()
                try:
                    llama_llm = OllamaLLM(model="gemma3:1b")
                    chain = prompt | llama_llm | output_parser
                    response = chain.invoke({"context": context, "question": query})
                except:
                    response = ""

                if not response or len(response.strip()) < 5:
                    try:
                        gpt_llm = ChatOpenAI(model="gpt-4.o-mini")
                        chain = prompt | gpt_llm | output_parser
                        response = chain.invoke({"context": context, "question": query})
                    except Exception as e:
                        response = f"Error using GPT: {e}"

                result = response

        # Return only the response part for AJAX
        return render_template("partials/bot_response.html", result=result, error=error)

    # On first page load
    return render_template("index.html", result=None, error=None)

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
