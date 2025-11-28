import streamlit as st
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from datetime import datetime
import time
import os
import httpx

st.set_page_config(
    page_title="CrewAI System Debugger",
    page_icon="🔧",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #6366f1;
        color: white;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #f3f4f6;
        color: #1f2937;
        margin-right: 20%;
    }
    .message-role {
        font-weight: bold;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    .message-content h1 {
        color: #1f2937;
        font-size: 2rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #6366f1;
        padding-bottom: 0.5rem;
    }
    .message-content h2 {
        color: #374151;
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    .message-content h3 {
        color: #4b5563;
        font-size: 1.25rem;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .message-content strong {
        color: #1f2937;
        font-weight: 600;
    }
    .message-content code {
        background-color: #f3f4f6;
        color: #dc2626;
        padding: 0.2rem 0.4rem;
        border-radius: 0.25rem;
        font-family: monospace;
        font-size: 0.9em;
    }
    .message-content pre {
        background-color: #1f2937;
        color: #f9fafb;
        padding: 1rem;
        border-radius: 0.5rem;
        overflow-x: auto;
        margin: 1rem 0;
    }
    .message-content pre code {
        background-color: transparent;
        color: #f9fafb;
        padding: 0;
    }
    .message-content ul {
        margin-left: 1.5rem;
        margin-bottom: 1rem;
    }
    .message-content li {
        margin-bottom: 0.5rem;
        line-height: 1.6;
    }
    .assistant-message h1, .assistant-message h2, .assistant-message h3 {
        color: #1f2937;
    }
    .stTextInput > div > div > input {
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'files_uploaded' not in st.session_state:
    st.session_state.files_uploaded = False
if 'files' not in st.session_state:
    st.session_state.files = {}
if 'error_log' not in st.session_state:
    st.session_state.error_log = ''
if 'processing' not in st.session_state:
    st.session_state.processing = False

def build_conversation_context():
    """Build context from uploaded files and error log"""
    context = "Here are the uploaded CrewAI system files:\n\n"
    
    if 'agents' in st.session_state.files:
        context += f"## AGENTS.YAML\n```yaml\n{st.session_state.files['agents']}\n```\n\n"
    if 'tasks' in st.session_state.files:
        context += f"## TASKS.YAML\n```yaml\n{st.session_state.files['tasks']}\n```\n\n"
    if 'tools' in st.session_state.files:
        context += f"## TOOLS.PY\n```python\n{st.session_state.files['tools']}\n```\n\n"
    if 'crew' in st.session_state.files:
        context += f"## CREW.PY\n```python\n{st.session_state.files['crew']}\n```\n\n"
    if 'main' in st.session_state.files:
        context += f"## MAIN.PY\n```python\n{st.session_state.files['main']}\n```\n\n"
    
    if st.session_state.error_log.strip():
        context += f"## ERROR LOG\n```\n{st.session_state.error_log}\n```\n\n"
    
    return context

def send_message(user_message, initial=False):
    """Send message to Claude API with custom HTTP client"""
    max_retries = 3
    retry_delay = 3
    
    for attempt in range(max_retries):
        try:
            system_prompt = """You are an expert CrewAI test engineer with over 15 years of experience in debugging and optimizing multi-agent systems. You are having a conversation with a developer who needs help with their CrewAI implementation.

## Your Role
- Provide conversational, helpful responses
- Answer follow-up questions about the analysis
- Offer clarifications and additional guidance
- Help implement fixes step by step
- Be supportive and encouraging

## Analysis Framework

### 1. AGENTS.YAML VALIDATION
- **Role Definition**: Check if roles are specific, actionable, and not overlapping
- **Goal Clarity**: Verify goals are measurable and aligned with system objectives
- **Backstory Relevance**: Ensure backstories provide context without being verbose
- **LLM Configuration**: Validate model selection and temperature settings
- **Tool Assignment**: Confirm tools are correctly referenced and appropriate for the agent
- **Common Issues**: Vague or duplicate roles, conflicting goals, missing tool references, inappropriate LLM settings

### 2. TASKS.YAML VALIDATION
- **Description Completeness**: Check if task descriptions are clear and actionable
- **Expected Output**: Verify output specifications are detailed and measurable
- **Agent Assignment**: Ensure tasks are assigned to agents with appropriate capabilities
- **Task Dependencies**: Validate task ordering and dependencies
- **Context Usage**: Check if context from previous tasks is properly referenced
- **Common Issues**: Ambiguous descriptions, missing expected_output, incorrect agent assignments, circular dependencies

### 3. TOOLS.PY VALIDATION
- **Import Statements**: Verify all required libraries are imported
- **Tool Definition**: Check @tool decorator usage and function signatures
- **Error Handling**: Ensure robust try-catch blocks and error messages
- **Return Types**: Validate return values match expected formats
- **API Keys/Credentials**: Check for proper environment variable usage

### 4. CREW.PY VALIDATION
- **Agent Instantiation**: Verify agents are correctly loaded from YAML
- **Task Instantiation**: Check tasks are properly loaded with correct parameters
- **Crew Configuration**: Validate process type (sequential/hierarchical)
- **Manager LLM**: If hierarchical, ensure manager_llm is configured

### 5. MAIN.PY VALIDATION
- **Crew Initialization**: Check if crew is properly imported and instantiated
- **Input Handling**: Verify inputs dictionary matches task requirements
- **Execution Method**: Validate kickoff() usage and parameters
- **Output Handling**: Check result processing and error handling
- **Environment Variables**: Ensure API keys are loaded correctly

### 6. ERROR LOG ANALYSIS
- Parse error messages to identify root causes
- Link errors to specific code issues
- Provide targeted solutions for runtime errors
- Explain error propagation and dependencies

## Response Style
- Be conversational and friendly
- Break down complex issues into digestible parts
- Provide code examples when helpful
- Ask clarifying questions when needed
- Acknowledge progress and celebrate fixes"""

            messages = []
            
            # Add context on first message
            if initial:
                full_message = build_conversation_context() + "\n" + user_message
                messages.append({"role": "user", "content": full_message})
            else:
                # Build conversation history
                for msg in st.session_state.conversation_history:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
                messages.append({"role": "user", "content": user_message})

            # Get API key
            api_key = None
            if hasattr(st, 'secrets') and "ANTHROPIC_API_KEY" in st.secrets:
                api_key = st.secrets["ANTHROPIC_API_KEY"]
            elif "ANTHROPIC_API_KEY" in os.environ:
                api_key = os.environ["ANTHROPIC_API_KEY"]
            else:
                st.error("❌ API key not found. Please add ANTHROPIC_API_KEY to your Streamlit secrets.")
                return False
            
            # Create custom HTTP client with longer timeouts and retry configuration
            http_client = httpx.Client(
                timeout=httpx.Timeout(120.0, connect=60.0),
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
                follow_redirects=True,
                verify=True
            )
            
            # Initialize Anthropic client with custom HTTP client
            client = Anthropic(
                api_key=api_key,
                http_client=http_client,
                max_retries=2
            )
            
            # Make API call
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                system=system_prompt,
                messages=messages
            )
            
            assistant_message = message.content[0].text
            
            # Close HTTP client
            http_client.close()
            
            # Add messages to conversation history
            st.session_state.conversation_history.append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now().isoformat()
            })
            st.session_state.conversation_history.append({
                "role": "assistant",
                "content": assistant_message,
                "timestamp": datetime.now().isoformat()
            })
            
            return True
            
        except httpx.ConnectTimeout:
            if attempt < max_retries - 1:
                st.warning(f"⏱️ Connection timeout on attempt {attempt + 1}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            else:
                st.error("❌ Connection Timeout: The request took too long to connect. This might be a Streamlit Cloud network restriction. Please try:\n\n1. Refresh the page and try again\n2. Check if Anthropic API is accessible from your region\n3. Contact Streamlit support about API access restrictions")
                return False
                
        except httpx.ReadTimeout:
            if attempt < max_retries - 1:
                st.warning(f"⏱️ Read timeout on attempt {attempt + 1}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            else:
                st.error("❌ Read Timeout: The API took too long to respond. Your files might be too large. Try:\n\n1. Reducing file sizes\n2. Removing the error log temporarily\n3. Trying again in a moment")
                return False
                
        except httpx.ConnectError as e:
            if attempt < max_retries - 1:
                st.warning(f"🔌 Network error on attempt {attempt + 1}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            else:
                st.error(f"❌ Network Connection Failed: Cannot reach Anthropic API.\n\n**This is likely a Streamlit Cloud limitation.**\n\nWorkarounds:\n1. Deploy on a different platform (Hugging Face Spaces, Render, Railway)\n2. Run locally: `streamlit run streamlit_app.py`\n3. Use a proxy service\n\nTechnical details: {str(e)}")
                return False
        
        except Exception as e:
            error_type = type(e).__name__
            if "Authentication" in error_type or "401" in str(e):
                st.error("❌ Authentication Error: Invalid API key. Please verify your ANTHROPIC_API_KEY in secrets.")
                return False
            elif "RateLimit" in error_type or "429" in str(e):
                st.error("❌ Rate Limit: Too many requests. Please wait a moment and try again.")
                return False
            else:
                if attempt < max_retries - 1:
                    st.warning(f"⚠️ Error on attempt {attempt + 1}: {error_type}. Retrying...")
                    time.sleep(retry_delay)
                    continue
                else:
                    st.error(f"❌ Error: {error_type}: {str(e)}\n\nIf this persists, Streamlit Cloud may be blocking external API calls. Consider running locally or deploying elsewhere.")
                    return False
    
    return False

# Main App Logic
if not st.session_state.files_uploaded:
    # Upload Interface
    st.markdown("<div class='main-header'>", unsafe_allow_html=True)
    st.title("🔧 CrewAI System Debugger")
    st.markdown("**Upload your CrewAI files and error logs for expert analysis**")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Important notice about Streamlit Cloud limitations
    st.info("ℹ️ **Note**: If you experience connection issues, this may be due to Streamlit Cloud network restrictions. Consider running locally with `streamlit run streamlit_app.py` or deploying on alternative platforms like Hugging Face Spaces or Railway.")
    
    st.header("Upload System Files")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("agents.yaml *")
        agents_file = st.file_uploader("Upload agents.yaml", type=['yaml', 'yml'], key="agents")
        
        st.subheader("tasks.yaml *")
        tasks_file = st.file_uploader("Upload tasks.yaml", type=['yaml', 'yml'], key="tasks")
    
    with col2:
        st.subheader("crew.py *")
        crew_file = st.file_uploader("Upload crew.py", type=['py'], key="crew")
        
        st.subheader("main.py *")
        main_file = st.file_uploader("Upload main.py", type=['py'], key="main")
    
    with col3:
        st.subheader("tools.py")
        st.caption("(Optional)")
        tools_file = st.file_uploader("Upload tools.py", type=['py'], key="tools")
    
    st.markdown("---")
    st.header("🐛 Error Log (Optional)")
    st.caption("Paste any error messages, stack traces, or execution issues you're experiencing")
    
    error_log = st.text_area(
        "Error Log",
        height=200,
        placeholder="Paste your error logs here... For example:\n\nTraceback (most recent call last):\n  File 'main.py', line 15, in <module>\n    result = crew.kickoff()\nValueError: Agent 'researcher' not found in tasks.yaml",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption("* Required files")
    with col2:
        if st.button("Start Debugging Session", type="primary", use_container_width=True,
                    disabled=not (agents_file and tasks_file and crew_file and main_file)):
            # Store files in session state
            if agents_file:
                st.session_state.files['agents'] = agents_file.read().decode('utf-8')
            if tasks_file:
                st.session_state.files['tasks'] = tasks_file.read().decode('utf-8')
            if crew_file:
                st.session_state.files['crew'] = crew_file.read().decode('utf-8')
            if main_file:
                st.session_state.files['main'] = main_file.read().decode('utf-8')
            if tools_file:
                st.session_state.files['tools'] = tools_file.read().decode('utf-8')
            
            st.session_state.error_log = error_log
            st.session_state.files_uploaded = True
            st.session_state.processing = True
            st.rerun()

else:
    # Chat Interface
    col1, col2, col3 = st.columns([2, 3, 1])
    
    with col1:
        st.title("🔧 CrewAI Debugger")
    
    with col3:
        if st.button("New Session", use_container_width=True):
            st.session_state.conversation_history = []
            st.session_state.files_uploaded = False
            st.session_state.files = {}
            st.session_state.error_log = ''
            st.session_state.processing = False
            st.rerun()
        
        if len(st.session_state.conversation_history) > 0:
            conversation_text = ""
            for msg in st.session_state.conversation_history:
                role = msg["role"].upper()
                timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
                conversation_text += f"**{role}** ({timestamp}):\n{msg['content']}\n\n---\n\n"
            
            st.download_button(
                label="Export Chat",
                data=conversation_text,
                file_name=f"crewai_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    st.markdown("---")
    
    # Process initial analysis if needed
    if st.session_state.processing and len(st.session_state.conversation_history) == 0:
        with st.spinner("Analyzing your CrewAI system... This may take a moment."):
            success = send_message("Please analyze my CrewAI system and identify any issues.", initial=True)
            if success:
                st.session_state.processing = False
                st.rerun()
            else:
                st.session_state.processing = False
    
    # Display conversation history
    if len(st.session_state.conversation_history) > 0:
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.conversation_history:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <div class="message-role">You • {datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M:%S")}</div>
                        <div class="message-content">{msg["content"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div class="message-role">AI Assistant • {datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M:%S")}</div>
                        <div class="message-content">
                    """, unsafe_allow_html=True)
                    st.markdown(msg["content"], unsafe_allow_html=True)
                    st.markdown("</div></div>", unsafe_allow_html=True)
    else:
        st.info("Waiting for initial analysis...")
    
    # Input area
    st.markdown("---")
    
    # Use form to prevent rerun on input change
    with st.form(key='message_form', clear_on_submit=True):
        user_input = st.text_input(
            "Message",
            placeholder="Ask a question about the analysis, request clarification, or get help implementing fixes...",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns([5, 1])
        with col2:
            send_button = st.form_submit_button("Send", type="primary", use_container_width=True)
    
    if send_button and user_input.strip():
        with st.spinner("Thinking..."):
            send_message(user_input)
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6b7280; padding: 1rem 0;'>"
    "Powered by Claude AI • CrewAI Framework Expert Analysis"
    "</div>",
    unsafe_allow_html=True
)
# import streamlit as st
# import anthropic
# from datetime import datetime
# import time
# import os

# st.set_page_config(
#     page_title="CrewAI System Debugger",
#     page_icon="🔧",
#     layout="wide"
# )

# # Custom CSS
# st.markdown("""
# <style>
#     .main-header {
#         text-align: center;
#         padding: 2rem 0;
#     }
#     .chat-message {
#         padding: 1.5rem;
#         border-radius: 0.5rem;
#         margin-bottom: 1rem;
#         display: flex;
#         flex-direction: column;
#     }
#     .user-message {
#         background-color: #6366f1;
#         color: white;
#         margin-left: 20%;
#     }
#     .assistant-message {
#         background-color: #f3f4f6;
#         color: #1f2937;
#         margin-right: 20%;
#     }
#     .message-role {
#         font-weight: bold;
#         margin-bottom: 0.5rem;
#         font-size: 0.9rem;
#     }
#     .message-content h1 {
#         color: #1f2937;
#         font-size: 2rem;
#         font-weight: bold;
#         margin-top: 2rem;
#         margin-bottom: 1rem;
#         border-bottom: 2px solid #6366f1;
#         padding-bottom: 0.5rem;
#     }
#     .message-content h2 {
#         color: #374151;
#         font-size: 1.5rem;
#         font-weight: bold;
#         margin-top: 1.5rem;
#         margin-bottom: 0.75rem;
#     }
#     .message-content h3 {
#         color: #4b5563;
#         font-size: 1.25rem;
#         font-weight: 600;
#         margin-top: 1rem;
#         margin-bottom: 0.5rem;
#     }
#     .message-content strong {
#         color: #1f2937;
#         font-weight: 600;
#     }
#     .message-content code {
#         background-color: #f3f4f6;
#         color: #dc2626;
#         padding: 0.2rem 0.4rem;
#         border-radius: 0.25rem;
#         font-family: monospace;
#         font-size: 0.9em;
#     }
#     .message-content pre {
#         background-color: #1f2937;
#         color: #f9fafb;
#         padding: 1rem;
#         border-radius: 0.5rem;
#         overflow-x: auto;
#         margin: 1rem 0;
#     }
#     .message-content pre code {
#         background-color: transparent;
#         color: #f9fafb;
#         padding: 0;
#     }
#     .message-content ul {
#         margin-left: 1.5rem;
#         margin-bottom: 1rem;
#     }
#     .message-content li {
#         margin-bottom: 0.5rem;
#         line-height: 1.6;
#     }
#     .assistant-message h1, .assistant-message h2, .assistant-message h3 {
#         color: #1f2937;
#     }
#     .stTextInput > div > div > input {
#         border-radius: 0.5rem;
#     }
# </style>
# """, unsafe_allow_html=True)

# # Initialize session state
# if 'conversation_history' not in st.session_state:
#     st.session_state.conversation_history = []
# if 'files_uploaded' not in st.session_state:
#     st.session_state.files_uploaded = False
# if 'files' not in st.session_state:
#     st.session_state.files = {}
# if 'error_log' not in st.session_state:
#     st.session_state.error_log = ''
# if 'processing' not in st.session_state:
#     st.session_state.processing = False

# def build_conversation_context():
#     """Build context from uploaded files and error log"""
#     context = "Here are the uploaded CrewAI system files:\n\n"
    
#     if 'agents' in st.session_state.files:
#         context += f"## AGENTS.YAML\n```yaml\n{st.session_state.files['agents']}\n```\n\n"
#     if 'tasks' in st.session_state.files:
#         context += f"## TASKS.YAML\n```yaml\n{st.session_state.files['tasks']}\n```\n\n"
#     if 'tools' in st.session_state.files:
#         context += f"## TOOLS.PY\n```python\n{st.session_state.files['tools']}\n```\n\n"
#     if 'crew' in st.session_state.files:
#         context += f"## CREW.PY\n```python\n{st.session_state.files['crew']}\n```\n\n"
#     if 'main' in st.session_state.files:
#         context += f"## MAIN.PY\n```python\n{st.session_state.files['main']}\n```\n\n"
    
#     if st.session_state.error_log.strip():
#         context += f"## ERROR LOG\n```\n{st.session_state.error_log}\n```\n\n"
    
#     return context

# def send_message(user_message, initial=False):
#     """Send message to Claude API with retry logic"""
#     max_retries = 3
#     retry_delay = 2
    
#     for attempt in range(max_retries):
#         try:
#             system_prompt = """You are an expert CrewAI test engineer with over 15 years of experience in debugging and optimizing multi-agent systems. You are having a conversation with a developer who needs help with their CrewAI implementation.

# ## Your Role
# - Provide conversational, helpful responses
# - Answer follow-up questions about the analysis
# - Offer clarifications and additional guidance
# - Help implement fixes step by step
# - Be supportive and encouraging

# ## Analysis Framework

# ### 1. AGENTS.YAML VALIDATION
# - **Role Definition**: Check if roles are specific, actionable, and not overlapping
# - **Goal Clarity**: Verify goals are measurable and aligned with system objectives
# - **Backstory Relevance**: Ensure backstories provide context without being verbose
# - **LLM Configuration**: Validate model selection and temperature settings
# - **Tool Assignment**: Confirm tools are correctly referenced and appropriate for the agent
# - **Common Issues**: Vague or duplicate roles, conflicting goals, missing tool references, inappropriate LLM settings

# ### 2. TASKS.YAML VALIDATION
# - **Description Completeness**: Check if task descriptions are clear and actionable
# - **Expected Output**: Verify output specifications are detailed and measurable
# - **Agent Assignment**: Ensure tasks are assigned to agents with appropriate capabilities
# - **Task Dependencies**: Validate task ordering and dependencies
# - **Context Usage**: Check if context from previous tasks is properly referenced
# - **Common Issues**: Ambiguous descriptions, missing expected_output, incorrect agent assignments, circular dependencies

# ### 3. TOOLS.PY VALIDATION
# - **Import Statements**: Verify all required libraries are imported
# - **Tool Definition**: Check @tool decorator usage and function signatures
# - **Error Handling**: Ensure robust try-catch blocks and error messages
# - **Return Types**: Validate return values match expected formats
# - **API Keys/Credentials**: Check for proper environment variable usage

# ### 4. CREW.PY VALIDATION
# - **Agent Instantiation**: Verify agents are correctly loaded from YAML
# - **Task Instantiation**: Check tasks are properly loaded with correct parameters
# - **Crew Configuration**: Validate process type (sequential/hierarchical)
# - **Manager LLM**: If hierarchical, ensure manager_llm is configured

# ### 5. MAIN.PY VALIDATION
# - **Crew Initialization**: Check if crew is properly imported and instantiated
# - **Input Handling**: Verify inputs dictionary matches task requirements
# - **Execution Method**: Validate kickoff() usage and parameters
# - **Output Handling**: Check result processing and error handling
# - **Environment Variables**: Ensure API keys are loaded correctly

# ### 6. ERROR LOG ANALYSIS
# - Parse error messages to identify root causes
# - Link errors to specific code issues
# - Provide targeted solutions for runtime errors
# - Explain error propagation and dependencies

# ## Response Style
# - Be conversational and friendly
# - Break down complex issues into digestible parts
# - Provide code examples when helpful
# - Ask clarifying questions when needed
# - Acknowledge progress and celebrate fixes"""

#             messages = []
            
#             # Add context on first message
#             if initial:
#                 full_message = build_conversation_context() + "\n" + user_message
#                 messages.append({"role": "user", "content": full_message})
#             else:
#                 # Build conversation history
#                 for msg in st.session_state.conversation_history:
#                     messages.append({
#                         "role": msg["role"],
#                         "content": msg["content"]
#                     })
#                 messages.append({"role": "user", "content": user_message})

#             # Get API key
#             api_key = None
#             if hasattr(st, 'secrets') and "ANTHROPIC_API_KEY" in st.secrets:
#                 api_key = st.secrets["ANTHROPIC_API_KEY"]
#             elif "ANTHROPIC_API_KEY" in os.environ:
#                 api_key = os.environ["ANTHROPIC_API_KEY"]
#             else:
#                 st.error("❌ API key not found. Please add ANTHROPIC_API_KEY to your Streamlit secrets.")
#                 return False
            
#             # Validate API key format
#             if not api_key or not api_key.startswith('sk-ant-'):
#                 st.error("❌ Invalid API key format. Anthropic API keys should start with 'sk-ant-'")
#                 return False
            
#             # Initialize client
#             client = anthropic.Anthropic(api_key=api_key)
            
#             # Make API call with timeout
#             message = client.messages.create(
#                 model="claude-sonnet-4-20250514",
#                 max_tokens=8000,
#                 system=system_prompt,
#                 messages=messages,
#                 timeout=60.0  # 60 second timeout
#             )
            
#             assistant_message = message.content[0].text
            
#             # Add messages to conversation history
#             st.session_state.conversation_history.append({
#                 "role": "user",
#                 "content": user_message,
#                 "timestamp": datetime.now().isoformat()
#             })
#             st.session_state.conversation_history.append({
#                 "role": "assistant",
#                 "content": assistant_message,
#                 "timestamp": datetime.now().isoformat()
#             })
            
#             return True
            
#         except anthropic.APIConnectionError as e:
#             if attempt < max_retries - 1:
#                 st.warning(f"Connection attempt {attempt + 1} failed. Retrying in {retry_delay} seconds...")
#                 time.sleep(retry_delay)
#                 continue
#             else:
#                 st.error(f"❌ Connection Error: Unable to reach Anthropic API after {max_retries} attempts.\n\nPossible causes:\n- Network connectivity issues\n- Streamlit Cloud firewall restrictions\n- Anthropic API is down\n\nPlease try again in a few moments.")
#                 return False
                
#         except anthropic.APIStatusError as e:
#             st.error(f"❌ API Status Error: {e.status_code}\n\nMessage: {str(e)}")
#             return False
            
#         except anthropic.RateLimitError as e:
#             st.error(f"❌ Rate Limit Error: You've exceeded the API rate limit. Please wait a moment and try again.")
#             return False
            
#         except anthropic.AuthenticationError as e:
#             st.error(f"❌ Authentication Error: Invalid API key. Please check your ANTHROPIC_API_KEY in Streamlit secrets.")
#             return False
            
#         except Exception as e:
#             st.error(f"❌ Unexpected Error: {type(e).__name__}: {str(e)}\n\nIf this persists, please check:\n1. Your API key is valid\n2. You have internet connectivity\n3. Anthropic API status at status.anthropic.com")
#             return False
    
#     return False

# # Main App Logic
# if not st.session_state.files_uploaded:
#     # Upload Interface
#     st.markdown("<div class='main-header'>", unsafe_allow_html=True)
#     st.title("🔧 CrewAI System Debugger")
#     st.markdown("**Upload your CrewAI files and error logs for expert analysis**")
#     st.markdown("</div>", unsafe_allow_html=True)
    
#     # Debug info (remove in production)
#     with st.expander("🔍 Debug Information"):
#         st.write("Checking API configuration...")
#         if hasattr(st, 'secrets') and "ANTHROPIC_API_KEY" in st.secrets:
#             api_key = st.secrets["ANTHROPIC_API_KEY"]
#             if api_key.startswith('sk-ant-'):
#                 st.success("✅ API key found and format is correct")
#             else:
#                 st.error("❌ API key found but format is incorrect (should start with 'sk-ant-')")
#         else:
#             st.error("❌ API key not found in secrets")
    
#     st.header("Upload System Files")
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.subheader("agents.yaml *")
#         agents_file = st.file_uploader("Upload agents.yaml", type=['yaml', 'yml'], key="agents")
        
#         st.subheader("tasks.yaml *")
#         tasks_file = st.file_uploader("Upload tasks.yaml", type=['yaml', 'yml'], key="tasks")
    
#     with col2:
#         st.subheader("crew.py *")
#         crew_file = st.file_uploader("Upload crew.py", type=['py'], key="crew")
        
#         st.subheader("main.py *")
#         main_file = st.file_uploader("Upload main.py", type=['py'], key="main")
    
#     with col3:
#         st.subheader("tools.py")
#         st.caption("(Optional)")
#         tools_file = st.file_uploader("Upload tools.py", type=['py'], key="tools")
    
#     st.markdown("---")
#     st.header("🐛 Error Log (Optional)")
#     st.caption("Paste any error messages, stack traces, or execution issues you're experiencing")
    
#     error_log = st.text_area(
#         "Error Log",
#         height=200,
#         placeholder="Paste your error logs here... For example:\n\nTraceback (most recent call last):\n  File 'main.py', line 15, in <module>\n    result = crew.kickoff()\nValueError: Agent 'researcher' not found in tasks.yaml",
#         label_visibility="collapsed"
#     )
    
#     st.markdown("---")
    
#     col1, col2 = st.columns([3, 1])
#     with col1:
#         st.caption("* Required files")
#     with col2:
#         if st.button("Start Debugging Session", type="primary", use_container_width=True,
#                     disabled=not (agents_file and tasks_file and crew_file and main_file)):
#             # Store files in session state
#             if agents_file:
#                 st.session_state.files['agents'] = agents_file.read().decode('utf-8')
#             if tasks_file:
#                 st.session_state.files['tasks'] = tasks_file.read().decode('utf-8')
#             if crew_file:
#                 st.session_state.files['crew'] = crew_file.read().decode('utf-8')
#             if main_file:
#                 st.session_state.files['main'] = main_file.read().decode('utf-8')
#             if tools_file:
#                 st.session_state.files['tools'] = tools_file.read().decode('utf-8')
            
#             st.session_state.error_log = error_log
#             st.session_state.files_uploaded = True
#             st.session_state.processing = True
#             st.rerun()

# else:
#     # Chat Interface
#     col1, col2, col3 = st.columns([2, 3, 1])
    
#     with col1:
#         st.title("🔧 CrewAI Debugger")
    
#     with col3:
#         if st.button("New Session", use_container_width=True):
#             st.session_state.conversation_history = []
#             st.session_state.files_uploaded = False
#             st.session_state.files = {}
#             st.session_state.error_log = ''
#             st.session_state.processing = False
#             st.rerun()
        
#         if len(st.session_state.conversation_history) > 0:
#             conversation_text = ""
#             for msg in st.session_state.conversation_history:
#                 role = msg["role"].upper()
#                 timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
#                 conversation_text += f"**{role}** ({timestamp}):\n{msg['content']}\n\n---\n\n"
            
#             st.download_button(
#                 label="Export Chat",
#                 data=conversation_text,
#                 file_name=f"crewai_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
#                 mime="text/markdown",
#                 use_container_width=True
#             )
    
#     st.markdown("---")
    
#     # Process initial analysis if needed
#     if st.session_state.processing and len(st.session_state.conversation_history) == 0:
#         with st.spinner("Analyzing your CrewAI system... This may take a moment."):
#             success = send_message("Please analyze my CrewAI system and identify any issues.", initial=True)
#             if success:
#                 st.session_state.processing = False
#                 st.rerun()
#             else:
#                 st.session_state.processing = False
    
#     # Display conversation history
#     if len(st.session_state.conversation_history) > 0:
#         chat_container = st.container()
#         with chat_container:
#             for msg in st.session_state.conversation_history:
#                 if msg["role"] == "user":
#                     st.markdown(f"""
#                     <div class="chat-message user-message">
#                         <div class="message-role">You • {datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M:%S")}</div>
#                         <div class="message-content">{msg["content"]}</div>
#                     </div>
#                     """, unsafe_allow_html=True)
#                 else:
#                     st.markdown(f"""
#                     <div class="chat-message assistant-message">
#                         <div class="message-role">AI Assistant • {datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M:%S")}</div>
#                         <div class="message-content">
#                     """, unsafe_allow_html=True)
#                     st.markdown(msg["content"], unsafe_allow_html=True)
#                     st.markdown("</div></div>", unsafe_allow_html=True)
#     else:
#         st.info("Waiting for initial analysis...")
    
#     # Input area
#     st.markdown("---")
    
#     # Use form to prevent rerun on input change
#     with st.form(key='message_form', clear_on_submit=True):
#         user_input = st.text_input(
#             "Message",
#             placeholder="Ask a question about the analysis, request clarification, or get help implementing fixes...",
#             label_visibility="collapsed"
#         )
        
#         col1, col2 = st.columns([5, 1])
#         with col2:
#             send_button = st.form_submit_button("Send", type="primary", use_container_width=True)
    
#     if send_button and user_input.strip():
#         with st.spinner("Thinking..."):
#             send_message(user_input)
#         st.rerun()

# # Footer
# st.markdown("---")
# st.markdown(
#     "<div style='text-align: center; color: #6b7280; padding: 1rem 0;'>"
#     "Powered by Claude AI • CrewAI Framework Expert Analysis"
#     "</div>",
#     unsafe_allow_html=True
# )
