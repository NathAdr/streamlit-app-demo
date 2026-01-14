import streamlit as st


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
    "Work Order",
    "Material Slip",
    "Process Stages",
    "Finished Goods Slip",
])

with tabs[0]:
    st.subheader("Work Order")
    st.write("Work Order content here")

    



    


with tabs[1]:
    st.subheader("Material Slip")
    st.write("Material Slip content here")

with tabs[2]:
    st.subheader("Process Stages")
    st.write("Process Stages content here")

with tabs[3]:
    st.subheader("Finished Goods Slip")
    st.write("Finished Goods Slip content here")

