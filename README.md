Here is a comprehensive Project Plan in `README.md` format, incorporating all your specified features, tools, and workflows.

***

# 🧠 AI Personal Operations Center (POC) - "The Second Brain"

## 📖 Overview
This project represents a local-first, privacy-focused **Agentic Operations Center**. It acts as an autonomous assistant capable of handling complex multimodal inputs (Voice, Text), executing secure system operations (SSH), managing personal finance, and proactively organizing daily life through a "Supervisor" agent architecture.

The system is fully containerized using **Docker**, orchestrating **Ollama** (Local LLM), **n8n** (Workflow Automation), and various tool integrations into a unified, observable ecosystem.

***

## 🏗 System Architecture

The following diagram illustrates the flow of data between the User, the Supervisor Agent, and the specialized Sub-Agents/Tools.

```mermaid
graph TD
    %% Users and Interfaces
    User([User]) -->|Voice/Text| Telegram[Telegram Interface]
    User -->|Dashboard Interaction| WebUI[Web Dashboard / Chat UI]
    
    %% Triggers
    Telegram -->|Webhook| n8n_Orch[n8n Orchestrator / Supervisor Agent]
    WebUI -->|API Request| n8n_Orch
    Cron[7:00 AM Schedule] -->|Morning Briefing| n8n_Orch
    
    %% The Brain (AI)
    n8n_Orch <-->|Inference| Ollama[Ollama (Llama 3.2 / DeepSeek)]
    n8n_Orch <-->|Safety Check| Critic[Critic Model / Security Auditor]
    
    %% Memory & Storage
    subgraph "Memory & Context"
        VecDB[(Vector Store)]
        SumMD[Summary.md]
        ExpDB[(Expense DB)]
    end
    n8n_Orch <--> VecDB
    n8n_Orch <--> SumMD
    
    %% Feature Modules (Sub-Agents)
    subgraph "Capabilities"
        %% Voice Pipeline
        subgraph "Voice Loop"
            Whisper[OpenAI Whisper (STT)]
            Kokoro[Kokoro/Coqui (TTS)]
        end
        
        %% Tool Execution
        subgraph "Sensitive Ops"
            SSH[SSH Terminal]
            HumanChk{Human Approval}
        end
        
        %% Data & Docs
        subgraph "Analysis & Docs"
            CodeInt[Python Sandbox / Code Interpreter]
            FileOp[File Operator / PDF Reader]
        end
        
        %% External Tools
        subgraph "External APIs"
            GSuite[Gmail / G-Cal / Docs]
            FinAPI[YFinance / Market Data]
        end
    end
    
    %% Connections
    n8n_Orch --> Whisper
    Whisper --> Ollama
    Ollama --> Kokoro
    Kokoro --> Telegram
    
    n8n_Orch -->|Delegation| CodeInt
    CodeInt -->|Chart Generation| ExpDB
    
    n8n_Orch -->|Draft Command| Critic
    Critic -->|Approved?| HumanChk
    HumanChk -->|Yes| SSH
    
    n8n_Orch --> GSuite
    n8n_Orch --> FinAPI
```

***

## 🛠 Tech Stack

| Component | Technology | Docker Image |
| :--- | :--- | :--- |
| **Orchestration** | n8n | `n8nio/n8n:latest` |
| **LLM Backend** | Ollama (Llama 3.2) | `ollama/ollama:latest` |
| **Speech-to-Text** | Whisper (Local) | `openai/whisper` (or `faster-whisper-server`) |
| **Text-to-Speech** | Kokoro / Coqui TTS | `ghcr.io/coqui-ai/tts` |
| **Database** | PostgreSQL / Vector Store | `postgres:16` / `chromadb` |
| **Code Sandbox** | Python Container | `python:3.11-slim` (with Pandas, Matplotlib) |
| **Frontend UI** | Streamlit / Open WebUI | `streamlit` or `open-webui` |
| **Observability** | LangFuse | `langfuse/langfuse` |

***

## 🚀 Core Features & Workflows

### 1. 🎙️ Multimodal Voice Interface ("Walk & Talk")
**Goal:** Hands-free interaction while walking.
*   **Workflow:**
    1.  **Input:** User sends Voice Note via Telegram.
    2.  **Transcribe:** n8n Webhook receives audio $\to$ sends to **Whisper Container**.
    3.  **Think:** Transcribed text $\to$ **Ollama** (Llama 3.2) for processing.
    4.  **Speak:** LLM response $\to$ **Kokoro TTS** $\to$ Audio File.
    5.  **Output:** n8n sends Audio File back to Telegram as a reply.

