import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date
import numpy as np

st.set_page_config(layout="wide")

st.markdown("""
<style>
button[data-testid="stTab"] {
    flex: 1;
    justify-content: center;
    font-size: 16px;
    font-weight: 600;
}
div.block-container { padding-top: 1rem; }
.invoice-box {
    border: 2px solid #333;
    padding: 30px;
    border-radius: 10px;
    background-color: #ffffff;
    color: #000;
    margin-bottom: 20px;
}
/* Menghilangkan background putih pada tabel di dalam invoice agar menyatu dengan box */
.invoice-box div[data-testid="stTable"] {
    background-color: transparent !important;
}
</style>
""", unsafe_allow_html=True)

COL_TGL = "TANGGAL PEMBELIAN"
COL_SUP = "NAMA SUPPLIER & PENYEDIA JASA"
COL_ITM = "Item"
COL_QTY = "Qty"
COL_HRG = "Harga"
COL_KET = "KETERANGAN"
COL_STS = "Status"
COL_ALM = "ALAMAT" 
STANDARD_COLS = [COL_TGL, COL_SUP, COL_ITM, COL_QTY, COL_HRG, COL_KET, COL_STS]

def parse_rupiah(text):
    if pd.isna(text) or text == "" or text is None:
        return 0
    if isinstance(text, (int, float)):
        return int(text) if not pd.isna(text) else 0
    try:
        cleaned = str(text).replace("Rp", "").replace("rp", "").replace(".", "").replace(",", "").strip()
        return int(cleaned) if cleaned else 0
    except ValueError:
        return 0

def load_data(file_path):
    if Path(file_path).exists():
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()
        mapping = {
            'tanggal': COL_TGL, 'tanggal pembelian': COL_TGL,
            'supplier': COL_SUP, 'nama supplier & penyedia jasa': COL_SUP,
            'item': COL_ITM, 'qty': COL_QTY, 'harga': COL_HRG,
            'keterangan': COL_KET, 'ket': COL_KET, 'status': COL_STS
        }
        new_column_names = []
        for col in df.columns:
            cleaned_col = col.lower().strip()
            if cleaned_col in mapping:
                new_column_names.append(mapping[cleaned_col])
            else:
                new_column_names.append(col)
        df.columns = new_column_names
        df = df.loc[:, ~df.columns.duplicated()]
        for col in STANDARD_COLS:
            if col not in df.columns:
                df[col] = 0 if col == COL_HRG else ("Pending" if col == COL_STS else "")
        df = df[STANDARD_COLS].copy()
        if COL_HRG in df.columns:
            df[COL_HRG] = df[COL_HRG].apply(parse_rupiah)
            df[COL_HRG] = pd.to_numeric(df[COL_HRG], errors="coerce").fillna(0).astype(int)
        return df
    return pd.DataFrame(columns=STANDARD_COLS)

def get_next_invoice_count():
    log_file = BASE_DIR / "invoice_log.txt"
    today_str = date.today().strftime("%Y%m%d")
    if not log_file.exists():
        return today_str, 1
    with open(log_file, "r") as f:
        try:
            content = f.read().split("|")
            if len(content) == 2:
                last_date, last_count = content[0], int(content[1])
                if last_date == today_str:
                    return today_str, last_count + 1
        except:
            pass
        return today_str, 1

def update_invoice_log(today_str, count):
    log_file = BASE_DIR / "invoice_log.txt"
    with open(log_file, "w") as f:
        f.write(f"{today_str}|{count}")

po_files = {
    "Bahan Baku Utama (Kain)": "DATA SUPPLIER KAIN.csv",
    "Bahan Pendukung": "DATA SUPPLIER KAIN - Bahan Baku Pendukung PO.csv",
    "Jasa Bordir": "DATA SUPPLIER KAIN - Jasa Bordir PO.csv",
    "Jasa Printing": "DATA SUPPLIER KAIN - Jasa Printing PO.csv",
    "Jasa DTF Sablon": "DATA SUPPLIER KAIN - Jasa DTF Sablon PO.csv",
    "Jasa Sublim": "DATA SUPPLIER KAIN - Jasa Sublim PO.csv",
    "Jasa Distribusi": "DATA SUPPLIER KAIN - Jasa Distribusi PO.csv",
    "ATK": "DATA SUPPLIER KAIN - ATK PO.csv"
}

