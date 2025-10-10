import uuid
import boto3
from botocore.exceptions import ClientError

def chat_with_bedrock_agent(st, agent_id, alias_id, region, user_input, session_id) :
    print("###"*33)
    print("Agent ID - " + agent_id)
    print("Alias ID - " + alias_id)
    print("Region - " + region)
    print("User input - " + user_input)
    print("Session ID - " + session_id)
    
    client = boto3.client(
            service_name = "bedrock-agent-runtime",
            region_name =  region,
        )
    
    response = client.invoke_agent(
        agentId = agent_id,
        agentAliasId = alias_id,
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
            #print(text, end="", flush=True)  # Print each chunk as soon as it's received
            st.markdown(text)  # Still update Streamlit UI incrementally if needed
        
    return completion


if __name__ == "__main__":
    # Example usage
    st = None  # Replace with actual Streamlit instance if needed
    agent_id = "example_agent_id"
    alias_id = "example_alias_id"
    region = "us-west-2"
    user_input = "Hello, how can I help you?"
    session_id = str(uuid.uuid4())  # Generate a new session ID

    response = chat_with_bedrock_agent(st, agent_id, alias_id, region, user_input, session_id)
    print("Response from agent:", response)