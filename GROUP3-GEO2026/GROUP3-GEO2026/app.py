import streamlit as st
import os
import base64

st.set_page_config(
    page_title="Cooperative Management",
    page_icon=":material/edit:",
    layout="wide"
)

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

logo_path = os.path.join(parent_dir, "img", "digikop.png") 

if os.path.exists(logo_path):
    img_base64 = get_base64_of_bin_file(logo_path)
    
    st.markdown(
        f"""
        <style>
        /* Target area navigasi dan tambahkan gambar sebelumnya */
        [data-testid="stSidebarNav"]::before {{
            content: "";
            display: block;
            margin-left: auto;
            margin-right: auto;
            margin-bottom: 20px;
            width: 200px;  /* ATUR LEBAR LOGO DISINI */
            height: 120px; /* ATUR TINGGI LOGO DISINI */
            background-image: url("data:image/png;base64,{img_base64}");
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("Gambar logo tidak ditemukan. Cek path/nama file.")

st.markdown("""
<style>
section[data-testid="stSidebar"] {
    width: 280px !important;
    min-width: 280px !important;
    max-width: 280px !important;
}
section[data-testid="stSidebar"] + section {
    margin-left: 280px;
}
div[data-testid="stSidebarResizeHandle"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

home_page = st.Page("home.py", title="Home", icon=":material/home:")
predict_page = st.Page("predict.py", title="Prediction", icon=":material/trending_up:")
purchasing_page = st.Page("purchasing.py", title="Puchasing", icon=":material/shopping_cart:")
sales_page = st.Page("sales.py", title="Sales", icon=":material/sell:")
finance_page = st.Page("finance.py", title="Finance", icon=":material/payments:")
inventory_page = st.Page("inventory.py", title="Inventory", icon=":material/inventory:")
manufacture_page = st.Page("manufacture.py", title="Manufacture", icon=":material/factory:")
human_page = st.Page("human.py", title="Human Capital", icon=":material/groups:")

pg = st.navigation([home_page, predict_page, purchasing_page, sales_page, finance_page, inventory_page, manufacture_page, human_page])

st.sidebar.markdown(
    """
    <p style='margin:0; font-size:14px; color:gray;'><strong>Made by</strong></p>
    <p style='margin:0; font-size:12px; color:gray;'>Lin Chao Ran</p>
    <p style='margin:0; font-size:12px; color:gray;'>Nerissa Kho Wei Na</p>
    <p style='margin:0; font-size:12px; color:gray;'>Keith Warren Wu Boediman</p>
    <p style='margin:0; font-size:12px; color:gray;'>Michael Nathaniel</p>
    <p style='margin:0; font-size:12px; color:gray;'>Nathan Adrian Chandra</p>
    <p style='margin:0; font-size:12px; color:gray;'>Bryant Chandra</p>
    """,
    unsafe_allow_html=True
)

st.sidebar.caption("")

st.sidebar.markdown(
    "<p style='margin:0; font-size:14px; color:gray;'><strong>In collaboration with:</strong></p>",
    unsafe_allow_html=True
)

st.sidebar.markdown("""
<div style="display:flex; justify-content:center; gap:12px; align-items:center;">
    <img src="https://serviceomni.petra.ac.id/resources/9ad247aa-98ac-475a-a2b5-d50903a2a128" width="60">
    <span style="font-size:18px;">|</span>
    <img src="https://cdn.freelogovectors.net/wp-content/uploads/2022/03/sutd_logo_freelogovectors.net_.png" width="110">
</div>
""", unsafe_allow_html=True)

st.sidebar.caption("")

st.sidebar.markdown(
    """
    <div style="font-size:12px; color:gray; margin-top:10px;">
        © 2026 <b>GEO - Group 3</b><br>
        All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)

pg.run()