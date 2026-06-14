# --- 1. Install & Setup (for Colab) ---
!pip install -U langgraph langchain-google-genai python-dotenv -q

from google.colab import auth
from googleapiclient.discovery import build
auth.authenticate_user()
docs_service = build('docs', 'v1')
drive_service = build('drive', 'v3')

# --- 2. API Key (stored as Colab secret) ---
from google.colab import userdata
GOOGLE_API_KEY = userdata.get('google_key')

# --- 3. Imports ---
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# --- 4. LLM Config ---
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
llm = ChatGoogleGenerativeAI(model='gemini-flash-latest')

# --- 5. State Definition ---
class PhrasalVerbState(TypedDict):
    verb: str
    phrasal_verb: str
    meaning: str
    doc_id: str

def get_clean_text(content):
    if isinstance(content, list):
        return " ".join([part['text'] for part in content if 'text' in part])
    return content

# --- 6. Node Functions ---
def generate_phrasal_verb(state: PhrasalVerbState):
    prompt = (
        f"Identify one common English phrasal verb using root verb '{state['verb']}'. "
        "Output ONLY the phrasal verb. Do not use bolding, quotes, or punctuation."
    )
    response = llm.invoke(prompt).content
    return {'phrasal_verb': get_clean_text(response).strip()}

def explain_phrasal_verb(state: PhrasalVerbState):
    prompt = (
        f"Explain the phrasal verb '{state['phrasal_verb']}'.\\n"
        "Follow this structure exactly and do NOT use Markdown (no **, no ###):\\n"
        "Definition: [Provide one clear definition] | Example: [Provide one creative sentence]"
    )
    raw_response = llm.invoke(prompt).content
    response = get_clean_text(raw_response)
    return {'meaning': response}

SHARED_DOC_ID = "your-google-doc-id"

def save_to_google_doc_formatted(state: PhrasalVerbState):
    doc = docs_service.documents().get(documentId=SHARED_DOC_ID).execute()
    end_index = doc.get('body').get('content')[-1].get('endIndex') - 1

    # Clean and format meaning
    raw_meaning = state['meaning'].replace("**", "").replace("#", "")
    if "|" in raw_meaning:
        parts = raw_meaning.split("|")
        formatted_meaning = f"{parts[0].strip()}\n\n{parts[1].strip()}"
    else:
        formatted_meaning = raw_meaning

    separator = "\n" + "_"*55 + "\n\n"
    title_line = f"{state['phrasal_verb'].upper()}\n"
    meta_line = f"Root Verb: {state['verb']}\n\n"
    full_text = separator + title_line + meta_line + formatted_meaning + "\n"

    requests = [
        {'insertText': {'location': {'index': end_index}, 'text': full_text}},
        # Heading 1 for Title
        {'updateParagraphStyle': {
            'range': {'startIndex': end_index + len(separator),
                      'endIndex': end_index + len(separator + title_line)},
            'paragraphStyle': {'namedStyleType': 'HEADING_1'}, 'fields': 'namedStyleType'
        }},
        # Italic Blue for Meta Line
        {'updateTextStyle': {
            'range': {'startIndex': end_index + len(separator + title_line),
                      'endIndex': end_index + len(separator + title_line + meta_line)},
            'textStyle': {'italic': True, 'foregroundColor': {'color': {'rgbColor': {'blue': 0.8}}}},
            'fields': 'italic,foregroundColor'
        }}
    ]
    docs_service.documents().batchUpdate(documentId=SHARED_DOC_ID, body={'requests': requests}).execute()
    return {"doc_id": SHARED_DOC_ID}

# --- 7. Build LangGraph Workflow ---
builder = StateGraph(PhrasalVerbState)
builder.add_node('generate_phrasal_verb', generate_phrasal_verb)
builder.add_node('explain_phrasal_verb', explain_phrasal_verb)
builder.add_node('save_to_google_doc', save_to_google_doc_formatted)

builder.add_edge(START, 'generate_phrasal_verb')
builder.add_edge('generate_phrasal_verb', 'explain_phrasal_verb')
builder.add_edge('explain_phrasal_verb', 'save_to_google_doc')
builder.add_edge('save_to_google_doc', END)

memory = InMemorySaver()
workflow = builder.compile(checkpointer=memory)

# --- 8. Run Function ---
def run_autonomous_workflow(root_verb: str, session_id: str):
    print(f"🚀 Processing: {root_verb}...")
    config = {'configurable': {'thread_id': session_id}}
    result = workflow.invoke({'verb': root_verb}, config=config)
    print(f"✅ Added '{result['phrasal_verb']}' to Autonomous_vocabulary_workflow.")
    print(f"📄 Open Doc: https://docs.google.com/document/d/{SHARED_DOC_ID}/edit")
    return result

# --- 9. Example Execution ---
run_autonomous_workflow("bring", "thread_001")