sup_files = {
    "Bahan Baku Utama (Kain)": "Supplier Utama.csv",
    "Bahan Pendukung": "Supplier Pendukung.csv",
    "Jasa Bordir": "Jasa Bordir.csv",
    "Jasa Printing": "Jasa Printing.csv",
    "Jasa DTF Sablon": "Jasa DTF Sablon.csv",
    "Jasa Sublim": "Jasa Sublim.csv",
    "Jasa Distribusi": "Jasa Distribusi.csv",
    "ATK": "ATK.csv"
}

BASE_DIR = Path(__file__).resolve().parent.parent
INVOICE_FILE = BASE_DIR / "purchase_invoice.csv"
HISTORY_FILE = BASE_DIR / "payment_history.csv"

tabs = st.tabs(["Purchase Order", "Receive Item", "Purchase Invoice", "Payment History", "Supplier"])

with tabs[0]:
    po_menu = st.selectbox("Kategori PO", list(po_files.keys()), key="sb_po")
    path_po = BASE_DIR / po_files[po_menu]
    df_po = load_data(path_po)
    
    st.dataframe(
        df_po, 
        column_config={COL_HRG: st.column_config.NumberColumn(COL_HRG, format="Rp %,.0f")},
        hide_index=True, 
        use_container_width=True
    )
    
    path_sup_for_po = BASE_DIR / sup_files[po_menu]
    list_supplier = []
    if path_sup_for_po.exists():
        df_temp_sup = pd.read_csv(path_sup_for_po)
        if not df_temp_sup.empty:
            df_temp_sup.columns = df_temp_sup.columns.str.strip()
            col_name_check = COL_SUP if COL_SUP in df_temp_sup.columns else df_temp_sup.columns[0]
            list_supplier = df_temp_sup[col_name_check].dropna().unique().tolist()

    st.divider()
    with st.form("form_po", clear_on_submit=True):
        col1, col2 = st.columns(2)
        tanggal = col1.date_input(COL_TGL, date.today())
        supplier = col1.selectbox(COL_SUP, ["Pilih Supplier"] + list_supplier)
        item = col2.text_input(COL_ITM)
        qty = col2.text_input(COL_QTY)
        harga_text = st.text_input(f"{COL_HRG} (Rp)", placeholder="Contoh: 150000")
        ket = st.text_area(COL_KET)
        
        if st.form_submit_button("Save Purchase Order"):
            harga = parse_rupiah(harga_text)
            if supplier != "Pilih Supplier" and item:
                new_row = [tanggal.strftime("%Y-%m-%d"), supplier, item, qty, harga, ket, "Pending"]
                new_data = pd.DataFrame([new_row], columns=STANDARD_COLS)
                pd.concat([df_po, new_data], ignore_index=True).to_csv(path_po, index=False)
                st.rerun()

