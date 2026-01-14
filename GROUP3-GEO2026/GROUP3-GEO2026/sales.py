import streamlit as st
from pathlib import Path
import pandas as pd
import datetime
import os



st.markdown("""
<style>
div[data-testid="stTabs"] { width: 100%; }
div[data-testid="stTabs"] > div > div { display: flex; }
button[data-testid="stTab"] { flex: 1; justify-content: center; font-weight: 600; }
div.block-container { padding-top: 1rem; }
.metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px;}
</style>
""", unsafe_allow_html=True)


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

FILES = {
    "customer": DATA_DIR / "Customer.csv",
    "so": DATA_DIR / "SalesOrder.csv",
    "do": DATA_DIR / "DeliveryOrder.csv",
    "si": DATA_DIR / "SalesInvoice.csv",
    "sr": DATA_DIR / "SalesReceipt.csv"
}


def init_csv():

    if not FILES["customer"].exists():
        pd.DataFrame(columns=["Nama Customer", "Contact Info"]).to_csv(FILES["customer"], index=False)
    
    if not FILES["so"].exists():
        pd.DataFrame(columns=["Order_ID", "Date", "Customer", "Item", "Qty", "Price", "Total", "Status"]).to_csv(FILES["so"], index=False)
    if not FILES["do"].exists():
        pd.DataFrame(columns=["DO_ID", "Order_ID", "Date", "Customer", "Items_Summary", "Status"]).to_csv(FILES["do"], index=False)
    if not FILES["si"].exists():
        pd.DataFrame(columns=["Invoice_ID", "DO_ID", "Date", "Customer", "Total_Bill", "Paid_Amount", "Status"]).to_csv(FILES["si"], index=False)
    if not FILES["sr"].exists():
        pd.DataFrame(columns=["Receipt_ID", "Invoice_ID", "Date", "Customer", "Payment_Method", "Amount_Paid", "Notes"]).to_csv(FILES["sr"], index=False)

init_csv()


def load_data(key):
    df = pd.read_csv(FILES[key])

    if key == "customer" and "Balance" in df.columns:
        df = df.drop(columns=["Balance"])
    return df

def save_data(key, df):
    df.to_csv(FILES[key], index=False)

def format_rp(val):
    return f"Rp {val:,.0f}".replace(',', '.')

tabs = st.tabs([
    "Sales Order (SO)", 
    "Delivery Order (DO)", 
    "Sales Invoice (SI)", 
    "Sales Receipt (SR)", 
    "Customer"
])


with tabs[0]:
    st.subheader("Sales Order")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info("Buat Pesanan Baru")
        customers = load_data("customer")
        if customers.empty:
            st.warning("Belum ada data customer. Isi tab Customer dulu.")
            cust_list = []
        else:
            cust_list = customers["Nama Customer"].tolist()

        with st.form("add_item_so", clear_on_submit=True):
            selected_cust = st.selectbox("Pilih Customer", cust_list)
            so_date = st.date_input("Tanggal Order", datetime.date.today())
            item_name = st.text_input("Nama Barang")
            qty = st.number_input("Qty", min_value=1, value=1)
            price = st.number_input("Harga Satuan", min_value=0.0, step=1000.0)
            
            add_item_btn = st.form_submit_button("Tambah ke Keranjang")

      
        if "cart" not in st.session_state:
            st.session_state.cart = []

        if add_item_btn:
            if item_name:
                total = qty * price
                st.session_state.cart.append({
                    "Item": item_name, "Qty": qty, "Price": price, "Total": total
                })
                st.success(f"{item_name} ditambahkan!")
            else:
                st.error("Nama barang wajib diisi")

    with col2:
   
        st.write("### Keranjang Pesanan Saat Ini")
        if st.session_state.cart:
            cart_df = pd.DataFrame(st.session_state.cart)
            st.dataframe(cart_df.style.format({"Price": "Rp {:,.0f}", "Total": "Rp {:,.0f}"}), use_container_width=True)
            
            grand_total = cart_df["Total"].sum()
            st.markdown(f"#### Total Estimasi: {format_rp(grand_total)}")
            
            if st.button("Simpan Sales Order (Finalize)"):
                df_so = load_data("so")
               
                new_id = f"SO-{len(df_so['Order_ID'].unique()) + 1:03d}"
                
                new_rows = []
                for item in st.session_state.cart:
                    new_rows.append({
                        "Order_ID": new_id,
                        "Date": so_date,
                        "Customer": selected_cust,
                        "Item": item["Item"],
                        "Qty": item["Qty"],
                        "Price": item["Price"],
                        "Total": item["Total"],
                        "Status": "Pending" 
                    })
                
                df_so = pd.concat([df_so, pd.DataFrame(new_rows)], ignore_index=True)
                save_data("so", df_so)
                
                st.session_state.cart = [] 
                st.success(f"Sales Order {new_id} berhasil dibuat!")
                st.rerun()
        else:
            st.info("Keranjang masih kosong.")

    st.divider()
    st.write("### Riwayat Sales Order")
    df_so_display = load_data("so")
    if not df_so_display.empty:
        grouped_so = df_so_display.groupby(["Order_ID", "Date", "Customer", "Status"])["Total"].sum().reset_index()
        st.dataframe(grouped_so.style.format({"Total": "Rp {:,.0f}"}), use_container_width=True)


