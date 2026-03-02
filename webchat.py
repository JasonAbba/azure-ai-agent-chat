import os
import streamlit as st
from azure.identity import ClientSecretCredential
from azure.ai.projects import AIProjectClient
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
AGENT_NAME = os.getenv("AGENT_NAME")

def custom_serializer(obj):
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    # If it fails, just return a string so it doesn't crash
    return str(obj)

def raw_thought_printer(message):
    return json.dumps(message, default=custom_serializer, indent=4)


def get_agent(project_client):
    """Get agent by name using the flattened list_agents method"""
    try:
        # Diagnostic confirmed: list_agents is direct
        agents = project_client.agents.list_agents()
        
        # Handle both paginated and direct list returns
        agent_list = agents.data if hasattr(agents, 'data') else agents

        # print("Available agents:", [agent.name for agent in agent_list])
        
        for agent in agent_list:
            if agent.name == AGENT_NAME:
                print(f"Found agent: {agent.name} - ID: {agent.id}")
                return agent
        
        st.error(f"❌ Agent '{AGENT_NAME}' not found")
        st.info("Available agents:")
        for agent in agent_list:
            st.write(f"  • {agent.name} (ID: {agent.id})")
        return None
        
    except Exception as e:
        st.error(f"❌ Error listing agents: {e}")
        return None

def initialize_session():
    """Initialize session state"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'thread_id' not in st.session_state:
        st.session_state.thread_id = None
    
    if 'project_client' not in st.session_state:
        credential = ClientSecretCredential(
            tenant_id=TENANT_ID,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
        
        st.session_state.project_client = AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=credential
        )
        
        st.session_state.agent = get_agent(st.session_state.project_client)
        
        if st.session_state.agent:
            # Diagnostic confirmed: threads is nested
            thread = st.session_state.project_client.agents.threads.create()
            st.session_state.thread_id = thread.id

def send_message(user_message):
    """Send message and get response using the nested structure"""
    client = st.session_state.project_client
    thread_id = st.session_state.thread_id
    agent = st.session_state.agent
    
    if not agent:
        return "❌ Agent not initialized"
    
    try:
        # Diagnostic confirmed: messages is nested
        client.agents.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )
        
        # Diagnostic confirmed: runs is nested
        run = client.agents.runs.create_and_process(
            thread_id=thread_id,
            agent_id=agent.id
        )
        
        if run.status == "failed":
            return f"❌ Run failed: {run.last_error}"
        
        # Diagnostic confirmed: messages is nested
        messages = client.agents.messages.list(thread_id=thread_id)
        message_list = messages.data if hasattr(messages, 'data') else messages

        # Find the latest assistant response for this run
        for message in message_list:
            if getattr(message, 'run_id', None) == run.id and message.role == "assistant":
                print(f"Raw thought: {raw_thought_printer(message)}")
                if hasattr(message, 'text_messages') and message.text_messages:
                    return message.text_messages[-1].text.value
                elif hasattr(message, 'content'):
                    for content_item in message.content:
                        if content_item.type == "text":
                            return content_item.text.value
                            
        return "⚠️ No response from agent"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def main():
    st.set_page_config(page_title="Azure AI Agent Chat", page_icon="🤖", layout="wide")
    st.title("🤖 Azure AI Foundry Agent Chat")
    st.markdown("---")
    
    try:
        initialize_session()
        
        if not st.session_state.agent:
            st.error("❌ Failed to initialize the agent.")
            st.stop()
        
        # Sidebar Info
        with st.sidebar:
            st.header("📊 Agent Info")
            st.write(f"**Name:** {st.session_state.agent.name}")
            st.write(f"**ID:** {st.session_state.agent.id}")
            st.write(f"**Thread:** {st.session_state.thread_id}")
            st.markdown("---")
            
            if st.button("🔄 New Chat"):
                st.session_state.messages = []
                thread = st.session_state.project_client.agents.threads.create()
                st.session_state.thread_id = thread.id
                st.rerun()
        
        # Render existing messages
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # Chat Input
        if prompt := st.chat_input("Message the agent..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                print(f"User: {prompt}")
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = send_message(prompt)
                    st.markdown(response)
                    print(f"Assistant: {response}")
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

    except Exception as e:
        st.error(f"❌ Unhandled Error: {e}")
        with st.expander("Details"):
            st.code(str(e))

if __name__ == "__main__":
    main()