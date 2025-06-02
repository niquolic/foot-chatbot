"""
LXP - Advanced AI development Workshop: AI Football Assistant frontend
"""

import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

# Import our backend logic
from backend import get_backend_instance
from prompts import INITIAL_MESSAGE, CHAT_INPUT_PLACEHOLDER

def setup_page():
    """
    Configure the Streamlit page with football theme.
    """
    st.set_page_config(
        page_title="AI Football Chatbot",
        page_icon="⚽️",
        layout="wide"
    )
    
    # Simple header with football theme
    st.title("⚽️ AI Football Chatbot")
    st.subheader("Your AI Football Assistant")
    
    # Add football info boxes using columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("🌍 **Global Coverage**\nGet football news for any team worldwide")
    
    with col2:
        st.info("⚡ **Real-time Data**\nGet live match updates and scores")
    
    with col3:
        st.info("📈 **Detailed Analysis**\nGet comprehensive team and player statistics")
    

def setup_sidebar():
    """
    Create a football-themed sidebar with information and controls.
    """
    st.sidebar.header("⚽️ Football Chatbot")
    
    # Football service info
    with st.sidebar.expander("📡 What can I do?"):
        st.write("""
        I can help you get comprehensive football news for any team worldwide.
        I can query the following tools:
        - Get football news for any team worldwide
        - Get football news for any team worldwide
        """)
    
    # Quick examples
    with st.sidebar.expander("💡 Try These Examples"):
        st.write("""
        **Sample Questions:**
        - "What's the football news for Manchester United?"
        - "Show me the football news for Barcelona"
        - "What's the football news for Real Madrid?"
        - "What's the football news for Bayern Munich?"
        """)
    


def setup_chat_memory():
    """
    Set up conversation memory and history.
    """
    msgs = StreamlitChatMessageHistory()
    memory = ConversationBufferMemory(
        chat_memory=msgs, 
        return_messages=True, 
        memory_key="chat_history", 
        output_key="output"
    )
    return msgs, memory


def initialize_chat_if_needed(msgs):
    """
    Initialize the chat with a welcome message if needed.
    """
    if len(msgs.messages) == 0:
        msgs.add_ai_message(INITIAL_MESSAGE)
        st.session_state.steps = {}


def add_reset_button(msgs):
    """
    Add a reset button in the sidebar.
    """
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🔄 Reset Chat", help="Start a new conversation"):
        msgs.clear()
        msgs.add_ai_message(INITIAL_MESSAGE)
        st.session_state.steps = {}
        st.rerun()
    

def display_chat_messages(msgs):
    """
    Display chat messages with football-themed avatars.
    """
    avatars = {"human": "🙋‍♂️", "ai": "⚽️"}
    
    for idx, msg in enumerate(msgs.messages):
        with st.chat_message(msg.type, avatar=avatars[msg.type]):
            # Show tool usage for AI messages
            if msg.type == "ai":
                display_intermediate_steps(idx)
            
            # Display the message content
            st.write(msg.content)


def display_intermediate_steps(message_index):
    """
    Display football tool usage with appropriate icons.
    """
    steps = st.session_state.steps.get(str(message_index), [])
    
    for step in steps:
        if step[0].tool == "_Exception":
            continue
        
        # Football tool icons
        tool_icons = {
            "get_football_news": "⚽️",
            "get_match_stats": "📊",
            "get_team_info": "🏆",
            "get_player_stats": "👤"
        }
        
        tool_name = step[0].tool
        icon = tool_icons.get(tool_name, "🔧")
        display_name = tool_name.replace('_', ' ').title()
        
        with st.status(f"{icon} {display_name}: {step[0].tool_input}", state="complete"):
            st.write("**Reasoning:**", step[0].log)
            st.write("**Result:**", step[1])


def handle_user_input(msgs, memory, backend):
    """
    Handle user input and generate AI response.
    """
    if prompt := st.chat_input(placeholder=CHAT_INPUT_PLACEHOLDER):
        # Display user message
        st.chat_message("human", avatar="🙋‍♂️").write(prompt)
        
        # Process through AI
        with st.chat_message("ai", avatar="⚽️"):
            with st.spinner("⚽️ Analyzing football data..."):
                st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
                executor = backend.create_agent_executor(memory)
                response = backend.process_message(prompt, executor, st_cb)
            
            # Display response
            st.write(response["output"])
            
            # Store tool usage steps
            st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]


def main():
    """
    Main function that runs the AI Weatherman app.
    """
    # Setup page
    setup_page()
    
    # Setup sidebar
    setup_sidebar()
    
    # Initialize backend and memory
    backend = get_backend_instance()
    msgs, memory = setup_chat_memory()
    
    # Initialize chat
    initialize_chat_if_needed(msgs)
    
    # Add controls
    add_reset_button(msgs)
    
    # Display conversation
    display_chat_messages(msgs)
    
    # Handle new input
    handle_user_input(msgs, memory, backend)


if __name__ == "__main__":
    main() 