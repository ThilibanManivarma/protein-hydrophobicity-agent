# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Check MEMORY.md for project notes and decisions that aren't part of the codebase itself.

## Project Purpose

Educational project demonstrating local agentic AI with tool-use (function calling). A protein hydrophobicity calculator built on Ollama + Llama 3.1 exists in two forms: a terminal REPL and a Streamlit web app.

## Prerequisites

- [Ollama](https://ollama.com/download) installed and running
- `llama3.1` model pulled: `ollama pull llama3.1`

## Running the Project

```bash
# Terminal agent
python agentic_protein_tool_1.py

# Web UI
streamlit run protein_hydrophobicity_app.py

# Install dependencies
pip install -r requirements.txt
```

## Architecture

Both scripts share the same pattern:

1. **Tool definition** — a JSON schema (`tools` list) that tells the LLM about `calculate_hydrophobicity(sequence)`
2. **Python tool** — `calculate_hydrophobicity()` using the Kyte-Doolittle scale; returns a dict with length, total score, average score, classification, and per-residue scores
3. **Agent loop** — iterative `ollama.chat()` calls; when the LLM emits a tool call the loop executes the Python function and feeds the result back; loop exits when the LLM produces a final text response

The two files differ only in presentation layer:

| | `agentic_protein_tool_1.py` | `protein_hydrophobicity_app.py` |
|---|---|---|
| UI | `chat()` REPL (stdin/stdout) | Streamlit chat with session state |
| Agent fn | `run_agent_clean()` → `str` | `run_agent()` → `(str, list[tool_calls])` |
| Tool info | Optional verbose flag | Returned as second value, shown in expandable UI |

## Key Implementation Details

- The LLM model name is hardcoded as `"llama3.1"` in both files — change in one place near the top of each file.
- `calculate_hydrophobicity()` validates each character against the 20-letter Kyte-Doolittle map; unknown residues are reported in the return dict rather than raised as exceptions.
- Ollama must be reachable at `http://localhost:11434` (default); the terminal version has an explicit connection check before starting the REPL.
- To add a new tool: define the Python function, add its JSON schema to the `tools` list, and add an `elif tool_name == "..."` branch inside the agent loop.
