from app.services.llm_client import call_llm

SNAPSHOT_PROMPT = """
Jesteś modułem ekstrakcji pamięci długoterminowej.
Zwróć WYŁĄCZNIE JSON zgodny z ustalonym schematem.
"""

def generate_snapshot(history):
    messages = [
        {"role": "system", "content": SNAPSHOT_PROMPT},
        {"role": "user", "content": str(history)}
    ]
    snapshot_json = call_llm(messages)
    return snapshot_json
