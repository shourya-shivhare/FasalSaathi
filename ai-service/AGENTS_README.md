# FasalSaathi AI: Agentic Architecture & Orchestration

This document outlines the architecture of the **FasalSaathi AI Service**, featuring our move to a **Supervisor-Worker** pattern using [LangGraph](https://langchain-ai.github.io/langgraph/).

## 🏗️ The Orchestrator (Supervisor Node)
The **Supervisor** is the brain of the advisor system. It doesn't answer the farmer directly; instead, it acts as an intelligent router and project manager.

- **Technology**: LangChain + Gemini 2.0 Flash.
- **Role**: 
  - Analyzes the farmer's intent (Weather, Market, Pests, or General).
  - Routes the state to the appropriate specialist agent.
  - Decides when a query is fully satisfied (`FINISH`) to trigger final synthesis.
- **Workflow**: 
  `START -> Supervisor -> Specialist Agent -> Synthesizer -> END`

---

## 👨‍🔬 Specialized Agents (Workers)

### 1. Weather Expert (`weather_agent`)
- **Focus**: Local weather conditions and their impact on specific crops.
- **Tools**: `get_weather_summary`
- **Output**: Actionable advice (e.g., "Postpone irrigation as rain is expected in 2 hours in Pune").

### 2. Market Expert (`market_agent`)
- **Focus**: Real-time mandi prices and price trends.
- **Tools**: `get_market_price`
- **Output**: Comparative pricing and sell/hold recommendations based on MSP.

### 3. Pest Expert (`pest_agent`)
- **Focus**: Disease diagnosis and treatment.
- **Integration**: Works in tandem with the YOLOv8-powered **Crop Scanning** feature.
- **Output**: Identification of the pest, chemical/organic treatment options, and preventive steps.

---

## 📈 Project Progress & Current State

### ✅ Phase 1: Foundation (Completed)
- [x] Basic Chatbot (Keyword-based).
- [x] User Authentication (FastAPI + JWT).
- [x] SQLite/PostgreSQL Database Integration.

### ✅ Phase 2: Agentic Refactoring (Completed 🚀)
- [x] Migrated from hardcoded routes to a **LangGraph** State Machine.
- [x] Resolved Tool Invocation errors (StructuredTool `.invoke` pattern).
- [x] Multi-agent orchestration for specialized domains.

### 🚧 Phase 3: Advanced Features (In Progress)
- [ ] Real-time AGMARKNET API integration for Market Expert.
- [ ] OpenWeatherMap API real-time feeds.
- [ ] Voice interface for regional languages.
- [ ] Interactive scanning results on the "Scan Crop" page.

---

## 🛠️ Performance & Scalability
- **Self-Healing**: The graph architecture allows individual agents to be upgraded or replaced without breaking the main flow.
- **Context-Aware**: Agents automatically receive the farmer's registered location (State/District) from their profile context.
