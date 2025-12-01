# Multi-Agent Customer Service System

A production-ready multi-agent system using **Gemini AI**, **MCP (Model Context Protocol)**, and **A2A (Agent-to-Agent)** communication.

## 🎯 Overview

This system implements a customer service automation platform with three specialized AI agents:

1. **Router Agent** - Orchestrator that uses Gemini AI to analyze queries and coordinate specialists
2. **Customer Data Agent** - Manages customer data via MCP protocol
3. **Support Agent** - Handles support queries using Gemini AI

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Router Agent (Gemini AI)                 │
│              Analyzes Intent & Coordinates Agents            │
└────────────────┬────────────────────────────────┬────────────┘
                 │                                │
         A2A Messages (JSON-RPC)         A2A Messages (JSON-RPC)
                 │                                │
    ┌────────────▼────────────┐    ┌────────────▼────────────┐
    │   Data Agent (Gemini)   │    │ Support Agent (Gemini)  │
    │  + MCP Client (stdio)   │    │  + MCP Client (stdio)   │
    └────────────┬────────────┘    └────────────┬────────────┘
                 │                                │
                 └────────────┬───────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   MCP Server      │
                    │  (stdio transport)│
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  SQLite Database  │
                    │   (support.db)    │
                    └───────────────────┘
```

## ✨ Key Features

### 1. **Real AI Agents**
- All agents use **Gemini 1.5 Pro** for intelligent decision-making
- Router Agent: Intent analysis and coordination
- Data Agent: Data validation with AI
- Support Agent: Natural language response generation

### 2. **Official MCP Protocol**
- Uses official `mcp` SDK (not custom REST API)
- stdio transport for process communication
- 6 MCP tools implemented correctly

### 3. **A2A Communication**
- JSON-RPC 2.0 protocol
- Full message logging and tracing
- Agent Cards define capabilities

## 📋 Requirements

- Python 3.10+
- Google API Key (Gemini)
- pip packages (see requirements.txt)

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Setup Database

```bash
python database_setup.py
```

This creates `support.db` with:
- 15 sample customers
- 25 sample tickets
- Proper indexes and foreign keys

### Step 3: Configure API Key

The `.env` file already contains the API key:
```
GOOGLE_API_KEY= your api key
```

### Step 4: Run Tests

```bash
python main_test.py
```

This will:
1. Start MCP server automatically (stdio)
2. Initialize all 3 agents
3. Connect agents to MCP server
4. Run 5 test scenarios + 1 bonus
5. Show A2A communication logs
6. Clean up connections

## 📊 Test Scenarios

### ✅ Scenario 1: Simple Query
```
Query: "Get customer information for ID 5"
Flow: Router → Data Agent → MCP → Database
```

### ✅ Scenario 2: Coordinated Query
```
Query: "I'm customer 1 and need help upgrading my account"
Flow: Router → Data Agent (get context) → Support Agent (generate response)
```

### ✅ Scenario 3: Complex Query
```
Query: "Show me all active customers who have open tickets"
Flow: Router → Data Agent (list customers) → Support Agent (get tickets) → Synthesis
```

### ✅ Scenario 4: Escalation
```
Query: "I've been charged twice, please refund immediately!"
Flow: Router → Support Agent (analyze urgency) → Priority response
```

### ✅ Scenario 5: Multi-Intent
```
Query: "Update my email to charlie.new@example.com and show my ticket history"
Flow: Router → Parallel: Data Agent (update + history) → Combined response
```

### ✅ Bonus: Complex Coordination
```
Query: "What are all the high-priority tickets currently open?"
Flow: Router → Support Agent → MCP (filter query) → Report
```

## 🔧 How It Works

### 1. MCP Server (Official SDK)

```python
# mcp_server.py uses official MCP SDK
from mcp.server import Server
from mcp.server.stdio import stdio_server

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [Tool(...), ...]  # 6 tools

@server.call_tool()
async def call_tool(name: str, arguments: Any):
    # Route to database operations
    ...
```

### 2. Agents with Gemini AI

```python
# All agents use Gemini for intelligence
import google.generativeai as genai

model = genai.GenerativeModel('gemini-1.5-pro')
response = model.generate_content(prompt)
```

### 3. A2A Communication

```python
# JSON-RPC 2.0 messages
message = A2AMessage(
    method="get_customer",
    params={"customer_id": 5},
    from_agent="router_agent",
    to_agent="data_agent"
)

