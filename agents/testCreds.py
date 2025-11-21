import boto3

data ={
			"role": "Math",
			"agent_id": "SJKM6KHGSQ",
			"alias_id": "8NTGST8TYP",
			"region_name": "us-east-1"
		}
session = boto3.Session(profile_name="default")

client = session.client("bedrock-agent-runtime", region_name="us-east-1")

response = client.invoke_agent(
    agentId="SJKM6KHGSQ",
    agentAliasId="8NTGST8TYP",
    sessionId="test-session",
    inputText="Hello agent!"
)

#print(response)

completion = ""
for event in response.get("completion"):
	if 'chunk' in event:
		chunk = event["chunk"]
		text = chunk["bytes"].decode()
		completion += text
    

print(completion)