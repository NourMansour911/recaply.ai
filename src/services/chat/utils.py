from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage

def to_lc_messages(history: List[Dict[str, Any]]):
    msgs = []
    for m in history:
        if m["role"] == "user":
            msgs.append(HumanMessage(content=m["content"]))
        else:
            msgs.append(AIMessage(content=m["content"]))
    return msgs