with tabs[1]:
    st.subheader("Delivery Order")
    
    df_so = load_data("so")
  
    pending_so = df_so[df_so["Status"] == "Pending"]["Order_ID"].unique()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info("Proses Pengiriman")
        selected_so_id = st.selectbox("Pilih No. Sales Order (Pending)", pending_so)
        do_date = st.date_input("Tanggal Pengiriman", datetime.date.today())
        
        if selected_so_id:
     
            items_to_ship = df_so[df_so["Order_ID"] == selected_so_id]
            cust_name = items_to_ship["Customer"].iloc[0]
            st.write(f"**Customer:** {cust_name}")
            

            items_summary = ", ".join([f"{row['Item']} ({row['Qty']})" for _, row in items_to_ship.iterrows()])
            
            if st.button("Buat Surat Jalan (Delivery Order)"):
                df_do = load_data("do")
                new_do_id = f"DO-{len(df_do) + 1:03d}"
                
                new_row = pd.DataFrame([{
                    "DO_ID": new_do_id,
                    "Order_ID": selected_so_id,
                    "Date": do_date,
                    "Customer": cust_name,
                    "Items_Summary": items_summary,
                    "Status": "Shipped"
                }])
                
                df_do = pd.concat([df_do, new_row], ignore_index=True)
                save_data("do", df_do)
                
                df_so.loc[df_so["Order_ID"] == selected_so_id, "Status"] = "Delivered"
                save_data("so", df_so)
                
                st.success(f"Delivery Order {new_do_id} berhasil dibuat!")
                st.rerun()

    with col2:
        st.write("### Detail Barang yang akan dikirim")
        if selected_so_id:
            st.dataframe(items_to_ship[["Item", "Qty"]], use_container_width=True)
        else:
            st.write("Tidak ada order yang dipilih.")
            
    st.divider()
    st.write("### Daftar Surat Jalan (History)")
    st.dataframe(load_data("do"), use_container_width=True)

with tabs[2]:
    st.subheader("Sales Invoice")
    
    df_do = load_data("do")
    df_so = load_data("so")
    
    df_si = load_data("si")
    invoiced_do_ids = df_si["DO_ID"].unique()
    uninvoiced_dos = df_do[~df_do["DO_ID"].isin(invoiced_do_ids)]["DO_ID"].unique()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info("Buat Invoice Baru")
        selected_do_id = st.selectbox("Pilih No. Delivery Order", uninvoiced_dos)
        inv_date = st.date_input("Tanggal Faktur", datetime.date.today())
        
        if selected_do_id:
            do_data = df_do[df_do["DO_ID"] == selected_do_id].iloc[0]
            so_id = do_data["Order_ID"]
            
            so_items = df_so[df_so["Order_ID"] == so_id]
            total_bill = so_items["Total"].sum()
            
            st.write(f"**Customer:** {do_data['Customer']}")
            st.metric("Total Tagihan", format_rp(total_bill))
            
            if st.button("Generate Invoice"):
                new_inv_id = f"INV-{len(df_si) + 1:03d}"
                
                new_row = pd.DataFrame([{
                    "Invoice_ID": new_inv_id,
                    "DO_ID": selected_do_id,
                    "Date": inv_date,
                    "Customer": do_data["Customer"],
                    "Total_Bill": total_bill,
                    "Paid_Amount": 0,
                    "Status": "Unpaid"
                }])
                
                df_si = pd.concat([df_si, new_row], ignore_index=True)
                save_data("si", df_si)
                
                df_do.loc[df_do["DO_ID"] == selected_do_id, "Status"] = "Invoiced"
                save_data("do", df_do)
                
                st.success(f"Invoice {new_inv_id} berhasil diterbitkan!")
                st.rerun()

    with col2:
        st.write("### Daftar Invoice")
        st.dataframe(load_data("si").style.format({"Total_Bill": "Rp {:,.0f}", "Paid_Amount": "Rp {:,.0f}"}), use_container_width=True)


