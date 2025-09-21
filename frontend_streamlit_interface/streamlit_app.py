import os
import json
import time
from typing import List, Dict, Any, Optional

import requests
import streamlit as st

# PUBLIC_INTERFACE
def get_backend_base_url() -> str:
    """Get the backend base URL from environment variables or fallback.

    Priority:
    1. FRONTEND_BACKEND_BASE_URL environment variable
    2. If running in Codespaces/preview, orchestrator may set it automatically.
    3. Default to http://localhost:8000

    Returns:
        str: Base URL for backend FastAPI.
    """
    # Note for orchestrator: Please set FRONTEND_BACKEND_BASE_URL in .env
    return os.getenv("FRONTEND_BACKEND_BASE_URL", "http://localhost:8000")


def _http_get(path: str, timeout: int = 20) -> requests.Response:
    base = get_backend_base_url().rstrip("/")
    url = f"{base}/{path.lstrip('/')}"
    return requests.get(url, timeout=timeout)


def _http_post(path: str, json_body: dict, timeout: int = 60) -> requests.Response:
    base = get_backend_base_url().rstrip("/")
    url = f"{base}/{path.lstrip('/')}"
    headers = {"Content-Type": "application/json"}
    return requests.post(url, json=json_body, headers=headers, timeout=timeout)


# PUBLIC_INTERFACE
def discover_api() -> Dict[str, Any]:
    """Fetch backend openapi.json to discover available endpoints."""
    try:
        resp = _http_get("openapi.json", timeout=20)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.sidebar.error(f"Failed to load backend OpenAPI spec: {e}")
        return {}


# PUBLIC_INTERFACE
def fetch_agents(api: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return list of agents using a conventional endpoint if available.

    This function tries to detect an agent list endpoint via OpenAPI.
    Fallbacks:
      - GET /agents
      - GET /api/agents
    """
    candidates = ["/agents", "/api/agents"]
    # Probe paths from OpenAPI if provided
    try:
        paths = api.get("paths", {}) if isinstance(api, dict) else {}
        for p in paths.keys():
            if "agent" in p.lower() and "get" in paths[p]:
                if p not in candidates:
                    candidates.insert(0, p)
    except Exception:
        pass

    for path in candidates:
        try:
            r = _http_get(path, timeout=20)
            if r.status_code == 200:
                data = r.json()
                # Expect list or dict with 'agents'
                if isinstance(data, list):
                    return data
                if isinstance(data, dict):
                    if "agents" in data and isinstance(data["agents"], list):
                        return data["agents"]
            # Continue to next candidate
        except Exception:
            continue
    return []


# PUBLIC_INTERFACE
def submit_query(agent_id: Optional[str], query: str) -> Dict[str, Any]:
    """Submit a query to the backend.

    Tries conventional endpoints:
      - POST /query {agent_id, query}
      - POST /api/query
      - POST /agents/{agent_id}/query {query}
    """
    payload = {"query": query}
    if agent_id:
        payload["agent_id"] = agent_id

    # Try common POST endpoints
    post_candidates = ["/query", "/api/query"]
    for path in post_candidates:
        try:
            r = _http_post(path, payload, timeout=120)
            if r.status_code in (200, 201):
                return r.json()
        except Exception:
            pass

    # Try agent-scoped endpoint
    if agent_id:
        scoped_candidates = [f"/agents/{agent_id}/query", f"/api/agents/{agent_id}/query"]
        for path in scoped_candidates:
            try:
                r = _http_post(path, {"query": query}, timeout=120)
                if r.status_code in (200, 201):
                    return r.json()
            except Exception:
                pass

    return {"error": "Unable to submit query to backend. Please verify API endpoints."}


# PUBLIC_INTERFACE
def fetch_history(agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch interaction history.

    Tries:
      - GET /history
      - GET /api/history
      - GET /agents/{agent_id}/history
    """
    get_candidates = ["/history", "/api/history"]
    for path in get_candidates:
        try:
            r = _http_get(path, timeout=30)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list):
                    return data
                if isinstance(data, dict) and "history" in data and isinstance(data["history"], list):
                    return data["history"]
        except Exception:
            pass

    if agent_id:
        scoped_candidates = [f"/agents/{agent_id}/history", f"/api/agents/{agent_id}/history"]
        for path in scoped_candidates:
            try:
                r = _http_get(path, timeout=30)
                if r.status_code == 200:
                    data = r.json()
                    if isinstance(data, list):
                        return data
                    if isinstance(data, dict) and "history" in data and isinstance(data["history"], list):
                        return data["history"]
            except Exception:
                pass

    return []


