# Darukaa Earth — AI Environmental Scientist

[![CI](https://github.com/ramm1a4d1h0u/darukaa-environmental-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/ramm1a4d1h0u/darukaa-environmental-ai/actions/workflows/ci.yml)

An AI-powered environmental reasoning and biodiversity recommendation system built for the Darukaa Earth Hackathon.

The system combines structured environmental data, rule-based reasoning, scientific knowledge retrieval (RAG), a recommendation engine, and Gemini-powered report generation.

##  Live Demo

https://darukaa-environmental-ai.onrender.com

##  GitHub

https://github.com/ramm1a4d1h0u/darukaa-environmental-ai

---

##  Problem

Environmental decisions depend on multiple interacting factors such as:

- Soil health
- Water availability
- Climate
- Land use
- Biodiversity

Generic AI systems can provide broad sustainability advice without reasoning about these factors together.

Darukaa Earth AI is designed as an **AI Environmental Scientist**, connecting environmental conditions to targeted interventions and explaining the reasoning behind them.

---

##  How It Works

```text
User Question
      ↓
Environmental Information Extraction
      ↓
Environmental State
      ↓
Risk Detection
      ↓
Multi-Metric Reasoning
      ↓
Scientific Knowledge Retrieval (RAG)
      ↓
Recommendation Engine
      ↓
Gemini Scientific Report
      ↓
Recommendation + Reasoning + Metrics + Time Horizon


---





##  Recommendation Engine

The system generates targeted interventions based on detected environmental risks.

Supported interventions include:

- Cover crops
- Crop rotation
- Crop diversification
- Agroforestry
- Residue management
- Soil moisture conservation
- Pollinator habitat

Each recommendation explains what to do, why it is relevant, affected environmental metrics, and the expected time horizon.

The system also respects user constraints during the conversation. For example, if the user says they do not want to plant trees, tree-based interventions such as agroforestry are excluded.

---

##  Scientific RAG

Scientific environmental knowledge is stored in:

`data/knowledge_base.json`

ChromaDB is used to retrieve relevant knowledge based on the user's environmental conditions and question.

The retrieved knowledge is used to ground the recommendation and report generation process.

---

##  Conversational AI

The system maintains session-level conversational context.

It can remember environmental measurements, crop, land use, region, and user constraints.

It can also ask clarification questions when important information is missing.

The system supports follow-up requests such as:

- Trade-off analysis
- One-year action plans
- Additional environmental recommendations

---

##  Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| LLM | Google Gemini |
| RAG | ChromaDB |
| Frontend | HTML, CSS, JavaScript |
| CI/CD | GitHub Actions |
| Deployment | Render |
| Version Control | Git, GitHub |

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/ramm1a4d1h0u/darukaa-environmental-ai.git
cd darukaa-environmental-ai