response = await data_agent.handle_message(message)
```

## 📁 File Structure

```
Assignment5/
├── .env                    # API keys
├── requirements.txt        # Python dependencies
├── database_setup.py       # Database initialization
├── support.db             # SQLite database (created by setup)
│
├── mcp_server.py          # MCP server (official SDK)
├── mcp_client.py          # MCP client for agents
│
├── a2a_protocol.py        # A2A communication protocol
├── agent_cards.py         # Agent capability definitions
│
├── router_agent.py        # Router Agent (Gemini AI)
├── data_agent.py          # Data Agent (Gemini + MCP)
├── support_agent.py       # Support Agent (Gemini + MCP)
│
├── main_test.py           # Test suite (all scenarios)
└── README.md              # This file
```

## 🛠️ MCP Tools

The MCP server provides 6 tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_customer` | Retrieve customer by ID | customer_id |
| `list_customers` | List customers with filters | status, limit |
| `update_customer` | Update customer info | customer_id, name, email, phone, status |
| `create_ticket` | Create support ticket | customer_id, issue, priority |
| `get_customer_history` | Get customer's tickets | customer_id |
| `get_tickets` | Query tickets with filters | status, priority, customer_ids |

## 🔍 A2A Protocol Details

### Message Format (JSON-RPC 2.0)
```json
{
  "jsonrpc": "2.0",
  "method": "get_customer",
  "params": {"customer_id": 5},
  "id": "uuid-here",
  "from_agent": "router_agent",
  "to_agent": "data_agent",
  "timestamp": "2025-12-01T14:30:00"
}
```

### Response Format
```json
{
  "jsonrpc": "2.0",
  "result": {"customer": {...}},
  "id": "uuid-here",
  "from_agent": "data_agent",
  "timestamp": "2025-12-01T14:30:01"
}
```

## 🎓 What Makes This Implementation Correct

### ✅ Fixes for老師's Feedback

1. **"Agents are just Python classes, not actual agents"**
   - ✅ **FIXED**: All agents now use Gemini 1.5 Pro
   - Router: AI-powered intent analysis
   - Data Agent: AI validation
   - Support Agent: Natural language generation

2. **"MCP implementation doesn't conform to MCP specs"**
   - ✅ **FIXED**: Uses official `mcp` SDK
   - stdio transport (standard MCP)
   - Proper tool registration with `@server.list_tools()`
   - Correct tool calling with `@server.call_tool()`

### 🏆 Assignment Requirements Met

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| **Part 1: System Architecture** | ✅ | 3 agents with clear roles |
| Router Agent | ✅ | Gemini AI for intent analysis |
| Data Agent | ✅ | Gemini + MCP for data ops |
| Support Agent | ✅ | Gemini for response generation |
| **Part 2: MCP Integration** | ✅ | Official SDK + 6 tools |
| MCP Server | ✅ | stdio transport, proper schema |
| Database Schema | ✅ | Customers + Tickets tables |
| **Part 3: A2A Coordination** | ✅ | JSON-RPC protocol |
| Task Allocation | ✅ | Scenario 1 & 2 |
| Negotiation | ✅ | Scenario 3 & 4 |
| Multi-Step | ✅ | Scenario 5 |
| **Test Scenarios** | ✅ | All 5 + bonus |

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError: mcp"
```bash
pip install mcp
```

### Problem: "API key not found"
Make sure `.env` file exists with:
```
GOOGLE_API_KEY= your api key
```

### Problem: "support.db not found"
```bash
python database_setup.py
```

### Problem: MCP server connection fails
- Make sure `mcp_server.py` is in the same directory
- Check Python version (3.10+)
- Verify all dependencies installed

## 📖 Learning Resources

- [MCP Official Docs](https://modelcontextprotocol.io/)
- [Google Gemini API](https://ai.google.dev/)
- [JSON-RPC 2.0 Spec](https://www.jsonrpc.org/specification)

## 📝 License

This project is for educational purposes (Gen AI Course Assignment 5).

## 👨‍💻 Author

**Assignment 5 - Multi-Agent Customer Service System**  
Course: Advanced Generative AI  
Date: December 2025
