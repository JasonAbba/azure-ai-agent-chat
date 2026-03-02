import os
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

print("Authenticating...")
credential = ClientSecretCredential(
    tenant_id=os.getenv("TENANT_ID"),
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET")
)

project_client = AIProjectClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=credential
)

print("Fetching all agents in your project...\n")

try:
    # In the new AgentsOperations class, the method is .list()
    agents = project_client.agents.list_agents()
    
    # Handle pagination
    agent_list = agents.data if hasattr(agents, 'data') else agents
    
    for agent in agent_list:
        name = getattr(agent, 'name', 'No Name')
        print(f"🤖 Agent Name: {name}")
        print(f"🔑 AGENT_ID:   {agent.id}")
        print("-" * 40)
        
except Exception as e:
    print(f"❌ Error fetching agents: {e}")