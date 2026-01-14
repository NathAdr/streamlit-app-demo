import streamlit as st
from pathlib import Path
import pandas as pd
import datetime

st.markdown("""
<style>
div[data-testid="stTabs"] { width: 100%; }
div[data-testid="stTabs"] > div > div { display: flex; }
button[data-testid="stTab"] { flex: 1; justify-content: center; font-size: 16px; font-weight: 600; }
div.block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

FILES = {
    "payment": DATA_DIR / "OtherPayment.csv",
    "deposit": DATA_DIR / "OtherDeposit.csv"
}

ACCOUNTS = ["Kas Besar", "Bank BCA", "Bank Mandiri", "Petty Cash"]

def init_csv():
    if not FILES["payment"].exists():
        pd.DataFrame(columns=["Date", "Account", "Description", "Amount"]).to_csv(FILES["payment"], index=False)
    if not FILES["deposit"].exists():
        pd.DataFrame(columns=["Date", "Account", "Description", "Amount"]).to_csv(FILES["deposit"], index=False)

init_csv()

def load_data(key):
    return pd.read_csv(FILES[key])

def save_data(key, df):
    df.to_csv(FILES[key], index=False)

def format_rp(val):
    return f"Rp {val:,.0f}".replace(',', '.')

tabs = st.tabs([
    "Other Payment",
    "Other Deposit",
    "Bank Statement"
])

with tabs[0]:
    st.subheader("Other Payment")
    
    with st.form("form_payment", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            pay_date = st.date_input("Tanggal", datetime.date.today())
            account = st.selectbox("Sumber Dana (Kas/Bank)", ACCOUNTS)
        with col2:
            desc = st.text_input("Deskripsi")
            amount = st.number_input("Nilai Pengeluaran", min_value=0.0, step=1000.0)
            
        submitted = st.form_submit_button("Simpan Pengeluaran")
    
    if submitted:
        if amount > 0 and desc:
            df_pay = load_data("payment")
            new_row = pd.DataFrame([{
                "Date": pay_date,
                "Account": account,
                "Description": desc,
                "Amount": amount
            }])
            df_pay = pd.concat([df_pay, new_row], ignore_index=True)
            save_data("payment", df_pay)
            st.success("Data Other Payment berhasil disimpan!")
            st.rerun()
        else:
            st.error("Mohon isi deskripsi dan nilai nominal.")

    st.write("---")
    st.write("##### Riwayat Input Payment")
    st.dataframe(load_data("payment").sort_values(by="Date", ascending=False), use_container_width=True)

with tabs[1]:
    st.subheader("Other Deposit")
    
    with st.form("form_deposit", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            dep_date = st.date_input("Tanggal", datetime.date.today())
            account = st.selectbox("Masuk ke Akun (Kas/Bank)", ACCOUNTS)
        with col2:
            desc = st.text_input("Deskripsi")
            amount = st.number_input("Nilai Penerimaan", min_value=0.0, step=1000.0)
            
        submitted = st.form_submit_button("Simpan Pemasukan")
    
    if submitted:
        if amount > 0 and desc:
            df_dep = load_data("deposit")
            new_row = pd.DataFrame([{
                "Date": dep_date,
                "Account": account,
                "Description": desc,
                "Amount": amount
            }])
            df_dep = pd.concat([df_dep, new_row], ignore_index=True)
            save_data("deposit", df_dep)
            st.success("Data Other Deposit berhasil disimpan!")
            st.rerun()
        else:
            st.error("Mohon isi deskripsi dan nilai nominal.")

    st.write("---")
    st.write("##### Riwayat Input Deposit")
    st.dataframe(load_data("deposit").sort_values(by="Date", ascending=False), use_container_width=True)


with tabs[2]:
    st.subheader("Bank Statement")
    
    selected_account = st.selectbox("Lihat Mutasi Akun:", ["Semua"] + ACCOUNTS)
    
    df_p = load_data("payment")
    df_d = load_data("deposit")
    
    df_p_clean = df_p.copy()
    df_p_clean['Mutation'] = -df_p_clean['Amount'] 
    df_p_clean['Type'] = 'Payment'
    
    df_d_clean = df_d.copy()
    df_d_clean['Mutation'] = df_d_clean['Amount'] 
    df_d_clean['Type'] = 'Deposit'
    
    statement_df = pd.concat([df_p_clean, df_d_clean], ignore_index=True)
    
    if selected_account != "Semua":
        statement_df = statement_df[statement_df['Account'] == selected_account]
        
    if not statement_df.empty:
        statement_df['Date'] = pd.to_datetime(statement_df['Date'])
        statement_df = statement_df.sort_values(by='Date')
        
        statement_df['Balance'] = statement_df['Mutation'].cumsum()
        
        display_df = statement_df[['Date', 'Account', 'Description', 'Type', 'Mutation', 'Balance']].copy()

        display_df['Date'] = display_df['Date'].dt.date
  
        display_df['Mutation_Display'] = display_df['Mutation'].apply(lambda x: format_rp(x))
        display_df['Balance_Display'] = display_df['Balance'].apply(lambda x: format_rp(x))
        
        st.dataframe(
            display_df[['Date', 'Account', 'Description', 'Type', 'Mutation_Display', 'Balance_Display']], 
            use_container_width=True,
            column_config={
                "Mutation_Display": st.column_config.TextColumn("Mutasi"),
                "Balance_Display": st.column_config.TextColumn("Saldo Akhir")
            }
        )
        
        total_in = statement_df[statement_df['Mutation'] > 0]['Mutation'].sum()
        total_out = statement_df[statement_df['Mutation'] < 0]['Mutation'].sum()
        current_bal = statement_df['Balance'].iloc[-1]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Pemasukan", format_rp(total_in))
        c2.metric("Total Pengeluaran", format_rp(abs(total_out)))
        c3.metric("Saldo Akhir", format_rp(current_bal))
        
    else:
        st.info("Belum ada transaksi pada akun ini.")