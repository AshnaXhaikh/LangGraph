# Phrasal Verb → Google Docs Automation

A LangGraph-based workflow that autonomously generates phrasal verbs from root verbs and appends them with definitions & examples to a formatted Google Doc.

## 🧠 How It Works

1. **Input** – A root verb (e.g., `"bring"`, `"look"`, `"set"`)
2. **LLM Step 1** – Gemini Flash generates a common phrasal verb (e.g., `"bring up"`)
3. **LLM Step 2** – Gemini explains it with a definition and creative example
4. **Google Docs API** – Appends the result to a shared Doc with:
   - Heading 1 for the phrasal verb
   - Italic + blue text for the root verb reference
   - Clean separation between definition and example

## 🔁 LangGraph Workflow

```
START → generate_phrasal_verb → explain_phrasal_verb → save_to_google_doc → END
```

- **State**: `PhrasalVerbState` (verb, phrasal_verb, meaning, doc_id)
- **Checkpointing**: In-memory saver (thread persistence per session)

## 🛠️ Tech Stack

- LangGraph (state machine + workflow)
- LangChain + Google Generative AI (Gemini Flash)
- Google Docs API (writing & formatting)
- Python

## 🚀 Setup

### 1. Clone the repo and navigate to this folder

```bash
git clone <your-repo>
cd langgraph-workflows/phrasal-verb-google-docs-automation
```

### 2. Install dependencies

```bash
pip install langgraph langchain-google-genai google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 3. Google API Setup

- Enable **Google Docs API** and **Google Drive API** in Google Cloud Console.
- Create an API key for Gemini (Google AI Studio).
- For Colab: store the key as a secret named `google_key`.
- For local: set environment variable `GOOGLE_API_KEY` and authenticate via `gcloud` or service account.

### 4. Shared Google Doc

- Create a Google Doc, share it with your service account email (or yourself).
- Replace `SHARED_DOC_ID` in the script with your document ID.

## 🧪 Run the Workflow

```python
from workflow import run_autonomous_workflow

run_autonomous_workflow("bring", "thread_001")
```

Output:
```
🚀 Processing: bring...
✅ Added 'bring up' to Autonomous_vocabulary_workflow.
📄 Open Doc: https://docs.google.com/document/d/<DOC_ID>/edit
```

## 🧠 Example Generated Entry in Google Doc

```
_______________________________________________________

BRING UP
Root Verb: bring

Definition: To introduce a topic for discussion.

Example: I decided not to bring up the ghost in the attic during our first dinner party.
```

## 🔁 Extending

We can reuse this pattern for any content generation pipeline:
- Flashcard generators
- Meeting note summarizers
- Automated glossary builders

Just swap the prompt logic and the target API.

```
