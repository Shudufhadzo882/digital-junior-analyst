"""
LangChain Agentic Core for the Digital Junior Analyst.
Uses langchain-classic for ReAct agent (create_react_agent / AgentExecutor),
compatible with LangChain v1.3+.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# Tool Functions (pure Python — no LangChain decoration at module level)
# ---------------------------------------------------------------------------

def rag_retrieval(query: str, store, k: int = 6) -> str:
    """
    Retrieve relevant document chunks from the FAISS vector store.
    Returns a formatted string with source citations.
    """
    if not store.is_ready:
        return "No documents loaded in vector store. Please upload documents or use demo mode."
    try:
        return store.retrieve_text(query, k=k)
    except Exception as e:
        return f"Retrieval error: {e}"


def financial_calculator(expression: str) -> str:
    """
    Perform safe financial ratio and metric calculations.
    Supports: P/E ratio, debt-to-equity, current ratio, EBITDA margin,
    Sharpe ratio, interest coverage, leverage ratio, and basic arithmetic.
    """
    expr = expression.strip().lower()
    results = []

    patterns = [
        (r"pe\s*ratio.*price[:\s]+([\d.]+).*eps[:\s]+([\d.]+)", "P/E Ratio",
         lambda m: f"{float(m.group(1)) / float(m.group(2)):.2f}x"),
        (r"current\s*ratio.*current\s*assets?[:\s]+([\d.]+).*current\s*liabilities?[:\s]+([\d.]+)",
         "Current Ratio", lambda m: f"{float(m.group(1)) / float(m.group(2)):.2f}x"),
        (r"debt.to.equity.*total\s*debt[:\s]+([\d.]+).*equity[:\s]+([\d.]+)",
         "Debt-to-Equity", lambda m: f"{float(m.group(1)) / float(m.group(2)):.2f}x"),
        (r"ebitda\s*margin.*ebitda[:\s]+([\d.]+).*revenue[:\s]+([\d.]+)",
         "EBITDA Margin", lambda m: f"{(float(m.group(1)) / float(m.group(2))) * 100:.1f}%"),
        (r"interest\s*coverage.*ebit[:\s]+([\d.]+).*interest[:\s]+([\d.]+)",
         "Interest Coverage", lambda m: f"{float(m.group(1)) / float(m.group(2)):.2f}x"),
        (r"leverage.*(?:net\s*debt|debt)[:\s]+([\d.]+).*ebitda[:\s]+([\d.]+)",
         "Leverage Ratio (Net Debt/EBITDA)", lambda m: f"{float(m.group(1)) / float(m.group(2)):.2f}x"),
        (r"gross\s*margin.*gross\s*profit[:\s]+([\d.]+).*revenue[:\s]+([\d.]+)",
         "Gross Margin", lambda m: f"{(float(m.group(1)) / float(m.group(2))) * 100:.1f}%"),
    ]

    for pattern, label, compute in patterns:
        m = re.search(pattern, expr)
        if m:
            try:
                val = compute(m)
                results.append(f"{label}: {val}")
            except ZeroDivisionError:
                results.append(f"{label}: Division by zero — check inputs")

    if not results:
        simple = re.sub(r"[^0-9+\-*/().\s]", "", expression)
        try:
            if simple.strip():
                val = eval(simple, {"__builtins__": {}})  # safe eval
                results.append(f"Result: {val:.4f}")
        except Exception:
            pass

    if not results:
        return (
            f"Could not parse '{expression}' as a known financial formula. "
            "Try format: 'P/E ratio price: 25.0 EPS: 2.50' or 'leverage net debt: 3.1 EBITDA: 0.764'"
        )

    return "\n".join(results)


def risk_matrix_builder(risk_factors_json: str) -> str:
    """
    Build a structured risk matrix from a JSON list of risk factors.
    Input: JSON string with list of {name, likelihood, impact, severity} objects.
    """
    try:
        factors = json.loads(risk_factors_json)
    except json.JSONDecodeError:
        return (
            "Risk Matrix Generation:\n"
            "Provide risk factors as JSON: "
            '[{"name":"...", "likelihood":"High", "impact":"Critical", "severity":"Critical"}]'
        )

    severity_order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
    sorted_factors = sorted(
        factors,
        key=lambda x: severity_order.get(x.get("severity", "Low"), 0),
        reverse=True
    )

    lines = [
        "| Risk Factor | Likelihood | Impact | Severity |",
        "|-------------|------------|--------|----------|",
    ]
    for f in sorted_factors:
        name = f.get("name", "Unknown")
        likelihood = f.get("likelihood", "Unknown")
        impact = f.get("impact", "Unknown")
        severity = f.get("severity", "Unknown")
        lines.append(f"| {name} | {likelihood} | {impact} | **{severity}** |")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Report Prompt Template
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are the Digital Junior Analyst — a highly capable, precise financial and risk intelligence analyst.

Your role is to produce Tier 1 investment-bank quality "Instant Synthesized Risk Reports" grounded in actual document data.

You have access to the following tools:
1. `rag_retrieval` — searches the internal document database for relevant information. Always use this FIRST to ground your analysis.
2. `financial_calculator` — performs financial ratio and metric calculations with precision.
3. `risk_matrix_builder` — generates a structured risk matrix table from identified risk factors.

REPORT FORMAT
When you have gathered sufficient information, produce a report with these sections:
- **EXECUTIVE SUMMARY** — 3-4 sentence synthesis of the core situation
- **KEY RISK FACTORS** — bullet list with severity tag [CRITICAL/HIGH/MEDIUM/LOW] for each
- **FINANCIAL METRICS ANALYSIS** — key numbers, ratios, and what they signal
- **RISK MATRIX** — structured table of all identified risks
- **STRATEGIC RECOMMENDATIONS** — 3-5 actionable recommendations
- **ANALYST CONFIDENCE** — rate your confidence in this report (HIGH/MEDIUM/LOW) and explain why

Always cite your sources inline using format: *(Source: [document title])*
Always use precise numbers from the retrieved documents.
Never fabricate specific financial figures — only use numbers found in the source documents.
"""

