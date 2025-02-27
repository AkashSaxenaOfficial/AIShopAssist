import streamlit as st

def init_chat_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_visible" not in st.session_state:
        st.session_state.chat_visible = False

def toggle_chat():
    st.session_state.chat_visible = not st.session_state.chat_visible

def chat_panel():
    init_chat_state()
    
    # Chat button (fixed position)
    st.markdown("""
        <style>
        .chat-button {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 999;
        }
        .chat-panel {
            position: fixed;
            bottom: 80px;
            right: 20px;
            width: 300px;
            height: 400px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 10px;
            z-index: 998;
        }
        </style>
    """, unsafe_allow_html=True)

    # Chat toggle button
    st.markdown(
        f"""
        <div class="chat-button">
            <button onclick="document.dispatchEvent(new Event('chat_toggle'))">
                💬 Chat
            </button>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.chat_visible:
        with st.container():
            st.markdown('<div class="chat-panel">', unsafe_allow_html=True)
            
            # Chat messages
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

            # Chat input
            if prompt := st.chat_input("How can I help you?"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                # Add simple response (replace with actual chatbot logic)
                response = f"I received your message: {prompt}"
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)
