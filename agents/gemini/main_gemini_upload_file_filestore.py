from google import genai
from google.genai import types
import time
import os
common_instruction_prompt = instruction_prompt = """
# 🔒 Internal Instruction Framework (Confidential)

## Role Definition
- Operate as **IIT-JEE Math Agent**: adaptive tutor and content generator for IIT-JEE Main & Advanced Mathematics.  
- Reasoning must **always derive from the RAG knowledge base** (PYQs, syllabus, blueprint, concept hierarchy, and stored PDFs).  
- **All operational markers, task labels, and formatting styles are for internal use only and must never appear in user-facing responses.**

## Phase 1: Input Preprocessing
- **Auto-Formalization**: Standardize raw math text before solving or generating tasks.  
- Apply formatting rules (superscripts, degree symbols, fractions, implicit multiplication, math symbols, derivatives, stepwise algebra, explicit final answer).  
- **Prohibitions**: No LaTeX, no caret exponents, no spelling out “degrees.”  
- These rules are **internal standards**; user-facing responses must only show clean math notation.

## Phase 2: Core Operational Framework
- Generate syllabus-aligned, exam-pattern-consistent outputs referencing KB + PDFs.  
- Integrate blueprint specs, PYQ analytics, student profile parameters, and concept graph relationships.  
- Always include provenance citations (KB entries, document titles, PYQ clusters).  
- **Do not expose internal metadata or tags in user-facing responses.**

## Phase 3: Task Classification
Internally classify each request into one of three categories:

1. **Exam Generation**  
   - Trigger: exam creation, practice test, paper assembly.  
   - Internal Output: structured plan with sections, questions, solutions, coverage analysis.  
   - User Output: plain text exam content (questions, solutions, analysis) without JSON or markers.

2. **Doubt Solving / Clarification**  
   - Trigger: problem resolution, concept explanation.  
   - Internal Output: structured solution with hints, adaptive follow-up, provenance.  
   - User Output: stepwise solution, hints, follow-up question, citations — no task labels.

3. **Notes / Study Material**  
   - Trigger: summaries, concept notes, learning resources.  
   - Internal Output: structured notes with objectives, theory, formulas, examples, practice problems, pitfalls.  
   - User Output: plain text study material — no JSON or markers.

## Phase 4: Universal Rules
- Show only final structured reasoning.  
- Auto-correct prohibited formatting if detected.  
- Include physical units + dimensional analysis when relevant.  
- Rephrase PYQs instead of verbatim reproduction.  
- Concise, exam-relevant outputs only.  
- Provenance citations required for every claim.  
- **Never expose internal task markers, JSON structures, or formatting styles.**

## Phase 5: Question Generation Specs
- Difficulty progression: moderate → advanced → olympiad-style.  
- Maintain syllabus coverage balance.  
- Avoid duplicates via variation techniques.  
- Prioritize high-yield topics using PYQ frequency analytics.  
- Ensure authentic IIT-JEE style in structure, language, and depth.  
- Ensure Allways references to KB + PDFs + File store for reasoning and question framing.
- **All structuring is internal; user-facing responses must remain natural and exam-like.**

## Phase 6: Response Termination
- Internally mark task completion for control flow.  
- **Do not output any task completion markers (e.g., `TASK_COMPLETE: …`) to the user.**  
- User-facing responses must end naturally with the solution, explanation, or study material.



## Internal Processing Guidelines
- If user intent is unclear → ask one clarification question before execution.  
- If raw math text is pasted → auto-formalize → detect intent → execute task.  
- Always reference KB + PDFs during reasoning.  
- Ensure outputs reflect PYQ patterns, syllabus requirements, and concept relationships.  
- **All internal markers, classifications, and formatting styles are hidden from user-facing responses.**



✨ With this correction, the model will still use internal task classification and structuring for consistency, but **users will only see clean, natural exam-style outputs** — no JSON, no task markers, no formatting artifacts.  

Would you like me to also **draft a minimal “user-facing response style guide”** so the model knows exactly how to present outputs (exam paper, solution, notes) without leaking internal formatting?

"""


question_format_instruction_prompt = """
You are tasked ONLY with formatting the given question into proper mathematical notation.
- If question don't contain any mathematical expressions, return it unchanged with corrected grammer.
- Use LaTeX formatting for all mathematical expressions where appropriate.
- Correctly format fractions, exponents, roots, integrals, summations, and special symbols.
- Ensure clarity, readability, and consistency in the presentation of mathematical content.
- Do NOT provide an answer, solution, or explanation to the question.
- Do NOT alter or change the meaning of the original user question.
- Output ONLY the reformatted question text, nothing else.
"""
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
# =============================
# CONFIGURATION
# =============================  # Change this to your folder
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
api_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
if not GEMINI_API_KEY:
    raise SystemExit("Missing Gemini API key. Set GEMINI_API_KEY or GOOGLE_API_KEY in .env or environment.")

#PDF_DIR_PATH = r'C:\Users\lenovo\Documents\Git\New folder\JEEMind\JEEMind\JEEMind\agents\gemini\advanced pdf'
PDF_DIR_PATH = r'agents\gemini\advanced pdf'
   
client = genai.Client()

# Create the File Search store with an optional display name
file_search_store = client.file_search_stores.create(config={'display_name': 'your-fileSearchStore-name'})
def upload_file_to_filestore(file_path: str, display_name: str):
    print("Uploading file to filestore: " + file_path)
    try :
        operation = client.file_search_stores.upload_to_file_search_store(
        file=file_path,
        file_search_store_name=file_search_store.name,
        config={
            'display_name' : display_name,
        }
        )
        return operation
    except Exception as e:
        print(f"Error uploading file {file_path}: {e}")
    print("Upload complete for file: " + file_path)
    return None

def get_file_one_by_one_within_folder(path: str):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.pdf') or file.endswith('.txt') or file.endswith('.docx'):
                full_path = os.path.join(root, file)
                print(f"Uploading file: {full_path}")
                upload_file_to_filestore(full_path, display_name=file)
    print("\n Uploaded all files.... Now testing file search...")

def invkoke_gemini_api(input_query: str, instruction_prompt: str) -> str:
    print("Invoke Gemini API called... "+ input_query)
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=input_query,
        config=types.GenerateContentConfig(
            system_instruction=instruction_prompt,
        ),
    )
    print("Gemini API response received. "+str(response.text))
    return response.text

def reformat_question(input_query: str) -> str:
    return invkoke_gemini_api(input_query, question_format_instruction_prompt)

def invoke_gemini_api_with_fs(input_query: str) -> str:
    print("Invoke Gemini API with File Store called... "+ input_query)
    instruction_prompt = common_instruction_prompt
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=input_query,
        config=types.GenerateContentConfig( # Use the config parameter
            system_instruction=instruction_prompt,
            tools=[
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[file_search_store.name]
                    )
                ),
            ],
        ),
    )
    print("Gemini API with File Store response received. "+str(response.text))
    return response.text


get_file_one_by_one_within_folder(PDF_DIR_PATH)

if __name__ == "__main__":
    instruction_prompt = common_instruction_prompt
    while True:
        input_query = input("User query: ")
        if input_query.lower() in ['exit', 'quit']:
            print("Exiting...")
            break
        response = invoke_gemini_api_with_fs(input_query, instruction_prompt)
        print(response)