import streamlit as st
import pandas as pd
from datetime import date
import os

FILE_KARYAWAN = 'db_karyawan.csv'
FILE_GAJI = 'db_gaji.csv'

def init_csv():
    """Memastikan file CSV tersedia dengan header yang benar"""
    if not os.path.exists(FILE_KARYAWAN):
        pd.DataFrame(columns=[
            "Nama Lengkap", "No KTP", "Posisi", "Kontak", "Tanggal Masuk", "Alamat"
        ]).to_csv(FILE_KARYAWAN, index=False)
        
    if not os.path.exists(FILE_GAJI):
        pd.DataFrame(columns=[
            "Periode", "Tipe", "Tgl Input", "Jatuh Tempo", "Nama Karyawan", 
            "Gaji Pokok", "Tunjangan", "Komisi", "Total Gross", 
            "Potongan", "Iuran", "Tabungan HR", "Total Deduction", "THP (Total)"
        ]).to_csv(FILE_GAJI, index=False)

def load_data_karyawan():
    """Load data karyawan dari CSV"""
    if os.path.exists(FILE_KARYAWAN):
        try:
            df = pd.read_csv(FILE_KARYAWAN)
            return df.to_dict('records')
        except:
            return []
    return []

def load_data_gaji():
    """Load data gaji dari CSV"""
    if os.path.exists(FILE_GAJI):
        try:
            df = pd.read_csv(FILE_GAJI)
            return df.to_dict('records')
        except:
            return []
    return []

def save_to_csv(data, filename):
    """Simpan list dictionary ke CSV (Menulis Permanen)"""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

init_csv()

st.session_state['data_karyawan'] = load_data_karyawan()
st.session_state['data_gaji'] = load_data_gaji()

