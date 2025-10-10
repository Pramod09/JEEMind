import uuid
import boto3
from botocore.exceptions import ClientError
from common import utils

def chat_with_bedrock_agent(st, role, user_input, session_id) :
    config = utils.get_agent_config_by_role(role)
    if not config:
        raise ValueError(f"No agent configuration found for role: {role}")

    print("###"*33)
    print("Agent ID - " + config["agent_id"])
    print("Alias ID - " + config["alias_id"])
    print("Region - " + config["region"])
    print("User input - " + user_input)
    print("Session ID - " + session_id)
    
    client = boto3.client(
            service_name = "bedrock-agent-runtime",
            region_name =  config["region"],
        )
    
    response = client.invoke_agent(
        agentId = config["agent_id"],
        agentAliasId = config["alias_id"],
        enableTrace = True,
        sessionId = session_id,
        inputText = user_input,
        streamingConfigurations = { 
        "applyGuardrailInterval" : 20,
        "streamFinalResponse" : False
        }
    )
    
    completion = ""
    for event in response.get("completion"):
        if 'chunk' in event:
            chunk = event["chunk"]
            text = chunk["bytes"].decode()
            completion += text
            if st is None:
                print(text, end="", flush=True)
            st.markdown(text)  # Still update Streamlit UI incrementally if needed
        
    return completion


if __name__ == "__main__":
    user_input = "Hello, how to reduce body fat ?"
    session_id = str(uuid.uuid4())  # Generate a new session ID

    response = chat_with_bedrock_agent(None, "Bariatrician", user_input, session_id)
    print("Response from agent:", response)