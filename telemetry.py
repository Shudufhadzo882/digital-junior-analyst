"""
Telemetry and Database logging utilities for the Digital Junior Analyst.
Provides a thread-safe Queue, background DB worker, and LangChain callback handler.
"""
from __future__ import annotations

import os
import sqlite3
import queue
import threading
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from langchain_core.callbacks import BaseCallbackHandler

# Global telemetry queue and worker state
_telemetry_queue = queue.Queue()
_worker_thread = None
_worker_lock = threading.Lock()
_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "telemetry.db")

def safe_str(val: Any) -> str:
    if val is None:
        return ""
    if isinstance(val, (list, dict, tuple)):
        import json
        try:
            return json.dumps(val)
        except Exception:
            return str(val)
    return str(val)

def safe_float(val: Any) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


class TelemetryDB:
    """Manages SQLite schema and inserts/updates for telemetry tables."""
    
    def __init__(self, db_path: str = _db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize tables if they do not exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enforce foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # 1. Sessions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                query TEXT,
                timestamp TEXT,
                latency REAL,
                status TEXT,
                method TEXT,
                final_report TEXT
            )
        """)
        
        # 2. Agent Runs Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_runs (
                agent_run_id TEXT PRIMARY KEY,
                session_id TEXT,
                agent_name TEXT,
                prompt TEXT,
                output TEXT,
                status TEXT,
                start_time TEXT,
                end_time TEXT,
                latency REAL,
                eval_hallucination_score REAL,
                eval_relevance_score REAL,
                eval_feedback TEXT,
                eval_timestamp TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id) ON DELETE CASCADE
            )
        """)
        
        # 3. Tool Invocations Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tool_invocations (
                tool_invocation_id TEXT PRIMARY KEY,
                agent_run_id TEXT,
                tool_name TEXT,
                tool_input TEXT,
                tool_output TEXT,
                status TEXT,
                start_time TEXT,
                end_time TEXT,
                latency REAL,
                FOREIGN KEY (agent_run_id) REFERENCES agent_runs (agent_run_id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        conn.close()

    def process_event(self, event: Dict[str, Any]):
        """Ingest a parsed telemetry event into SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        try:
            etype = event.get("type")
            if etype == "session_start":
                cursor.execute("""
                    INSERT OR REPLACE INTO sessions (session_id, query, timestamp, status, method)
                    VALUES (?, ?, ?, 'RUNNING', ?)
                """, (
                    safe_str(event.get("session_id")),
                    safe_str(event.get("query")),
                    safe_str(event.get("timestamp")),
                    safe_str(event.get("method"))
                ))
                
            elif etype == "session_end":
                cursor.execute("""
                    UPDATE sessions
                    SET latency = ?, status = ?, final_report = ?
                    WHERE session_id = ?
                """, (
                    safe_float(event.get("latency")),
                    safe_str(event.get("status")),
                    safe_str(event.get("final_report")),
                    safe_str(event.get("session_id"))
                ))
                
            elif etype == "agent_start":
                cursor.execute("""
                    INSERT OR REPLACE INTO agent_runs (agent_run_id, session_id, agent_name, prompt, status, start_time)
                    VALUES (?, ?, ?, ?, 'RUNNING', ?)
                """, (
                    safe_str(event.get("agent_run_id")),
                    safe_str(event.get("session_id")),
                    safe_str(event.get("agent_name")),
                    safe_str(event.get("prompt")),
                    safe_str(event.get("start_time"))
                ))
                
            elif etype == "agent_end" or etype == "agent_error":
                cursor.execute("""
                    UPDATE agent_runs
                    SET output = ?, status = ?, end_time = ?, latency = ?
                    WHERE agent_run_id = ?
                """, (
                    safe_str(event.get("output")),
                    safe_str(event.get("status")),
                    safe_str(event.get("end_time")),
                    safe_float(event.get("latency")),
                    safe_str(event.get("agent_run_id"))
                ))
                
            elif etype == "tool_start":
                cursor.execute("""
                    INSERT OR REPLACE INTO tool_invocations (tool_invocation_id, agent_run_id, tool_name, tool_input, status, start_time)
                    VALUES (?, ?, ?, ?, 'RUNNING', ?)
                """, (
                    safe_str(event.get("tool_invocation_id")),
                    safe_str(event.get("agent_run_id")) if event.get("agent_run_id") else None,
                    safe_str(event.get("tool_name")),
                    safe_str(event.get("tool_input")),
                    safe_str(event.get("start_time"))
                ))
                
            elif etype == "tool_end" or etype == "tool_error":
                cursor.execute("""
                    UPDATE tool_invocations
                    SET tool_output = ?, status = ?, end_time = ?, latency = ?
                    WHERE tool_invocation_id = ?
                """, (
                    safe_str(event.get("tool_output")),
                    safe_str(event.get("status")),
                    safe_str(event.get("end_time")),
                    safe_float(event.get("latency")),
                    safe_str(event.get("tool_invocation_id"))
                ))
                
            conn.commit()
        except Exception as e:
            # Silent print to console to prevent blocking UI
            print(f"[TelemetryDB Error] Failed processing event: {e}")
        finally:
            conn.close()


class TelemetryCallbackHandler(BaseCallbackHandler):
    """
    LangChain callback handler to capture agent execution and tool invocations.
    Pushes events onto a thread-safe global queue.
    """
    
    def __init__(self, session_id: str):
        super().__init__()
        self.session_id = session_id
        self.start_times: Dict[str, float] = {}

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: Any,
        parent_run_id: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        run_str = str(run_id)
        self.start_times[run_str] = time.time()
        
        # Log AgentExecutor (parent_run_id is None, indicating root ReAct executor)
        if parent_run_id is None:
            # ReAct agent prompt query is in 'input'
            prompt = inputs.get("input", "")
            event = {
                "type": "agent_start",
                "agent_run_id": run_str,
                "session_id": self.session_id,
                "agent_name": "Digital Junior Analyst ReAct Agent",
                "prompt": prompt,
                "start_time": datetime.utcnow().isoformat() + "Z",
            }
            enqueue_telemetry(event)

    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: Any,
        parent_run_id: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        run_str = str(run_id)
        start_time = self.start_times.pop(run_str, time.time())
        latency = time.time() - start_time
        
        if parent_run_id is None:
            output = outputs.get("output", "")
            event = {
                "type": "agent_end",
                "agent_run_id": run_str,
                "output": output,
                "end_time": datetime.utcnow().isoformat() + "Z",
                "latency": latency,
                "status": "SUCCESS",
            }
            enqueue_telemetry(event)

    def on_chain_error(
        self,
        error: BaseException,
        *,
        run_id: Any,
        parent_run_id: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        run_str = str(run_id)
        start_time = self.start_times.pop(run_str, time.time())
        latency = time.time() - start_time
        
        if parent_run_id is None:
            event = {
                "type": "agent_error",
                "agent_run_id": run_str,
                "output": f"Exception: {str(error)}",
                "end_time": datetime.utcnow().isoformat() + "Z",
                "latency": latency,
                "status": "FAILED",
            }
            enqueue_telemetry(event)

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: Any,
        parent_run_id: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        run_str = str(run_id)
        self.start_times[run_str] = time.time()
        tool_name = serialized.get("name", "Unknown Tool")
        
        event = {
            "type": "tool_start",
            "tool_invocation_id": run_str,
            "agent_run_id": str(parent_run_id) if parent_run_id else None,
            "tool_name": tool_name,
            "tool_input": input_str,
            "start_time": datetime.utcnow().isoformat() + "Z",
        }
        enqueue_telemetry(event)

    def on_tool_end(
        self,
        output: Any,
        *,
        run_id: Any,
        parent_run_id: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        run_str = str(run_id)
        start_time = self.start_times.pop(run_str, time.time())
        latency = time.time() - start_time
        
        event = {
            "type": "tool_end",
            "tool_invocation_id": run_str,
            "tool_output": str(output),
            "end_time": datetime.utcnow().isoformat() + "Z",
            "latency": latency,
            "status": "SUCCESS",
        }
        enqueue_telemetry(event)

    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: Any,
        parent_run_id: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        run_str = str(run_id)
        start_time = self.start_times.pop(run_str, time.time())
        latency = time.time() - start_time
        
        event = {
            "type": "tool_error",
            "tool_invocation_id": run_str,
            "tool_output": f"Exception: {str(error)}",
            "end_time": datetime.utcnow().isoformat() + "Z",
            "latency": latency,
            "status": "FAILED",
        }
        enqueue_telemetry(event)


def enqueue_telemetry(event: Dict[str, Any]):
    """Pushes a telemetry event into the processing queue."""
    _telemetry_queue.put(event)


def _telemetry_worker_loop():
    """Loops and processes events from the telemetry queue."""
    db = TelemetryDB()
    while True:
        try:
            event = _telemetry_queue.get()
            if event is None:  # Shutdown signal
                _telemetry_queue.task_done()
                break
            db.process_event(event)
            _telemetry_queue.task_done()
        except Exception as e:
            print(f"[Telemetry Worker Loop Error] {e}")


def start_telemetry_worker():
    """Starts the background telemetry processor thread if not already running."""
    global _worker_thread
    with _worker_lock:
        if _worker_thread is None or not _worker_thread.is_alive():
            # Initialize DB schema on main thread to prevent race conditions
            TelemetryDB()
            _worker_thread = threading.Thread(target=_telemetry_worker_loop, daemon=True, name="TelemetryWorker")
            _worker_thread.start()


def stop_telemetry_worker():
    """Stops the telemetry processor thread."""
    global _worker_thread
    with _worker_lock:
        if _worker_thread is not None and _worker_thread.is_alive():
            _telemetry_queue.put(None)
            _worker_thread.join()
            _worker_thread = None


def log_manual_telemetry(session_id: str, query: str, context: str, report: str, latency: float, status: str, method: str):
    """Manually log a direct RAG execution or fallback as an agent run and tool invocation."""
    import uuid
    from datetime import datetime
    
    run_id = str(uuid.uuid4())
    tool_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    
    # 1. Agent Start
    enqueue_telemetry({
        "type": "agent_start",
        "agent_run_id": run_id,
        "session_id": session_id,
        "agent_name": f"Digital Junior Analyst Direct RAG ({method})",
        "prompt": query,
        "start_time": now,
    })
    
    # 2. Tool Start
    enqueue_telemetry({
        "type": "tool_start",
        "tool_invocation_id": tool_id,
        "agent_run_id": run_id,
        "tool_name": "rag_retrieval",
        "tool_input": query,
        "start_time": now,
    })
    
    # 3. Tool End
    enqueue_telemetry({
        "type": "tool_end",
        "tool_invocation_id": tool_id,
        "tool_output": context,
        "end_time": now,
        "latency": 0.1,  # minor latency for retrieving documents
        "status": "SUCCESS",
    })
    
    # 4. Agent End
    enqueue_telemetry({
        "type": "agent_end",
        "agent_run_id": run_id,
        "output": report,
        "end_time": now,
        "latency": latency,
        "status": status,
    })

