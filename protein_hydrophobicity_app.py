import streamlit as st
import json
import ollama
from typing import Dict, Any

# ---------- Page config ----------
st.set_page_config(
    page_title="Protein Hydrophobicity AI",
    page_icon="🧬",
    layout="centered"
)

# ---------- Custom CSS for a polished look ----------
st.markdown("""
<style>
    /* Background and fonts */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #e0e0e0;
    }
    .stChatMessage {
        background-color: rgba(255,255,255,0.08) !important;
        border-radius: 15px !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
    }
    /* User message bubble */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background-color: rgba(46, 204, 113, 0.2) !important;
        border-left: 4px solid #2ecc71 !important;
    }
    /* Assistant message bubble */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
        background-color: rgba(52, 152, 219, 0.2) !important;
        border-left: 4px solid #3498db !important;
    }
    /* Input box */
    .stChatInput textarea {
        background-color: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: #e0e0e0 !important;
    }
    .stChatInput textarea::placeholder {
        color: #b0b0b0 !important;
    }
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(0,0,0,0.3) !important;
    }
    .stButton button {
        background-color: #3498db;
        color: white;
        border-radius: 10px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton button:hover {
        background-color: #2980b9;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# ---------- Hydrophobicity calculation function ----------
def calculate_hydrophobicity(sequence: str) -> Dict[str, Any]:
    """Calculate protein hydrophobicity using Kyte-Doolittle scale"""
    
    hydrophobicity_scale = {
        'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5,
        'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
        'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6,
        'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2
    }
    
    sequence = sequence.upper()
    
    if not all(aa in hydrophobicity_scale for aa in sequence):
        invalid = [char for char in sequence if char not in hydrophobicity_scale]
        return {"error": f"Invalid amino acids: {', '.join(set(invalid))}"}
    
    scores = [hydrophobicity_scale[aa] for aa in sequence]
    avg_score = sum(scores) / len(scores)
    
    classification = "hydrophobic" if avg_score > 1.0 else "hydrophilic" if avg_score < -1.0 else "neutral"
    
    return {
        "sequence": sequence,
        "length": len(sequence),
        "total_hydrophobicity": round(sum(scores), 2),
        "average_hydrophobicity": round(avg_score, 2),
        "classification": classification,
        "per_residue_scores": {sequence[i]: scores[i] for i in range(len(sequence))}
    }


# ---------- Tool definition ----------
tools = [{
    'type': 'function',
    'function': {
        'name': 'calculate_hydrophobicity',
        'description': 'Calculate protein hydrophobicity using Kyte-Doolittle scale. Returns scores and classification (hydrophobic/hydrophilic/neutral).',
        'parameters': {
            'type': 'object',
            'properties': {
                'sequence': {
                    'type': 'string',
                    'description': 'Protein sequence in single-letter amino acid code (e.g., "MKTAYIAK")'
                }
            },
            'required': ['sequence']
        }
    }
}]

# ---------- Agent function (adapted for streamlit) ----------
def run_agent(user_query: str, model: str = 'llama3.1') -> str:
    """
    Runs the agentic loop, returns final answer.
    We collect tool calls to optionally display them.
    """
    messages = [{'role': 'user', 'content': user_query}]
    tool_calls_made = []
    
    while True:
        response = ollama.chat(model=model, messages=messages, tools=tools)
        messages.append(response['message'])
        
        if response['message'].get('tool_calls'):
            for tool_call in response['message']['tool_calls']:
                function_name = tool_call['function']['name']
                arguments = tool_call['function']['arguments']
                
                if function_name == 'calculate_hydrophobicity':
                    result = calculate_hydrophobicity(**arguments)
                else:
                    result = {"error": f"Unknown function: {function_name}"}
                
                # Store for display later
                tool_calls_made.append({
                    "function_name": function_name,
                    "arguments": arguments,
                    "result": result
                })
                
                messages.append({'role': 'tool', 'content': json.dumps(result)})
        else:
            return response['message']['content'], tool_calls_made

# ---------- Session State Initialization ----------
if "messages" not in st.session_state:
    st.session_state.messages = []   # list of dicts: {"role": "user"/"assistant", "content": "...", "tool_info": optional}

# ---------- Sidebar ----------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/dna-helix.png", width=80)
    st.title("🧬 Protein Hydrophobicity AI")
    st.markdown("""
    **Powered by:**  
    - Local LLM (Ollama)  
    - Kyte‑Doolittle scale  

    **Ask me things like:**  
    - *"What is the hydrophobicity of MKTAYIAK?"*  
    - *"Is ARNDCEQGH hydrophobic?"*  
    - *"Compare ILVFW and EDNQK"*  
    - *"Explain what hydrophobicity means"*  
    """)
    
    st.divider()
    st.caption("Model: `llama3.1` (change in code if needed)")
    
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------- Main Chat Interface ----------
st.title("🧪 Hydrophobicity Agent Chat")
st.caption("Ask me anything about protein hydrophobicity — I can calculate and explain.")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # Show tool details if any
        if msg.get("tool_info"):
            with st.expander("🔍 View calculation details"):
                for tool in msg["tool_info"]:
                    st.json(tool)

# Chat input
if prompt := st.chat_input("Ask your question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Run agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer, tool_calls = run_agent(prompt)
        st.markdown(answer)
        
        # Show tool calls if any were made
        if tool_calls:
            with st.expander("🔍 Calculation details"):
                for tool in tool_calls:
                    st.json(tool)
    
    # Store assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "tool_info": tool_calls if tool_calls else None
    })