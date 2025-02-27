# streamlit run app.py

import streamlit as st
from pages.plp import show_plp
from components.chat_panel import chat_panel

# Configure Streamlit page
st.set_page_config(
    page_title="E-Commerce Demo",
    page_icon="🛍️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0;
    }
    </style>
""", unsafe_allow_html=True)

# Main navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Products"):
    st.switch_page("pages/plp.py")

# Show home page content
st.title("Welcome to Our Store")
st.write("Explore our products and chat with our AI assistant!")

# Featured products section
st.header("Featured Products")
show_plp()  # Show product listing on home page

# Add chat panel
chat_panel()

