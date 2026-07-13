"""
Gemini Evaluator - Asynchronous LLM-as-a-Judge evaluation for Agent Runs.
Checks for Hallucination (0-100) and Context Relevance (0-100) and writes back to SQLite.
"""
from __future__ import annotations

import os
import time
import json
import sqlite3
import threading
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Evaluator prompts
EVALUATION_SYSTEM_PROMPT = """You are an expert AI financial and risk auditor acting as an "LLM-as-a-Judge".
Your task is to evaluate a generated financial analysis report against the retrieved context document chunks used by the analyst agent.

You will assess two metrics:
1. Context Relevance Score (0-100): How relevant and useful is the retrieved context to the analyst's query? 
   - 100 means the context contains everything needed to fully answer the query.
   - 0 means the context is completely irrelevant and has no connection to the query.
2. Hallucination Score (0-100): Does the generated report contain any claims, facts, or numbers that are not supported by or contradict the retrieved context?
   - 0 means the report is completely faithful to the context (every fact, name, and number is verified in the retrieved documents).
   - 100 means the report is entirely fabricated or contains severe contradictions and unsupported facts.

You must output your evaluation in JSON format with the following keys:
- "relevance_score": integer between 0 and 100
- "hallucination_score": integer between 0 and 100
- "feedback": detailed text explaining your scoring, listing any specific discrepancies or hallucinations found, and noting if the context was relevant.

Strictly return ONLY a valid JSON object matching the schema.
Do not wrap your output in markdown code blocks like ```json ... ```. Just return raw JSON.
"""

EVALUATION_USER_PROMPT = """
Analyst Query:
{query}

Retrieved Context Documents:
{context}

Generated Report:
{report}

Perform the evaluation and output the JSON.
"""

_evaluator_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "telemetry.db")

def evaluate_run_with_gemini(client: genai.Client, query: str, context: str, report: str) -> dict | None:
    """Invokes Gemini to perform the evaluation with priority fallback models and returns the structured result."""
    user_content = EVALUATION_USER_PROMPT.format(
        query=query,
        context=context,
        report=report
    )
    
    models = ["gemini-3.5-flash", "gemini-2.0-flash", "gemini-3.1-flash-lite"]
    
    for model_name in models:
        try:
            print(f"[Gemini Evaluator] Attempting evaluation using model {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=user_content,
                config=types.GenerateContentConfig(
                    system_instruction=EVALUATION_SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    temperature=0.1,
                )
            )
            
            # Parse the JSON response
            text = response.text.strip()
            # Clean markdown codeblocks if LLM included them despite system prompt instructions
            if text.startswith("```"):
                lines = text.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                text = "\n".join(lines).strip()
                
            data = json.loads(text)
            return {
                "hallucination_score": int(data.get("hallucination_score", 0)),
                "relevance_score": int(data.get("relevance_score", 0)),
                "feedback": str(data.get("feedback", "")),
            }
        except Exception as e:
            print(f"[Gemini Evaluator Error] Failed calling Gemini model {model_name}: {e}")
            # Try the next model
            continue
            
    print("[Gemini Evaluator Error] All models in fallback list failed.")
    return None

def run_evaluation_loop(db_path: str = _evaluator_db_path, api_key: str | None = None, once: bool = False):
    """
    Background worker loop that polls for completed agent runs and runs Gemini evaluations.
    Can be run as a continuous loop or a single pass (once=True).
    """
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY", "")
    
    if not api_key:
        print("[Gemini Evaluator] No Gemini API key provided. Background evaluator cannot start.")
        return

    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f"[Gemini Evaluator] Failed to initialize Gemini Client: {e}")
        return

    print(f"[Gemini Evaluator] Active. Monitoring database: {db_path}")

    while True:
        try:
            # Connect to database and find completed agent runs that don't have evaluations yet
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ar.agent_run_id, ar.prompt, ar.output, ar.session_id, s.query
                FROM agent_runs ar
                JOIN sessions s ON ar.session_id = s.session_id
                WHERE ar.eval_hallucination_score IS NULL 
                  AND ar.status = 'SUCCESS'
            """)
            rows = cursor.fetchall()
            conn.close()

            for run_id, prompt, output, session_id, s_query in rows:
                print(f"[Gemini Evaluator] Evaluating run {run_id}...")
                
                # Fetch all retrieved context (tool outputs from RAG retrieval) for this run
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT tool_output
                    FROM tool_invocations
                    WHERE agent_run_id = ? 
                      AND tool_name = 'rag_retrieval'
                    ORDER BY start_time ASC
                """, (run_id,))
                tool_outputs = cursor.fetchall()
                conn.close()

                # Concatenate all retrieved document chunks
                context_chunks = []
                for i, (tool_out,) in enumerate(tool_outputs, 1):
                    context_chunks.append(f"--- Context Segment {i} ---\n{tool_out}")
                
                context = "\n\n".join(context_chunks) if context_chunks else "No retrieved context docs found."

                # Run evaluation via Gemini
                eval_res = evaluate_run_with_gemini(client, s_query, context, output)
                
                if eval_res:
                    now = datetime.utcnow().isoformat() + "Z"
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE agent_runs
                        SET eval_hallucination_score = ?,
                            eval_relevance_score = ?,
                            eval_feedback = ?,
                            eval_timestamp = ?
                        WHERE agent_run_id = ?
                    """, (
                        eval_res["hallucination_score"],
                        eval_res["relevance_score"],
                        eval_res["feedback"],
                        now,
                        run_id
                    ))
                    conn.commit()
                    conn.close()
                    print(f"[Gemini Evaluator] Evaluated run {run_id}: Hallucination={eval_res['hallucination_score']}, Relevance={eval_res['relevance_score']}")
                else:
                    # To prevent stalling on error, write an error placeholder or retry later
                    print(f"[Gemini Evaluator] Temporary error evaluating run {run_id}. Will retry.")

            if once:
                break
                
            time.sleep(4)
        except Exception as e:
            print(f"[Gemini Evaluator Loop Error] {e}")
            if once:
                break
            time.sleep(10)

if __name__ == "__main__":
    print("Starting manual execution of Gemini Evaluator loop (once=False)...")
    run_evaluation_loop(once=False)


_evaluator_thread = None
_evaluator_lock = threading.Lock()

def start_evaluator_worker(api_key: str | None = None):
    """Starts the background evaluation thread if not already running."""
    global _evaluator_thread
    with _evaluator_lock:
        if _evaluator_thread is None or not _evaluator_thread.is_alive():
            _evaluator_thread = threading.Thread(
                target=run_evaluation_loop,
                args=(_evaluator_db_path, api_key, False),
                daemon=True,
                name="GeminiEvaluatorWorker"
            )
            _evaluator_thread.start()


def stop_evaluator_worker():
    """Stops the background evaluation thread."""
    global _evaluator_thread
    with _evaluator_lock:
        if _evaluator_thread is not None and _evaluator_thread.is_alive():
            # Wait for it to join (though daemon=True, nice to stop it cleanly if possible, 
            # but since there's no stop event flag, we just let it die when the main thread dies)
            pass

