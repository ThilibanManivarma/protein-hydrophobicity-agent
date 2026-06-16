"""
Clean Interactive Agentic AI - Minimal Output Version
Perfect for users who want just the answers without technical details
"""

import json
import ollama

# Hydrophobicity calculation function
def calculate_hydrophobicity(sequence: str) -> dict:
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


# Tool definition for LLM
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


# Agent function - CLEAN VERSION (minimal output)
def run_agent_clean(user_query: str, model: str = 'llama3.1', verbose: bool = False):
    """
    Clean agent with minimal output
    
    Args:
        user_query: User's question
        model: Ollama model name
        verbose: If True, shows detailed processing info
    """
    
    messages = [{'role': 'user', 'content': user_query}]
    
    while True:
        response = ollama.chat(model=model, messages=messages, tools=tools)
        messages.append(response['message'])
        
        if response['message'].get('tool_calls'):
            if verbose:
                print("🔧 Using calculation tool...")
            
            for tool_call in response['message']['tool_calls']:
                function_name = tool_call['function']['name']
                arguments = tool_call['function']['arguments']
                
                if function_name == 'calculate_hydrophobicity':
                    result = calculate_hydrophobicity(**arguments)
                else:
                    result = {"error": f"Unknown function: {function_name}"}
                
                if verbose:
                    print(f"   Result: {json.dumps(result, indent=2)}")
                
                messages.append({'role': 'tool', 'content': json.dumps(result)})
        else:
            # Return final answer
            return response['message']['content']


# Interactive mode - CLEAN VERSION
def chat():
    """Simple chat interface"""
    
    print("\n" + "="*70)
    print("          PROTEIN HYDROPHOBICITY AI ASSISTANT")
    print("="*70)
    print("\nAsk me anything about protein hydrophobicity!")
    print("Examples:")
    print("  • What is the hydrophobicity of MKTAYIAK?")
    print("  • Is ARNDCEQGH hydrophobic?")
    print("  • Compare ILVFW versus EDNQK")
    print("\nType 'quit' to exit")
    print("="*70 + "\n")
    
    while True:
        try:
            query = input("You: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! 👋\n")
                break
            
            if not query:
                continue
            
            # Get answer from agent
            print("AI: ", end="", flush=True)
            answer = run_agent_clean(query, verbose=False)
            print(answer + "\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋\n")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    # Quick connection check
    try:
        ollama.list()
        print("✅ Connected to Ollama!\n")
        chat()
    except Exception as e:
        print(f"\n❌ Cannot connect to Ollama: {e}")
        print("Make sure Ollama is running!\n")
        # Try to continue anyway
        try:
            chat()
        except:
            print("Could not start. Please check your Ollama installation.\n")