with tabs[1]:
    rec_menu = st.selectbox("Kategori Receive Item", list(po_files.keys()), key="sb_receive")
    path_rec = BASE_DIR / po_files[rec_menu]
    df_rec = load_data(path_rec)

    st.write("### Daftar Order (Klik baris untuk konfirmasi)")
    search_rec = st.text_input(f"Cari...", key="search_receive")
    
    df_pending = df_rec[df_rec[COL_STS] == "Pending"].copy() if not df_rec.empty else pd.DataFrame()
    if not df_pending.empty and search_rec:
        df_pending = df_pending[df_pending.apply(lambda row: row.astype(str).str.contains(search_rec, case=False).any(), axis=1)]

    event_rec = st.dataframe(
        df_pending, 
        column_config={COL_HRG: st.column_config.NumberColumn(COL_HRG, format="Rp %,.0f")}, 
        hide_index=True, 
        use_container_width=True, 
        on_select="rerun", 
        selection_mode="single-row", 
        key="df_receive_action"
    )

    selected_rows = event_rec.selection.rows
    if selected_rows and not df_pending.empty:
        idx_in_pending = selected_rows[0]
        item_name = df_pending.iloc[idx_in_pending].get(COL_ITM, "Unknown")
        if st.button(f"Konfirmasi Terima: {item_name}", type="primary"):
            idx_to_update = df_pending.index[idx_in_pending]
            df_rec.at[idx_to_update, COL_STS] = "Diterima"
            df_rec.to_csv(path_rec, index=False)
            st.rerun()

    st.divider()
    col_a, col_b = st.columns([3, 1])
    col_a.subheader("Ringkasan Barang Diterima")
    
    if col_b.button("Generate Invoice", use_container_width=True):
        all_data_diterima = []
        for cat, file_name in po_files.items():
            p = BASE_DIR / file_name
            df_cat = load_data(p)
            if not df_cat.empty:
                diterima = df_cat[df_cat[COL_STS] == "Diterima"].copy()
                if not diterima.empty:
                    all_data_diterima.append(diterima)
                    df_cat[df_cat[COL_STS] != "Diterima"].to_csv(p, index=False)
        
        if all_data_diterima:
            combined_df = pd.concat(all_data_diterima, ignore_index=True)
            today_str, current_count = get_next_invoice_count()
            invoice_list = []
            
            for supplier_name, group in combined_df.groupby(COL_SUP):
                inv_no = f"INV/{today_str}/{current_count:03d}"
                group_to_save = group.copy()
                group_to_save["No Invoice"] = inv_no
                group_to_save["Terbayar"] = 0 
                invoice_list.append(group_to_save)
                current_count += 1
                
            update_invoice_log(today_str, current_count - 1)
            final_invoice_df = pd.concat(invoice_list, ignore_index=True)
            
            if INVOICE_FILE.exists():
                existing_inv = pd.read_csv(INVOICE_FILE)
                pd.concat([existing_inv, final_invoice_df], ignore_index=True).to_csv(INVOICE_FILE, index=False)
            else:
                final_invoice_df.to_csv(INVOICE_FILE, index=False)
            st.success(f"Berhasil Generate {len(invoice_list)} Invoice!")
            st.rerun()
        else:
            st.warning("Tidak ada barang dengan status 'Diterima' untuk diproses.")

    df_received = df_rec[df_rec[COL_STS] == "Diterima"].copy() if not df_rec.empty else pd.DataFrame()
    if not df_received.empty:
        summary_cols = [COL_ITM, COL_QTY, COL_HRG, COL_SUP]
        st.table(df_received[summary_cols].style.format({COL_HRG: "Rp {:,.0f}"}))
    else:
        st.info("Belum ada barang yang diterima di kategori ini.")

with tabs[2]:
    st.subheader("Purchase Invoice")
    if INVOICE_FILE.exists():
        df_inv = pd.read_csv(INVOICE_FILE)
        if not df_inv.empty:
            if "Terbayar" not in df_inv.columns:
                df_inv["Terbayar"] = 0

            invoices = df_inv["No Invoice"].unique()
            for inv_id in invoices:
                inv_data = df_inv[df_inv["No Invoice"] == inv_id].copy()
                supplier_head = inv_data[COL_SUP].iloc[0] if COL_SUP in inv_data.columns else "Unknown"
                
                st.markdown(f'<div class="invoice-box">', unsafe_allow_html=True)
                col_h1, col_h2 = st.columns(2)
                col_h1.markdown(f"### **{supplier_head}**")
                inv_date = inv_data[COL_TGL].iloc[0] if COL_TGL in inv_data.columns else "-"
                col_h2.markdown(f"<div style='text-align:right'><b>Nomor:</b> {inv_id}<br><b>Tanggal:</b> {inv_date}</div>", unsafe_allow_html=True)
                
                inv_data[COL_QTY] = pd.to_numeric(inv_data[COL_QTY], errors='coerce').fillna(0)
                inv_data["Subtotal"] = inv_data[COL_QTY] * inv_data[COL_HRG]
                
                st.table(inv_data[[COL_ITM, COL_QTY, COL_HRG, "Subtotal"]].style.format({COL_HRG: "Rp {:,.0f}", "Subtotal": "Rp {:,.0f}"}))
                
                total_tagihan = inv_data["Subtotal"].sum()
                terbayar_sebelumnya = inv_data["Terbayar"].iloc[0]
                sisa_tagihan = total_tagihan - terbayar_sebelumnya
                
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    st.write(f"**Total Tagihan:** Rp {total_tagihan:,.0f}")
                    st.write(f"**Sudah Dibayar:** Rp {terbayar_sebelumnya:,.0f}")
                    st.markdown(f"#### **Sisa Perlu Dibayar: Rp {sisa_tagihan:,.0f}**")
                
                with col_f2:
                    with st.form(f"pay_{inv_id}"):
                        metode = st.selectbox("Metode Pembayaran", ["Cash", "Bank BCA", "Bank Mandiri"], key=f"met_{inv_id}")
                        input_bayar = st.text_input("Jumlah Bayar (Rp)", placeholder="Masukkan angka", key=f"val_{inv_id}")
                        submit_pay = st.form_submit_button("Konfirmasi Pembayaran")
                        
                        if submit_pay:
                            jumlah_bayar = parse_rupiah(input_bayar)
                            if jumlah_bayar > 0:
                                total_terbayar_baru = terbayar_sebelumnya + jumlah_bayar
                                
                                history_row = pd.DataFrame([{
                                    "Tanggal Bayar": date.today().strftime("%Y-%m-%d"),
                                    "Nama Supplier": supplier_head,
                                    "Jumlah Dibayar": jumlah_bayar,
                                    "Metode": metode,
                                    "No Invoice": inv_id
                                }])
                                
                                if HISTORY_FILE.exists():
                                    pd.concat([pd.read_csv(HISTORY_FILE), history_row], ignore_index=True).to_csv(HISTORY_FILE, index=False)
                                else:
                                    history_row.to_csv(HISTORY_FILE, index=False)

                                if total_terbayar_baru >= total_tagihan:
                                    df_inv = df_inv[df_inv["No Invoice"] != inv_id]
                                    st.success(f"Invoice {inv_id} LUNAS.")
                                else:
                                    df_inv.loc[df_inv["No Invoice"] == inv_id, "Terbayar"] = total_terbayar_baru
                                    st.info(f"Pembayaran sebagian berhasil dicatat.")
                                
                                df_inv.to_csv(INVOICE_FILE, index=False)
                                st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Belum ada invoice aktif.")
    else:
        st.info("Belum ada invoice.")

