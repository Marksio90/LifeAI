from app.agents.prompt import CHAOS_AGENT_PROMPT
from app.services.llm_client import call_llm

def run_chaos_agent(conversation_history: list[str]) -> str:
    messages = [
        {"role": "system", "content": CHAOS_AGENT_PROMPT}
    ]

    for msg in conversation_history:
        messages.append(msg)

    response = call_llm(messages)
    return response
