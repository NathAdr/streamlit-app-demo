import streamlit as st
from pathlib import Path
import pandas as pd
from datetime import date

st.markdown("""
<style>
div[data-testid="stTabs"] {
    width: 100%;
}

div[data-testid="stTabs"] > div > div {
    display: flex;
}

button[data-testid="stTab"] {
    flex: 1;
    justify-content: center;
    font-size: 16px;
    font-weight: 600;
}

div.block-container {
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "Item",
    "Inventory Taking Order"
])

with tabs[0]:
    BASE_DIR = Path(__file__).resolve().parent.parent
    FILE_PATH = BASE_DIR / "Item.csv"
    
    data = pd.read_csv(FILE_PATH)
    st.write(data)


    st.subheader("Add New Item Data")

    with st.form("add_item", clear_on_submit=True):
        name = st.text_input("Item Name")
        number = st.text_input("Item Code")
        type = st.text_input("Item Type")
        unit = st.text_input("Unit")
        qty = st.number_input("Qty", step=1)

        submitted = st.form_submit_button("Simpan")

    if submitted:
        if name.strip() == "":
            st.error("Nama Item Wajib diisi!")
        else:
            new_row = pd.DataFrame([[
                name,
                number,
                type,
                unit,
                qty
            ]], columns=data.columns)  

            data = pd.concat([data, new_row], ignore_index=True)
            data.to_csv(FILE_PATH, index=False)

            st.rerun()

with tabs[1]:
    BASE_DIR = Path(__file__).resolve().parent.parent
    FILE_PATH = BASE_DIR / "Inventory.csv"
    
    data = pd.read_csv(FILE_PATH)
    st.write(data)


    st.subheader("Add New Data")

    with st.form("add_inven", clear_on_submit=True):
        dte = st.date_input("Tanggal", date.today())
        ware = st.text_input("Warehouse")
        stat = st.text_input("Status")
        pic = st.text_input("PIC")

        submitted = st.form_submit_button("Simpan")

    if submitted:
        if pic.strip() == "":
            st.error("Nama PIC Wajib diisi!")
        else:
            new_row = pd.DataFrame([[
                dte,
                ware,
                stat,
                pic
            ]], columns=data.columns)  

            data = pd.concat([data, new_row], ignore_index=True)
            data.to_csv(FILE_PATH, index=False)

            st.rerun()
