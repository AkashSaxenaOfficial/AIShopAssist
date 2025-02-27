import streamlit as st
from data.mock_data import get_product_by_id
from components.chat_panel import chat_panel

def show_pdp():
    if "selected_product" not in st.session_state:
        st.warning("Please select a product from the product list")
        if st.button("Go to Products"):
            st.switch_page("pages/plp.py")
        return

    product = get_product_by_id(st.session_state.selected_product)
    
    if not product:
        st.error("Product not found")
        return

    # Product details layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(product["image"], use_column_width=True)
    
    with col2:
        st.title(product["name"])
        st.write(f"### ${product['price']:.2f}")
        st.write(product["description"])
        st.write(f"Category: {product['category']}")
        
        # Add to cart button (mock functionality)
        if st.button("Add to Cart"):
            st.success("Added to cart!")

    # Add chat panel
    chat_panel()

if __name__ == "__main__":
    show_pdp()