def _apply_ocean_theme():
    """Apply Ocean Professional theme via Streamlit config and custom CSS."""
    st.set_page_config(
        page_title="Agent Query UI",
        page_icon="🌊",
        layout="wide",
    )
    # Ocean Professional theme palette
    primary = "#1E3A8A"
    secondary = "#F59E0B"
    success = "#059669"
    error = "#DC2626"
    background = "#F3F4F6"
    surface = "#FFFFFF"
    text = "#111827"

    st.markdown(
        f"""
        <style>
            :root {{
                --primary: {primary};
                --secondary: {secondary};
                --success: {success};
                --error: {error};
                --bg: {background};
                --surface: {surface};
                --text: {text};
                --muted: #6B7280;
                --border: #E5E7EB;
            }}
            .ocean-card {{
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 16px 18px;
                box-shadow: 0 4px 14px rgba(30, 58, 138, 0.06);
            }}
            .ocean-header {{
                font-weight: 700;
                color: var(--text);
                margin: 0 0 8px 0;
            }}
            .ocean-subtle {{
                color: var(--muted);
                font-size: 0.9rem;
                margin-top: -6px;
            }}
            .ocean-accent {{
                color: var(--primary);
                font-weight: 600;
            }}
            .block-container {{
                padding-top: 2rem;
                padding-bottom: 2rem;
            }}
            .ocean-badge {{
                display: inline-block;
                padding: 2px 10px;
                border-radius: 999px;
                background: rgba(30, 58, 138, 0.08);
                color: var(--primary);
                font-weight: 600;
                font-size: 12px;
                border: 1px solid rgba(30, 58, 138, 0.15);
            }}
            .ocean-divider {{
                height: 1px;
                background: var(--border);
                margin: 8px 0 14px 0;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _init_session_state():
    if "selected_agent_id" not in st.session_state:
        st.session_state.selected_agent_id = None
    if "history" not in st.session_state:
        st.session_state.history = []
    if "api_discovery" not in st.session_state:
        st.session_state.api_discovery = {}
    if "agents" not in st.session_state:
        st.session_state.agents = []


def _sidebar_ui():
    st.sidebar.markdown("### 🌊 Agent Query Console")
    st.sidebar.caption("Ocean Professional • Classic layout")

    base_url = get_backend_base_url()
    st.sidebar.write(f"Backend: {base_url}")

    if st.sidebar.button("Refresh API & Agents", type="secondary"):
        st.session_state.api_discovery = discover_api()
        st.session_state.agents = fetch_agents(st.session_state.api_discovery)
        st.toast("Refreshed backend metadata", icon="✅")

    # Agent selection
    agents = st.session_state.get("agents", [])
    agent_names = []
    id_by_label = {}
    for a in agents:
        # Accept dicts with id/name keys; fallback to str
        if isinstance(a, dict):
            label = a.get("name") or a.get("id") or a.get("label") or json.dumps(a)
            aid = a.get("id") or a.get("agent_id") or a.get("name")
        else:
            label = str(a)
            aid = str(a)
        agent_names.append(label)
        id_by_label[label] = aid

    if agent_names:
        selected_label = st.sidebar.selectbox("Select Agent", ["(None)"] + agent_names, index=0)
        st.session_state.selected_agent_id = id_by_label.get(selected_label) if selected_label != "(None)" else None
    else:
        st.sidebar.info("No agents discovered. You can still try querying the default endpoint.")

    with st.sidebar.expander("OpenAPI (read-only)", expanded=False):
        st.json(st.session_state.get("api_discovery", {}), expanded=False)

    st.sidebar.markdown("---")
    st.sidebar.markdown("#### History")
    if st.sidebar.button("Load History", type="secondary"):
        st.session_state.history = fetch_history(st.session_state.selected_agent_id)

    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history[-10:]), start=1):
            with st.sidebar:
                st.markdown(f"- {item.get('query')[:40]}{'...' if len(item.get('query',''))>40 else ''}")
    else:
        st.sidebar.caption("No history loaded yet.")


def _main_panel():
    st.markdown("## 🧠 LLM Query")
    st.caption("Submit a prompt to the selected agent and view responses. Applies Ocean Professional styling.")

    with st.container():
        with st.form(key="query_form", clear_on_submit=False):
            col1, col2 = st.columns([3, 1])
            with col1:
                query = st.text_area(
                    "Your prompt",
                    placeholder="Ask a question, provide instructions, or describe a task...",
                    height=150,
                )
            with col2:
                st.write("")
                st.write("")
                st.markdown('<span class="ocean-badge">Agent</span>', unsafe_allow_html=True)
                st.write(st.session_state.selected_agent_id or "Default")

            submitted = st.form_submit_button("Submit", use_container_width=True, type="primary")
            if submitted:
                if not query or not query.strip():
                    st.error("Please enter a query.")
                else:
                    with st.spinner("Contacting backend..."):
                        start = time.time()
                        resp = submit_query(st.session_state.selected_agent_id, query.strip())
                        latency = time.time() - start

                    # Add to history in-session as well
                    st.session_state.history.append({
                        "agent_id": st.session_state.selected_agent_id,
                        "query": query.strip(),
                        "response": resp,
                        "timestamp": time.time(),
                        "latency": latency,
                    })

                    if "error" in resp:
                        st.error(resp.get("error"))
                    else:
                        st.success(f"Response received in {latency:.2f}s")
                        _render_response(resp)

    st.markdown("### Recent Interactions")
    if not st.session_state.history:
        st.info("No interactions yet. Submit a query to see responses here.")
    else:
        for item in reversed(st.session_state.history[-5:]):
            with st.container():
                st.markdown('<div class="ocean-card">', unsafe_allow_html=True)
                st.markdown(f"<div class='ocean-header'>Query</div>", unsafe_allow_html=True)
                st.write(item.get("query"))
                st.markdown("<div class='ocean-divider'></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='ocean-header'>Response</div>", unsafe_allow_html=True)
                _render_response(item.get("response", {}))
                st.caption(f"Agent: {item.get('agent_id') or 'Default'} • {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item.get('timestamp', time.time())))} • {item.get('latency', 0):.2f}s")
                st.markdown('</div>', unsafe_allow_html=True)


def _render_response(resp: Any):
    """Render backend response heuristically."""
    if resp is None:
        st.warning("Empty response.")
        return
    # Try to detect structured content
    if isinstance(resp, dict):
        # Common keys: 'answer', 'response', 'output', 'result', 'content'
        text = None
        for k in ("answer", "response", "output", "result", "content", "text"):
            if k in resp and isinstance(resp[k], str):
                text = resp[k]
                break
        if text:
            st.markdown('<div class="ocean-card">', unsafe_allow_html=True)
            st.markdown(text)
            st.markdown('</div>', unsafe_allow_html=True)
        # Show any citations/references if present
        refs = resp.get("references") or resp.get("citations") or resp.get("sources")
        if isinstance(refs, list) and refs:
            st.markdown("##### References")
            for r in refs:
                if isinstance(r, dict):
                    label = r.get("title") or r.get("id") or "Source"
                    url = r.get("url")
                    if url:
                        st.markdown(f"- [{label}]({url})")
                    else:
                        st.markdown(f"- {json.dumps(r, indent=2)}")
                else:
                    st.markdown(f"- {str(r)}")
        # Fallback to raw JSON
        with st.expander("Raw JSON"):
            st.json(resp)
    elif isinstance(resp, list):
        for i, it in enumerate(resp, start=1):
            st.markdown(f"**Item {i}**")
            _render_response(it)
    else:
        st.write(str(resp))


def _footer():
    st.markdown("---")
    st.caption("Ocean Professional • Streamlit UI for Bedrock Agent Querying")


def main():
    _apply_ocean_theme()
    _init_session_state()

    # Display requested developer message prominently
    st.info("Edit src/App.js and save to reload.")

    # First-time discovery
    if not st.session_state.api_discovery:
        st.session_state.api_discovery = discover_api()
    if not st.session_state.agents:
        st.session_state.agents = fetch_agents(st.session_state.api_discovery)

    # Subtle badge below the info note for emphasis (non-intrusive)
    st.markdown('<span class="ocean-badge">Developer Tip</span>', unsafe_allow_html=True)

    _sidebar_ui()
    _main_panel()
    _footer()


if __name__ == "__main__":
    main()
"""