### 2. 👮 Supervisor & Sub-Agents Pattern
**Goal:** Break down complex tasks into atomic actions.
*   **Supervisor Agent:** Analyzes intent and routes to specific workers.
    *   **Worker A (Search):** RAG search over emails/docs.
    *   **Worker B (Analyst):** Uses "Code Interpreter" to analyze data.
    *   **Worker C (Writer):** Formats final output (PDF/Markdown).

### 3. 🛡️ Secure SSH & Human-in-the-Loop
**Goal:** Execute terminal commands safely without accidental destruction.
*   **Security Layer:**
    1.  **Draft:** Agent proposes `rm -rf /logs`.
    2.  **Critic Audit:** A separate "Critic" model prompt: *"User wants to run `rm -rf /logs`. Is this safe? Respond YES/NO."*
    3.  **Human Gate:** If Critic is unsure or command is high-risk $\to$ Send Telegram Button: **[Approve] / [Deny]**.
    4.  **Execution:** Only runs upon explicit click.

### 4. 🧠 Long-Term Memory (Context Preservation)
**Goal:** Continuity across sessions.
*   **Session Start:** Workflow reads `Summary.md` (high-level user profile) before processing the first query.
*   **Session End (Batch):** Every 10 turns, a background job summarizes the interaction and updates `user_profiles` in the Vector Store.
*   **Recall:** Uses semantic search to retrieve "User preferences for Python projects" when relevant.

### 5. 💰 Expenditure Tracking & Visualization
**Goal:** Frictionless expense logging with visual insights.
*   **Input:** User texts: *"Spent $50 on lunch."*
*   **Extraction:** Agent extracts `{"amount": 50, "category": "Food", "date": "2025-01-27"}`.
*   **Storage:** Appends to SQL Database or Google Sheet.
*   **Visualization:**
    *   **Trigger:** User asks *"Show my monthly spending."*
    *   **Action:** Python Sandbox queries DB $\to$ Generates Pie Chart (`matplotlib`) $\to$ Saves image.
    *   **Output:** Image sent to Chat UI / Telegram.

### 6. 🌅 "Morning Analyst" Briefing
**Goal:** Executive summary delivered at 7:00 AM.
*   **Trigger:** Cron Schedule (07:00).
*   **Data Sources:**
    *   **Calendar:** Fetch today's events.
    *   **Gmail:** Filter for "Urgent" or domain `*@hsbc.com` received overnight.
    *   **Markets:** Python script calls `yfinance` (S&P 500 close, HKD/USD).
*   **Synthesis:** Agent generates a structured briefing with "Action Items".

***

## 📂 Folder Structure

```text
/ai-poc-project
├── docker-compose.yml       # Orchestrates n8n, ollama, whisper, db
├── .env                     # API Keys (Telegram, Google, OpenAI if needed)
├── /n8n_workflows           # JSON exports of n8n flows
│   ├── supervisor_agent.json
│   ├── voice_pipeline.json
│   └── morning_briefing.json
├── /python_sandbox          # Scripts for code interpreter
│   ├── market_data.py
│   └── generate_chart.py
├── /memory                  # Local storage for context
│   ├── summary.md
│   └── vector_store/
└── /data                    # Persistent volume data
```

***

## 🗓 Implementation Roadmap

### Phase 1: Foundation (Days 1-2)
- [ ] Set up `docker-compose.yml` with Ollama, n8n, and PostgreSQL.
- [ ] Connect Telegram Bot API to n8n Webhook.
- [ ] Verify Ollama is running `llama3.2` locally.

### Phase 2: The Brain & Tools (Days 3-5)
- [ ] Build the **Supervisor Agent** node in n8n.
- [ ] Integrate **Google Workspace** (Gmail/Calendar/Sheets) credentials.
- [ ] Implement **SSH Tool** with the "Human-in-the-Loop" Telegram button.

### Phase 3: Voice & Multimedia (Days 6-7)
- [ ] Deploy **Whisper** and **TTS** containers.
- [ ] Create the Audio processing workflow (Audio $\to$ Text $\to$ AI $\to$ Audio).

### Phase 4: Memory & Analysis (Days 8-10)
- [ ] Set up the **Expense Database** and Python Chart generation script.
- [ ] Implement the **"Read Summary.md"** logic at start of chat.
- [ ] Configure **LangFuse** for observability.

***

## 🚦 Getting Started

1. **Clone & Setup:**
   ```bash
   git clone https://github.com/yourname/ai-poc.git
   cd ai-poc
   cp .env.example .env
   ```

2. **Launch Stack:**
   ```bash
   docker-compose up -d
   ```

3. **Initialize Models:**
   ```bash
   docker exec -it ollama ollama run llama3.2
   ```

4. **Connect n8n:**
   Open `http://localhost:5678`, import workflows from `/n8n_workflows`, and authenticate Telegram/Google.
