import json
import os

PROJECT_NAME = "JEEMind"
FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "agents", "common", "agents_config.json"
)
print(f"Using agents configuration file: {FILE_PATH}")

def read_agents_json_file() -> dict:
    file_path = FILE_PATH
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file {file_path}.")
        return {}

def get_all_agent_name_as_list() -> list:
    config = read_agents_json_file()
    if not isinstance(config, dict):
        print("Invalid configuration format. Expected a dictionary.")
        return []
    
    agent_names = []
    for agent in config.get("agents", []):
        if "role" in agent:
            agent_names.append(agent["role"])
    
    return agent_names


def get_agent_config_by_role(role :str) -> dict:
    config = read_agents_json_file()
    if not isinstance(config, dict):
        print("Invalid configuration format. Expected a dictionary.")
        return {}
    
    for agent in config.get("agents", []):
        if agent.get("role") == role:
            return agent
    
    print(f"No agent found with role: {role}")
    return {}

if __name__ == "__main__":
    print(read_agents_json_file())
    print(get_all_agent_name_as_list())
    print(get_agent_config_by_role("Bariatrician"))