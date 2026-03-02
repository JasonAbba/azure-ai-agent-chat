# Azure AI Foundry Agent Chat

A Streamlit-based web interface for interacting with Azure AI Foundry agents. This project provides a user-friendly chat interface to communicate with your custom AI agents deployed on Azure AI Foundry (formerly Azure AI Studio).

## Setup & Configuration

### Prerequisites

- Python 3.8 or higher
- Azure subscription with AI Foundry project set up
- Service principal credentials (Tenant ID, Client ID, Client Secret)
- An AI agent deployed in your Azure AI Foundry project

### Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd <your-repo-name>
```

2. Install required dependencies:
```bash
pip install streamlit azure-identity azure-ai-projects python-dotenv
```

3. Create a `.env` file in the project root with your Azure credentials:
```env
TENANT_ID=your-tenant-id
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret
PROJECT_ENDPOINT=https://your-project.api.azureml.ms
AGENT_NAME=your-agent-name
```

### Getting Your Configuration Values

- **TENANT_ID, CLIENT_ID, CLIENT_SECRET**: These are your Azure service principal credentials. You can create a service principal in Azure Portal under "App registrations"
- **PROJECT_ENDPOINT**: Found in your Azure AI Foundry project settings
- **AGENT_NAME**: Use the `find_agent_id.py` script to discover available agents in your project

## Usage

### Finding Your Agent

Before running the chat interface, you need to identify which agent you want to use. Run the utility script to list all available agents:

```bash
python find_agent_id.py
```

This will output all agents in your project:
```
🤖 Agent Name: My Custom Agent
🔑 AGENT_ID:   asst_abc123xyz
----------------------------------------
```

Copy the agent name and add it to your `.env` file as `AGENT_NAME`.

### Running the Chat Interface

Launch the Streamlit web application:

```bash
streamlit run webchat.py
```

The chat interface will open in your default browser at `http://localhost:8501`.

### Features

- **Interactive Chat**: Send messages and receive responses from your AI agent
- **Thread Management**: Each chat session maintains conversation context
- **New Chat**: Start fresh conversations with the "New Chat" button
- **Agent Info Sidebar**: View current agent details and thread ID
- **Error Handling**: Clear error messages for troubleshooting

### Chat Interface

- Type your message in the input box at the bottom
- The agent will process your message and respond
- All messages are stored in the conversation thread
- Use the sidebar to start a new conversation or view agent information

## Project Structure

- `webchat.py` - Main Streamlit application for the chat interface
- `find_agent_id.py` - Utility script to list available agents
- `.env` - Configuration file (not tracked in git)
- `README.md` - This file

## Troubleshooting

**Agent not found**: Run `find_agent_id.py` to verify your agent name matches exactly (case-sensitive)

**Authentication errors**: Verify your service principal has appropriate permissions in Azure AI Foundry

**Connection issues**: Check that your `PROJECT_ENDPOINT` is correct and accessible

**No response from agent**: Ensure your agent is properly deployed and active in Azure AI Foundry

## Security Notes

- Never commit your `.env` file to version control
- Keep your service principal credentials secure
- Consider using Azure Key Vault for production deployments
- Rotate credentials regularly