with tabs[3]:
    st.subheader("Sales Receipt")
    
    df_si = load_data("si")
    unpaid_invoices = df_si[df_si["Status"] != "Paid"]["Invoice_ID"].unique()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info("Input Pembayaran")
        selected_inv_id = st.selectbox("Pilih No. Invoice", unpaid_invoices)
        
        if selected_inv_id:
            inv_data = df_si[df_si["Invoice_ID"] == selected_inv_id].iloc[0]
            sisa_tagihan = inv_data["Total_Bill"] - inv_data["Paid_Amount"]
            
            st.write(f"**Customer:** {inv_data['Customer']}")
            st.write(f"Total Faktur: {format_rp(inv_data['Total_Bill'])}")
            st.write(f"Sudah Dibayar: {format_rp(inv_data['Paid_Amount'])}")
            st.markdown(f"#### Sisa: {format_rp(sisa_tagihan)}")
            
            with st.form("pay_form"):
                pay_date = st.date_input("Tanggal Bayar", datetime.date.today())
                pay_method = st.selectbox("Metode Pembayaran", ["Transfer Bank", "Cash", "Cek/Giro"])
                pay_nominal = st.number_input("Nominal Pembayaran", min_value=0.0, max_value=float(sisa_tagihan), step=1000.0)
                submit_pay = st.form_submit_button("Simpan Pembayaran")
                
            if submit_pay and pay_nominal > 0:
                df_sr = load_data("sr")
                new_sr_id = f"RCP-{len(df_sr) + 1:03d}"
                
                new_receipt = pd.DataFrame([{
                    "Receipt_ID": new_sr_id,
                    "Invoice_ID": selected_inv_id,
                    "Date": pay_date,
                    "Customer": inv_data["Customer"],
                    "Payment_Method": pay_method,
                    "Amount_Paid": pay_nominal,
                    "Notes": "Lunas" if pay_nominal == sisa_tagihan else "Sebagian"
                }])
                df_sr = pd.concat([df_sr, new_receipt], ignore_index=True)
                save_data("sr", df_sr)
                
                new_total_paid = inv_data["Paid_Amount"] + pay_nominal
                status = "Paid" if new_total_paid >= inv_data["Total_Bill"] else "Partial"
                
                df_si.loc[df_si["Invoice_ID"] == selected_inv_id, "Paid_Amount"] = new_total_paid
                df_si.loc[df_si["Invoice_ID"] == selected_inv_id, "Status"] = status
                save_data("si", df_si)
                
                st.success("Pembayaran berhasil disimpan!")
                st.rerun()

    with col2:
        st.write("### Riwayat Pembayaran")
        st.dataframe(load_data("sr").style.format({"Amount_Paid": "Rp {:,.0f}"}), use_container_width=True)


with tabs[4]:
    st.subheader("Data Customer")
    
    data = load_data("customer")

   
    st.dataframe(data, use_container_width=True)

    st.write("### Tambah Customer Baru")
    with st.form("add_cus", clear_on_submit=True):
        cus = st.text_input("Nama Customer")
        number = st.text_input("Contact Info")


        submitted = st.form_submit_button("Simpan")

    if submitted:
        if cus.strip() == "":
            st.error("Nama Customer Wajib diisi!")
        else:
     
            new_row = pd.DataFrame([[cus, number]], columns=data.columns)  
            data = pd.concat([data, new_row], ignore_index=True)
            save_data("customer", data)
            st.rerun()