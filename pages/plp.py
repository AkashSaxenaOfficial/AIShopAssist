import streamlit as st
from data.mock_data import get_products_by_category
from components.chat_panel import chat_panel

def show_plp():
    st.title("Products")
    
    # Filters
    category = st.selectbox("Category", ["All", "Electronics", "Clothing", "Home"])
    
    # Get products
    products = get_products_by_category(None if category == "All" else category)
    
    # Display products in grid
    cols = st.columns(3)
    for idx, product in enumerate(products):
        with cols[idx % 3]:
            st.image(product["image"], use_column_width=True)
            st.subheader(product["name"])
            st.write(f"${product['price']:.2f}")
            if st.button(f"View Details {product['id']}", key=f"prod_{product['id']}"):
                st.session_state.selected_product = product["id"]
                st.switch_page("pages/pdp.py")

    # Add chat panel
    chat_panel()

if __name__ == "__main__":
    show_plp()