st.markdown("""
<style>
div[data-testid="stTabs"] { width: 100%; }
div[data-testid="stTabs"] > div > div { display: flex; }
button[data-testid="stTab"] { flex: 1; justify-content: center; font-weight: 600; }
div.block-container { padding-top: 1rem; }
.metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

tabs = st.tabs(["Employee", "Salary", "Tabungan Hari Raya"])

with tabs[0]:
    with st.form("form_karyawan", clear_on_submit=True):
        st.write("**Tambah Karyawan Baru**")
        col1, col2 = st.columns(2)
        
        with col1:
            nama = st.text_input("Nama Lengkap")
            ktp = st.text_input("No. KTP", max_chars=16) 
            posisi = st.text_input("Posisi / Jabatan")
        
        with col2:
            kontak = st.text_input("No. HP / Kontak")
            tgl_masuk = st.date_input("Tanggal Masuk", value=date.today())
            alamat = st.text_area("Alamat Domisili", height=105) 
            
        submitted = st.form_submit_button("Simpan Data Karyawan", use_container_width=True)
        
        if submitted:
            if nama and ktp and posisi: 
                karyawan_baru = {
                    "Nama Lengkap": nama,
                    "No KTP": ktp,
                    "Posisi": posisi,
                    "Kontak": kontak,
                    "Tanggal Masuk": str(tgl_masuk), 
                    "Alamat": alamat
                }
              
              
                st.session_state['data_karyawan'].append(karyawan_baru)
                
                
                save_to_csv(st.session_state['data_karyawan'], FILE_KARYAWAN)
                
                st.success(f"Berhasil menambahkan karyawan: {nama}")
                st.rerun() 
            else:
                st.error("Mohon lengkapi Nama, No KTP, dan Posisi!")

    st.markdown("---")
    st.subheader(f"Daftar Karyawan ({len(st.session_state['data_karyawan'])})")
    
    if len(st.session_state['data_karyawan']) > 0:
        df_karyawan = pd.DataFrame(st.session_state['data_karyawan'])
        st.dataframe(df_karyawan, use_container_width=True)
    else:
        st.info("Belum ada data karyawan.")


with tabs[1]:
    if len(st.session_state['data_karyawan']) == 0:
        st.warning("Belum ada data karyawan. Silakan input data di Tab 'Employee' terlebih dahulu.")
    else:
        df_karyawan = pd.DataFrame(st.session_state['data_karyawan'])
        list_nama_karyawan = df_karyawan['Nama Lengkap'].tolist()

        with st.form("form_salary", clear_on_submit=True):
            st.write("### Informasi Periode & Pembayaran")
            
            col_a1, col_a2, col_a3 = st.columns(3)
            with col_a1:
                pay_type = st.selectbox("Payment Type", ["Monthly", "Non-Monthly", "Yearly"])
            with col_a2:
                bulan = st.selectbox("Bulan", [
                    "January", "February", "March", "April", "May", "June", 
                    "July", "August", "September", "October", "November", "December"
                ])
            with col_a3:
                curr_year = date.today().year
                tahun_list = [curr_year - i for i in range(2)] + [curr_year + i for i in range(1, 6)]
                tahun_list.sort()
                tahun = st.selectbox("Tahun", tahun_list, index=tahun_list.index(curr_year))

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                tgl_transaksi = st.date_input("Tanggal Transaksi", value=date.today())
            with col_b2:
                tgl_jatuh_tempo = st.date_input("Tanggal Jatuh Tempo", value=date.today())

            st.markdown("---")
            st.write("### Salary Detail")
            
            nama_karyawan = st.selectbox("Nama Lengkap Karyawan", list_nama_karyawan)

            c_inc, c_ded = st.columns(2)
            with c_inc:
                st.info("**Gross Income (Pendapatan)**")
                gaji_pokok = st.number_input("Gaji Pokok", min_value=0, step=100000, format="%d")
                tunjangan = st.number_input("Tunjangan", min_value=0, step=50000, format="%d")
                komisi = st.number_input("Komisi / Bonus", min_value=0, step=50000, format="%d")
                total_gross = gaji_pokok + tunjangan + komisi
                st.markdown(f"**Total Gross: Rp {total_gross:,.0f}**")

            with c_ded:
                st.error("**Deduction (Potongan)**")
                potongan_gaji = st.number_input("Pengurangan Gaji (Absen/Sanksi)", min_value=0, step=10000, format="%d")
                iuran = st.number_input("Iuran Bulanan (BPJS/Koperasi)", min_value=0, step=10000, format="%d")
                thr_saving = st.number_input("Tabungan Hari Raya", min_value=0, step=10000, format="%d")
                total_deduction = potongan_gaji + iuran + thr_saving
                st.markdown(f"**Total Deduction: Rp {total_deduction:,.0f}**")

            st.markdown("---")
            submitted_gaji = st.form_submit_button("Hitung & Simpan Data Gaji", use_container_width=True)

            if submitted_gaji:
                grand_total = total_gross - total_deduction
                
                data_gaji_baru = {
                    "Periode": f"{bulan} {tahun}",
                    "Tipe": pay_type,
                    "Tgl Input": str(tgl_transaksi), 
                    "Jatuh Tempo": str(tgl_jatuh_tempo), 
                    "Nama Karyawan": nama_karyawan,
                    "Gaji Pokok": gaji_pokok,
                    "Tunjangan": tunjangan,
                    "Komisi": komisi,
                    "Total Gross": total_gross,
                    "Potongan": potongan_gaji,
                    "Iuran": iuran,
                    "Tabungan HR": thr_saving,
                    "Total Deduction": total_deduction,
                    "THP (Total)": grand_total
                }
                
              
                st.session_state['data_gaji'].append(data_gaji_baru)
                
                
                save_to_csv(st.session_state['data_gaji'], FILE_GAJI)
                
                st.success(f"Data Gaji {nama_karyawan} berhasil disimpan!")
                st.metric(label="Total Take Home Pay (THP)", value=f"Rp {grand_total:,.0f}")
                st.rerun()

        st.subheader("Riwayat Penggajian")
        if len(st.session_state['data_gaji']) > 0:
            df_gaji = pd.DataFrame(st.session_state['data_gaji'])
            st.dataframe(df_gaji, use_container_width=True)
            
            csv_gaji = df_gaji.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data Gaji", csv_gaji, "payroll_data.csv", "text/csv")

with tabs[2]:
   
    if len(st.session_state['data_gaji']) > 0:
        # Load Data Gaji
        df = pd.DataFrame(st.session_state['data_gaji'])
        
        # 2. PROSES GROUPING & SUM
        # Mengelompokkan berdasarkan Nama, lalu menjumlahkan kolom 'Tabungan HR'
        # Hasilnya adalah tabel ringkasan
        df_thr = df.groupby('Nama Karyawan')[['Tabungan HR']].sum().reset_index()
        
        # Urutkan dari yang terbanyak
        df_thr = df_thr.sort_values(by='Tabungan HR', ascending=False)
        
        # 3. TAMPILKAN RINGKASAN TOTAL
        st.subheader("Rekapitulasi Total Tabungan")
        
        # Buat kolom baru format Rupiah (String) agar enak dilihat di tabel
        df_thr['Total Terkumpul'] = df_thr['Tabungan HR'].apply(lambda x: f"Rp {x:,.0f}")
        
        # Tampilkan tabel (Hanya Nama & Total)
        st.dataframe(
            df_thr[['Nama Karyawan', 'Total Terkumpul']], 
            use_container_width=True,
            hide_index=True
        )
        
        # 4. FITUR DETAIL (Melihat rincian per orang)
        st.divider()
        st.subheader("Rincian Detail per Karyawan")
        
        col_detail1, col_detail2 = st.columns([1, 2])
        
        with col_detail1:
            # Dropdown pilih nama
            pilih_nama_thr = st.selectbox("Pilih Karyawan:", df_thr['Nama Karyawan'].unique())
            
            # Hitung total individu
            total_individu = df_thr[df_thr['Nama Karyawan'] == pilih_nama_thr]['Tabungan HR'].values[0]
            st.metric(label=f"Total Tabungan {pilih_nama_thr}", value=f"Rp {total_individu:,.0f}")
            
        with col_detail2:
            st.write(f"**Riwayat Setoran THR - {pilih_nama_thr}**")
            
            # Filter DataFrame utama untuk hanya menampilkan karyawan yang dipilih
            # dan hanya kolom yang relevan
            df_detail = df[df['Nama Karyawan'] == pilih_nama_thr][['Periode', 'Tgl Input', 'Tabungan HR']]
            
            # Format rupiah di tabel detail juga
            df_detail['Tabungan HR'] = df_detail['Tabungan HR'].apply(lambda x: f"Rp {x:,.0f}")
            
            st.dataframe(df_detail, use_container_width=True, hide_index=True)
            
    else:
        st.info("Belum ada data gaji yang diinput. Data THR akan otomatis muncul di sini setelah Anda menginput gaji dengan potongan 'Tabungan Hari Raya'.")
    