REPORT_PROMPT_TEMPLATE = """
Generate an Instant Synthesized Risk Report for the following analyst query:

QUERY: {query}

Instructions:
1. Start by calling `rag_retrieval` with the query to retrieve relevant document context.
2. If the query mentions financial ratios or metrics, call `financial_calculator` with specific numbers found in retrieved documents.
3. After gathering information, synthesize a comprehensive risk report.
4. Use `risk_matrix_builder` to create the final risk matrix section.

Provide a thorough, investment-bank quality analysis.
"""

REACT_PROMPT_TEMPLATE = """You are the Digital Junior Analyst — a precise financial and risk intelligence analyst.

You have access to these tools:

{tools}

Use the following format exactly:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat up to 6 times)
Thought: I now know the final answer
Final Answer: [the complete structured risk report here]

REPORT FORMAT for Final Answer:
**EXECUTIVE SUMMARY**
[3-4 sentence synthesis]

**KEY RISK FACTORS**
- [CRITICAL] Risk name — description *(Source: document)*
- [HIGH] Risk name — description *(Source: document)*

**FINANCIAL METRICS ANALYSIS**
[key numbers and ratios found in documents]

**RISK MATRIX**
[call risk_matrix_builder and include its output here]

**STRATEGIC RECOMMENDATIONS**
1. [recommendation]
2. [recommendation]

**ANALYST CONFIDENCE**: [HIGH/MEDIUM/LOW] — [brief rationale]

Always cite sources. Never fabricate financial figures.

Begin!

Question: {input}
Thought:{agent_scratchpad}"""


# ---------------------------------------------------------------------------
# Agent Builder (using langchain-classic)
# ---------------------------------------------------------------------------

