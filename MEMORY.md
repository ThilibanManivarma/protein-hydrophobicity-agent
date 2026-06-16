# MEMORY.md

Project notes and decisions that aren't derivable from the code or git history.

## Project Context

- This is tutorial project #05 in the `claude_code_pro/claude_tries` series.
- Purpose: teaching agentic AI patterns (tool use / function calling) using a local LLM — no cloud API costs or data privacy concerns.
- Audience: researchers / developers with Python comfort but new to LLM agents.

## Design Decisions

- **Ollama + Llama 3.1** chosen over cloud APIs to keep setup fully local and free.
- Two versions (CLI + Streamlit) are intentionally kept as separate files (not shared library) to make each file self-contained and easy to read in isolation.
- The `calculate_hydrophobicity` function is duplicated between files for the same readability reason.
