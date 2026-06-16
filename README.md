# Protein Hydrophobicity AI Agent

A local agentic AI that calculates and explains protein hydrophobicity using the Kyte-Doolittle scale. The agent runs entirely on your machine via [Ollama](https://ollama.com) — no cloud API, no subscription.

Two interfaces are included:
- `agentic_protein_tool_1.py` — interactive terminal REPL
- `protein_hydrophobicity_app.py` — Streamlit web chat

---

## How It Works

The project demonstrates the **tool-use / function-calling** pattern for local LLMs:

```
User query
    └─► Ollama (llama3.1)
            ├─► [tool call] calculate_hydrophobicity(sequence)
            │       └─► result fed back into conversation
            └─► Final natural-language response
```

The LLM decides when to invoke `calculate_hydrophobicity`, executes it via a Python dispatch loop, and incorporates the result into its reply. This is the same pattern used by ChatGPT plugins and GPT Actions.

---

## Prerequisites

- Python 3.9+
- [Ollama](https://ollama.com/download) installed and running

Pull the required model (≈5 GB download):

```bash
ollama pull llama3.1
```

---

## Installation

```bash
# 1. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
```

---

## Usage

### Terminal agent

```bash
python agentic_protein_tool_1.py
```

```
You: What is the hydrophobicity of MKTAYIAK?
AI:  The sequence MKTAYIAK has an average Kyte-Doolittle score of 1.4, classifying it as hydrophobic.

You: Compare ILVFW and EDNQK
AI:  ...

You: quit
```

Type `quit`, `exit`, or `q` to end the session.

### Streamlit web app

```bash
streamlit run protein_hydrophobicity_app.py
```

Opens a chat interface in your browser. Expandable panels show the raw JSON returned by each tool call. Use the **Clear conversation** button in the sidebar to reset history.

---

## Hydrophobicity Tool

`calculate_hydrophobicity(sequence: str) -> dict`

Uses the Kyte-Doolittle scale across all 20 standard amino acids. Input is case-insensitive.

| Field | Description |
|---|---|
| `sequence` | Uppercase-normalised input |
| `length` | Number of residues |
| `total_hydrophobicity` | Sum of per-residue scores |
| `average_hydrophobicity` | Mean score |
| `classification` | `"hydrophobic"` (avg > 1.0) · `"hydrophilic"` (avg < −1.0) · `"neutral"` |
| `per_residue_scores` | Dict mapping each residue to its score |

Unknown characters return `{"error": "Invalid amino acids: X, ..."}` without raising an exception.

---

## Adding a New Tool

1. Write a Python function that returns a `dict`.
2. Add a JSON schema entry to the `tools` list (follow the existing pattern).
3. Add an `elif function_name == "your_function"` branch inside the agent loop.

The LLM will automatically decide when to call it based on the `description` field in the schema.

---

## Project Structure

```
TUTORIAL/
├── agentic_protein_tool_1.py       # Terminal agent
├── protein_hydrophobicity_app.py   # Streamlit web app
├── requirements.txt
├── CLAUDE.md
├── MEMORY.md
└── README.md
```

---

## Credits

- [Ollama](https://ollama.com) — local LLM runtime
- [Llama 3.1](https://ai.meta.com/llama/) — Meta's open-source model
- [Streamlit](https://streamlit.io) — web interface
