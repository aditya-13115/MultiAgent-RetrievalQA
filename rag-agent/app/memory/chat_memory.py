from typing import List, Dict


class ChatMemory:
    def __init__(self, max_history: int = 5):
        self.history: List[Dict[str, str]] = []
        self.max_history = max_history

    def add_interaction(self, user_query: str, agent_response: str):
        self.history.append({"role": "user", "content": user_query})
        self.history.append({"role": "assistant", "content": agent_response})

        if len(self.history) > self.max_history * 2:
            self.history = self.history[-(self.max_history * 2) :]

    def get_history_string(self) -> str:
        if not self.history:
            return "No previous conversation history."

        history_str = ""
        for msg in self.history:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_str += f"{role}: {msg['content']}\n"
        return history_str.strip()

    def clear(self):
        self.history = []
