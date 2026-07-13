"""
Telemetry Integration Test.
Runs end-to-end telemetry generation and asserts DB entries and Gemini evaluations.
"""
import os
import time
import sqlite3
from dotenv import load_dotenv
from rag_pipeline import get_store, load_demo_documents
from analyst_agent import run_analyst
from telemetry import start_telemetry_worker, stop_telemetry_worker
from evaluator import run_evaluation_loop

load_dotenv()

def run_test():
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        print("[ERROR] GEMINI_API_KEY not found in environment. Cannot run test.")
        return

    print("=== Starting End-to-End Telemetry Integration Test ===")

    # 1. Initialize store with demo data
    print("[INFO] Initializing vector store with demo documents...")
    store = get_store()
    docs = load_demo_documents()
    store.build(docs, api_key=api_key)

    # 2. Start background telemetry worker
    print("[INFO] Starting telemetry logging thread...")
    start_telemetry_worker()

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "telemetry.db")
    if os.path.exists(db_path):
        # Clear database to ensure clean test results
        print("[INFO] Cleaning existing telemetry database...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tool_invocations;")
        cursor.execute("DELETE FROM agent_runs;")
        cursor.execute("DELETE FROM sessions;")
        conn.commit()
        conn.close()

    # 3. Execute Analyst Query (Using direct mode for fast deterministic execution)
    query = "What is the leverage ratio for ACME Corp and are they at risk of a covenant breach?"
    print(f"[QUERY] Executing query: '{query}'...")
    res = run_analyst(query, api_key, store, use_agent=False)
    session_id = res["session_id"]
    print(f"[SUCCESS] Session completed! Session ID: {session_id}")

    # Give a brief moment for background queue to flush to SQLite
    time.sleep(2)

    # 4. Verify DB Records
    print("[INFO] Verifying SQLite records...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check session
    cursor.execute("SELECT session_id, query, status, method, final_report FROM sessions WHERE session_id = ?", (session_id,))
    session_row = cursor.fetchone()
    assert session_row is not None, "[ERROR] Session record not found in database!"
    print(f"  - Session status: {session_row[2]} (Expected: SUCCESS)")
    print(f"  - Session method: {session_row[3]} (Expected: direct)")
    assert session_row[2] == "SUCCESS", "Session status is not SUCCESS"

    # Check agent run
    cursor.execute("SELECT agent_run_id, session_id, agent_name, status, eval_hallucination_score FROM agent_runs WHERE session_id = ?", (session_id,))
    run_row = cursor.fetchone()
    assert run_row is not None, "[ERROR] Agent run record not found in database!"
    run_id = run_row[0]
    print(f"  - Agent run status: {run_row[3]} (Expected: SUCCESS)")
    assert run_row[3] == "SUCCESS", "Agent run status is not SUCCESS"

    # Check tool invocations
    cursor.execute("SELECT tool_name, status FROM tool_invocations WHERE agent_run_id = ?", (run_id,))
    tool_rows = cursor.fetchall()
    assert len(tool_rows) > 0, "[ERROR] No tool invocations found for the agent run!"
    print(f"  - Logged tool invocations: {[t[0] for t in tool_rows]} (Expected to contain 'rag_retrieval')")
    assert any(t[0] == "rag_retrieval" for t in tool_rows), "rag_retrieval tool not logged"

    conn.close()
    print("[SUCCESS] DB schema and log capture verified successfully!")

    # 5. Run Evaluator Once
    print("[INFO] Launching Gemini Evaluator loop (once=True)...")
    run_evaluation_loop(db_path, api_key, once=True)

    # 6. Verify Evaluations updated
    print("[INFO] Verifying LLM evaluation score updates...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT eval_hallucination_score, eval_relevance_score, eval_feedback FROM agent_runs WHERE agent_run_id = ?", (run_id,))
    eval_row = cursor.fetchone()
    conn.close()

    assert eval_row is not None, "[ERROR] Run record not found during eval check"
    h_score, r_score, feedback = eval_row
    assert h_score is not None, "[ERROR] Hallucination score is still NULL!"
    assert r_score is not None, "[ERROR] Context relevance score is still NULL!"
    
    print("=== ALL TESTS PASSED SUCCESSFULLY ===")
    print(f"  - Hallucination Score: {h_score}/100")
    print(f"  - Context Relevance Score: {r_score}/100")
    print(f"  - Evaluator Feedback: {feedback[:100]}...")

    # Cleanup
    stop_telemetry_worker()

if __name__ == "__main__":
    run_test()
