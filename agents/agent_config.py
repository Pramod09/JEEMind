from typing import List, Dict
import json

agent_config_path = r'agents\common\agents_config.json'

def load_agents_config(config_file = None) -> List[Dict]:
    if config_file is None:
        config_file = agent_config_path
    with open(config_file) as f:
        return json.load(f)

def agents_as_a_list(config_file = None) -> str:
    agents = load_agents_config(config_file)
    agent_names = [agent['role'] for agent in agents['agents']]
    return agent_names


def fetch_agent_config_by_role(role: str, config_file = None) -> Dict:
    if config_file is None:
        config_file = agent_config_path
    agents = load_agents_config(config_file)
    for agent in agents['agents']:
        if agent['role'] == role:
            return agent
    return None


if __name__ == "__main__":
    print("", agents_as_a_list())



