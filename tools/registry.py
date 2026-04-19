class Tool:
    def __init__(self, name, func, description, parameters):
        self.name = name
        self.function = func
        self.description = description
        self.parameters = parameters


TOOLS = []


def get_tool_by_name(name: str):
    for tool in TOOLS:
        if tool.name == name:
            return tool
        return None


def get_tool_schemas():
    """Format tools for LLM prompt"""
    schemas = []

    for tool in TOOLS:
        schemas.append(
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            }
        )

    return schemas