with tabs[3]:
    st.subheader("Payment History")
    if HISTORY_FILE.exists():
        df_history = pd.read_csv(HISTORY_FILE)
        if not df_history.empty:
            st.dataframe(
                df_history,
                column_config={
                    "Jumlah Dibayar": st.column_config.NumberColumn("Jumlah Dibayar", format="Rp %,.0f")
                },
                hide_index=True,
                use_container_width=True
            )
            
            if st.button("Hapus Riwayat Pembayaran"):
                HISTORY_FILE.unlink()
                st.rerun()
        else:
            st.info("Belum ada riwayat pembayaran tercatat.")
    else:
        st.info("Riwayat pembayaran belum ada.")

with tabs[4]:
    sup_menu = st.selectbox("Kategori Supplier", list(sup_files.keys()), key="sb_sup")
    path_sup = BASE_DIR / sup_files[sup_menu]

    if path_sup.exists():
        data_sup = pd.read_csv(path_sup)
        data_sup.columns = data_sup.columns.str.strip()

        normalized_cols = {}
        for col in data_sup.columns:
            key = col.lower().strip()
            if "supplier" in key:
                normalized_cols[col] = COL_SUP
            elif "alamat" in key:
                normalized_cols[col] = COL_ALM
            else:
                normalized_cols[col] = col

        data_sup.rename(columns=normalized_cols, inplace=True)

        data_sup = data_sup.loc[:, ~data_sup.columns.duplicated()]

    else:
        data_sup = pd.DataFrame(columns=[COL_SUP, COL_ALM])

    for col in [COL_SUP, COL_ALM]:
        if col not in data_sup.columns:
            data_sup[col] = ""

    data_sup = data_sup[[COL_SUP, COL_ALM]].copy()

    event_sup = st.dataframe(
        data_sup,
        hide_index=True,
        use_container_width=True,
        selection_mode="single-row",
        on_select="rerun",
        key="supplier_table"
    )

    selected_rows = event_sup.selection.rows

    if selected_rows:
        idx = selected_rows[0]
        nama_sup = data_sup.iloc[idx][COL_SUP]

        if st.button(f"🗑 Hapus Supplier: {nama_sup}", type="primary"):
            data_sup.drop(index=data_sup.index[idx], inplace=True)
            data_sup.to_csv(path_sup, index=False)
            st.success(f"Supplier '{nama_sup}' berhasil dihapus.")
            st.rerun()

    st.divider()

    with st.form("form_sup", clear_on_submit=True):
        s_nama = st.text_input("Nama Supplier")
        s_alamat = st.text_input("Alamat")

        if st.form_submit_button("Simpan Supplier"):
            if s_nama:
                new_sup = pd.DataFrame([[s_nama, s_alamat]], columns=[COL_SUP, COL_ALM])
                pd.concat([data_sup, new_sup], ignore_index=True).to_csv(path_sup, index=False)
                st.success("Supplier berhasil ditambahkan.")
                st.rerun()