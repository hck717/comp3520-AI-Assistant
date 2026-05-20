import os
import requests
import streamlit as st

# Safely get secrets for Streamlit Cloud, fallback to env var or localhost for local dev
try:
    # Try to get from Streamlit Cloud Secrets first
    N8N_BASE_URL = st.secrets.get("N8N_BASE_URL", os.getenv("N8N_BASE_URL", "http://localhost:5678/webhook"))
except Exception:
    # Fallback if secrets are not available (e.g. local dev without .streamlit/secrets.toml)
    N8N_BASE_URL = os.getenv("N8N_BASE_URL", "http://localhost:5678/webhook")

# Ensure the URL doesn't end with a slash
if N8N_BASE_URL.endswith('/'):
    N8N_BASE_URL = N8N_BASE_URL[:-1]

# If using ngrok, ensure we append /webhook if it's not already there
if "ngrok" in N8N_BASE_URL and not N8N_BASE_URL.endswith('/webhook'):
    N8N_BASE_URL = f"{N8N_BASE_URL}/webhook"

UI_PATH = "chat"           # from Serve UI (GET) node
API_PATH = "chat-response" # from Receive Msg (POST)1 node

st.set_page_config(page_title="n8n Agent UI", page_icon="🤖", layout="centered")

st.title("🤖 n8n AI Agent")

# Add a sidebar to show connection status (helpful for debugging)
with st.sidebar:
    st.subheader("🔌 Connection Info")
    st.markdown(f"**Base URL:** `{N8N_BASE_URL}`")
    st.markdown(f"**Full API URL:** `{N8N_BASE_URL}/{API_PATH}`")
    st.caption("Make sure your n8n docker container and ngrok are running!")
    
    # Add a test connection button
    if st.button("🧪 Test Connection"):
        try:
            test_resp = requests.get(N8N_BASE_URL.replace('/webhook', ''), timeout=5)
            st.success("✅ n8n is reachable!")
        except Exception as e:
            st.error(f"❌ Cannot reach n8n: {e}")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your n8n AI assistant. How can I help you today?"}
    ]

# Display chat messages from history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

def call_n8n_api(message: str) -> str:
    """Call the n8n /chat-response webhook and return the agent's reply."""
    url = f"{N8N_BASE_URL}/{API_PATH}"
    try:
        resp = requests.post(
            url,
            json={"message": message},
            timeout=120,  # Increased timeout for complex queries
        )
        resp.raise_for_status()
        data = resp.json()
        # Your Respond to UI nodes return { "output": "<text>" }
        return data.get("output", "No response defined in n8n.")
    except requests.exceptions.Timeout:
        return "⏱️ Request timed out. The agent might be processing a complex query. Please try again."
    except requests.exceptions.ConnectionError:
        return "🔌 Cannot connect to n8n. Make sure:\n1. Docker containers are running (`docker ps`)\n2. ngrok tunnel is active\n3. Streamlit secrets/env has correct URL"
    except requests.exceptions.HTTPError as e:
        return f"❌ HTTP Error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return f"❌ Error calling n8n: {e}\n\nMake sure your n8n docker container and ngrok tunnel are running, and the URL matches."

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Agent is thinking..."):
            reply = call_n8n_api(user_input)
            st.markdown(reply)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": reply})
    
    # Auto-scroll to bottom (rerun to show new messages)
    st.rerun()
