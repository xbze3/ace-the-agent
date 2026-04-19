class AgentState:
    def __init__(self):
        self.messages = []

    def add_user_message(self, content):
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content):
        self.messages.append({"role": "assistant", "content": content})

    def add_tool_result(self, result):
        self.messages.append({"role": "user", "content": f"Tool result: {result}"})

    def get_messages(self):
        return self.messages
