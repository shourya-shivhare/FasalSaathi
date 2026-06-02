# Memory Architecture and State Checkpointing

FasalSaathi features a dual-layered memory model designed to maintain context across individual conversation turns and persist agricultural diagnostic records (crops grown, past pests, matched schemes) for years.

This document describes the memory structures, SQLite schemas, node implementations, and context-retrieval mechanisms.

---

## The Dual-Layer Memory Model

```mermaid
graph TD
    subgraph Conversation Thread Memory (Short-Term)
        A[LangGraph SQLite Saver] -->|Loads Thread ID| B(FasalSaathiState History)
        B -->|Saves state snapshot per node| A
    end
    subgraph Farmer Profile Memory (Long-Term)
        C[SQLiteMemoryStore] -->|retrieve| D[memory_retrieve_node]
        E[memory_persist_node] -->|persist| C
    end
    D -->|Populates state.memory_context| B
    B -->|Provides recommendations| E
```

---

## 1. Short-Term Conversation Memory (Checkpointing)

For conversational multi-turn capability, FasalSaathi uses LangGraph's native checkpointing system:
- **Checkpointer**: [SqliteSaver](file:///e:/Desktop/Web%20Development/FasalSaathi/ai-service/app/graph/checkpoints.py) is instantiated with the database file `graph_checkpoints.db`.
- **Functionality**: Saves the entire state dictionary (`FasalSaathiState`) at every checkpoint (node transition). When a client calls `/api/chat` with a specific `thread_id`, the checkpointer automatically loads the exact state snapshot.
- **Interrupt / Resume**: Essential for image uploads and human intervention. By persisting state, a farmer's session can be suspended mid-execution, prompt for an upload or support review, and resume without losing previous analysis data.

---

## 2. Long-Term Farmer Memory (Relational Store)

Long-term memories are managed by the [SQLiteMemoryStore](file:///e:/Desktop/Web%20Development/FasalSaathi/ai-service/app/memory/store.py) class, which writes records to `ai_memory.db`.

### Database Schema

```sql
CREATE TABLE IF NOT EXISTS farmer_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    category TEXT NOT NULL,
    data TEXT NOT NULL,          -- JSON serialized payload
    session_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fm_user ON farmer_memory(user_id);
CREATE INDEX IF NOT EXISTS idx_fm_cat ON farmer_memory(user_id, category);
CREATE INDEX IF NOT EXISTS idx_fm_time ON farmer_memory(user_id, created_at DESC);
```

### Memory Categories
- `past_crops`: Tracks previously recommended or harvested crops.
- `pest_history`: Stores YOLOv8 pest detection results and severities.
- `scheme_history`: Records eligible government schemes matched to the profile.
- `market_history`: Tracks queried commodity mandi prices and price forecasts.
- `conversation_summaries`: Stores final LLM summaries generated at the end of workflows.

---

## 3. Node Integration

### `memory_retrieve_node`
- **When**: Runs immediately after the graph starts (`START -> memory_retrieve`).
- **Function**: Reads up to $50$ entries for the active `user_id` and groups them by category. The results are injected into the state dictionary as `state["memory_context"]`.

### `memory_persist_node`
- **When**: Runs immediately after a workflow completes and produces a final summary (`summary -> memory_persist`).
- **Function**: Extracts results (such as `crop_recommendations`, `pest_detection_result`, `scheme_recommendations`) from the state and commits them as serialized JSON entries to the SQLite database.

---

## 4. Context Retrieval for Follow-Up Queries

If the intent router classifies the query as a `follow_up` (e.g. *"Tell me more about the third scheme you mentioned"*), execution branches to [context_retrieval_node](file:///e:/Desktop/Web%20Development/FasalSaathi/ai-service/app/nodes/context_retrieval.py):
1. It merges the long-term `memory_context` containing past recommendations with the current thread's active messages.
2. It extracts historical recommendations and synthesizes a prompt enrichment context.
3. It hands this structured prompt back to the `conversational` node, allowing the LLM to speak intelligently about past recommendations without repeating the heavy processing graph nodes.

---

## Code References
- Memory store: [store.py](file:///e:/Desktop/Web%20Development/FasalSaathi/ai-service/app/memory/store.py)
- Memory nodes: [memory_node.py](file:///e:/Desktop/Web%20Development/FasalSaathi/ai-service/app/nodes/memory_node.py)
- Context retrieval node: [context_retrieval.py](file:///e:/Desktop/Web%20Development/FasalSaathi/ai-service/app/nodes/context_retrieval.py)