def build_analyst_agent(api_key: str, store, temperature: float = 0.1):
    """
    Construct a LangChain ReAct agent using langchain-classic.

    Returns:
        AgentExecutor ready to invoke.
    """
    from langchain_classic.agents import create_react_agent, AgentExecutor
    from langchain_classic.tools import Tool
    from langchain_classic.prompts import PromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        google_api_key=api_key,
        temperature=temperature,
    )

    tools = [
        Tool(
            name="rag_retrieval",
            func=lambda query: rag_retrieval(query, store),
            description=(
                "Search the internal document database for relevant financial and risk information. "
                "Use this first to ground your analysis in actual document data. "
                "Input: a search query string describing what information you need."
            ),
        ),
        Tool(
            name="financial_calculator",
            func=financial_calculator,
            description=(
                "Calculate financial ratios and metrics with precision. "
                "Supported: P/E ratio, debt-to-equity, current ratio, EBITDA margin, "
                "interest coverage, leverage ratio, gross margin. "
                "Input format example: 'leverage net debt: 3.1 EBITDA: 0.764'"
            ),
        ),
        Tool(
            name="risk_matrix_builder",
            func=risk_matrix_builder,
            description=(
                "Build a structured risk matrix table from identified risk factors. "
                "Input: JSON string with list of risk factors. "
                'Example: [{"name":"Liquidity Risk","likelihood":"High","impact":"Critical","severity":"Critical"}]'
            ),
        ),
    ]

    prompt = PromptTemplate.from_template(REACT_PROMPT_TEMPLATE)
    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=8,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )
    return executor


# ---------------------------------------------------------------------------
# Direct RAG fallback (simpler, always works)
# ---------------------------------------------------------------------------

def generate_report_direct(query: str, api_key: str, store) -> str:
    """
    Directly call Gemini with RAG context — no agent overhead.
    Used as fallback if the ReAct agent fails.
    """
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage, SystemMessage

    context = rag_retrieval(query, store, k=6)

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        google_api_key=api_key,
        temperature=0.1,
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""
DOCUMENT CONTEXT (retrieved from internal knowledge base):
{context}

ANALYST QUERY: {query}

Generate a complete, structured risk report based on the above document context.
Use the exact report format: EXECUTIVE SUMMARY, KEY RISK FACTORS, FINANCIAL METRICS ANALYSIS,
RISK MATRIX (as a markdown table), STRATEGIC RECOMMENDATIONS, ANALYST CONFIDENCE.
If the context does not contain enough information for certain sections, note the data gap explicitly.
"""),
    ]

    response = llm.invoke(messages)
    return response.content


# ---------------------------------------------------------------------------
# Main report generation entry point
# ---------------------------------------------------------------------------

def run_analyst(
    query: str,
    api_key: str,
    store,
    use_agent: bool = True,
    status_callback=None,
) -> Dict[str, Any]:
    """
    Main entry point for generating a risk report.

    Returns:
        Dict with keys: 'report', 'sources', 'intermediate_steps', 'method'
    """
    if status_callback:
        status_callback("🔍 Retrieving relevant documents from knowledge base...")

    # Always retrieve sources for citation display
    sources = []
    if store.is_ready:
        raw_results = store.retrieve(query, k=6)
        sources = [
            {
                "title": doc.metadata.get("title", "Unknown"),
                "source": doc.metadata.get("source", "Unknown"),
                "chunk": doc.page_content[:400] + ("..." if len(doc.page_content) > 400 else ""),
                "score": round(score, 4),
            }
            for doc, score in raw_results
        ]

    intermediate_steps = []
    method = "direct"
    report = ""

    if use_agent:
        try:
            if status_callback:
                status_callback("🤖 Initializing ReAct analyst agent...")
            executor = build_analyst_agent(api_key, store)

            if status_callback:
                status_callback("⚡ Agent is reasoning step-by-step (multi-tool)...")

            result = executor.invoke(
                {"input": REPORT_PROMPT_TEMPLATE.format(query=query)}
            )
            report = result.get("output", "")
            intermediate_steps = result.get("intermediate_steps", [])
            method = "agent"

            if status_callback:
                status_callback("✅ Report synthesis complete.")

        except Exception as e:
            if status_callback:
                status_callback(
                    f"⚠️ Agent hit an issue ({type(e).__name__}). "
                    f"Falling back to direct RAG synthesis..."
                )
            report = generate_report_direct(query, api_key, store)
            method = "direct_fallback"
            if status_callback:
                status_callback("✅ Report generated via direct RAG.")
    else:
        if status_callback:
            status_callback("⚡ Generating report via RAG synthesis (direct mode)...")
        report = generate_report_direct(query, api_key, store)
        method = "direct"
        if status_callback:
            status_callback("✅ Report synthesis complete.")

    return {
        "report": report,
        "sources": sources,
        "intermediate_steps": intermediate_steps,
        "method": method,
    }
