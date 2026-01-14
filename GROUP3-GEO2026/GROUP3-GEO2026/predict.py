import streamlit as st
from model import predict_jumlah
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import stats
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

st.markdown("""
<style>
div[data-testid="stTabs"] { width: 100%; }
div[data-testid="stTabs"] > div > div { display: flex; }
button[data-testid="stTab"] { flex: 1; justify-content: center; font-weight: 600; }
div.block-container { padding-top: 1rem; }
.metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "Revenue Prediction", 
    "Sales Forecasting"
])

with tabs[0]:
    st.subheader("Revenue Prediction Tool")

    st.write("Enter order details to estimate expected revenue.")

    # ---------- Input form ----------

    with st.form("prediction_form"):
        qty = st.number_input("Quantity (QTY)", min_value=1, value=100)
        harga = st.number_input("Unit Price (HARGA)", min_value=1, value=10000)
        satuan = st.selectbox("Unit (SATUAN)", ["pcs", "stell", "paket"])

        submitted = st.form_submit_button("Predict Revenue")

    # ---------- Prediction ----------

    if submitted:
        pred = predict_jumlah(
            qty=qty if qty > 0 else None,
            harga=harga if harga > 0 else None,
            satuan=satuan
        )

        formatted_pred = f"{pred:,.0f}".replace(",", ".")
        st.success(f"Predicted Revenue: **Rp {formatted_pred}**")

with tabs[1]:
    st.subheader("Sales Forcasting (XGBoost - Quarterly)")

    st.markdown("""
    **Format Upload:** File Excel dengan kolom wajib: `TANGGAL PEMESANAN` dan `QTY`.
    **Catatan:** Model ini menggunakan agregasi **Per Kuartal (3 Bulan)** untuk menangkap tren jangka panjang.
    """)

    def create_lagged_features(data, lag=1):
        """Membuat fitur lag untuk time series"""
        lagged_data = data.copy()
        for i in range(1, lag+1):
            lagged_data[f'QTY_{i}'] = lagged_data['QTY'].shift(i)
        return lagged_data

    def run_forecasting(df, forecast_quarters):
        st.write("---")
        st.subheader("1. Preprocessing Data (Quarterly Aggregation)")

        try:
            df['TANGGAL PEMESANAN'] = pd.to_datetime(df['TANGGAL PEMESANAN'], format='%Y-%m-%d', errors='coerce')
        except:
            df['TANGGAL PEMESANAN'] = pd.to_datetime(df['TANGGAL PEMESANAN'], errors='coerce')
        
        df = df.dropna(subset=['TANGGAL PEMESANAN'])

        df['QTY'] = pd.to_numeric(df['QTY'], errors='coerce')
        df = df.dropna(subset=['QTY'])

        df['QUARTER_START'] = df['TANGGAL PEMESANAN'].dt.to_period('Q').dt.to_timestamp()

        qty_by_date = df.groupby('QUARTER_START')['QTY'].sum().reset_index()
        qty_by_date.rename(columns={'QUARTER_START': 'TANGGAL PEMESANAN'}, inplace=True) 
        
        qty_by_date.replace('', np.nan, inplace=True)
        qty_by_date = qty_by_date.dropna()

        st.write("#### Tren Data Historis (Per Kuartal)")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(qty_by_date['TANGGAL PEMESANAN'], qty_by_date['QTY'], label='Quantity', color='red')
        ax.set_title('Quarterly Quantity Trend Over Time (Including Outliers)')
        ax.set_xlabel('Date')
        ax.set_ylabel('Quantity')
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

        qty_by_date_filtered = qty_by_date.copy()
        if len(qty_by_date) > 5: 
            qty_by_date_filtered = qty_by_date[(np.abs(stats.zscore(qty_by_date['QTY'])) < 4)].copy()

        st.subheader("2. Training Model")
        
        LAG = 4 
        
        qty_with_lags = create_lagged_features(qty_by_date_filtered, LAG)
        qty_with_lags.dropna(inplace=True)

        if qty_with_lags.empty:
            st.error("Data terlalu sedikit setelah pembersihan & lagging. Butuh minimal 2 tahun data historis.")
            return

        X = qty_with_lags.drop(columns=['QTY', 'TANGGAL PEMESANAN'])
        y = qty_with_lags['QTY']

        X_train, X_test, y_train_log, y_test_log = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        y_train_log = np.log1p(y_train_log)
        y_test_log = np.log1p(y_test_log)

        model_xgb = xgb.XGBRegressor(
            objective='reg:squarederror',
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5
        )
        
        with st.spinner('Sedang melatih model...'):
            model_xgb.fit(X_train, y_train_log)

        predictions_xgb = model_xgb.predict(X_test)
        rmse_xgb = np.sqrt(mean_squared_error(y_test_log, predictions_xgb))

        y_pred = np.expm1(predictions_xgb)
        y_test_actual = np.expm1(y_test_log)
        dates_test = qty_with_lags.loc[X_test.index, 'TANGGAL PEMESANAN']

        fig2, ax2 = plt.subplots(figsize=(12, 6))
        ax2.plot(dates_test, y_test_actual, label="Actual", color='blue')
        ax2.plot(dates_test, y_pred, label="Predicted", color='orange', linestyle='--')
        ax2.set_title('Validasi: Actual vs Predicted (Test Set)')
        ax2.legend()
        ax2.grid(True)
        ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.xticks(rotation=45)
        st.pyplot(fig2)

        st.subheader(f"3. Forecasting {forecast_quarters} Kuartal ke Depan")

        all_predictions_log = model_xgb.predict(X)
        all_predictions = np.expm1(all_predictions_log)
        
        results_df = qty_with_lags[['TANGGAL PEMESANAN', 'QTY']].copy()
        results_df['Predicted QTY'] = all_predictions
        results_df = results_df.rename(columns={'QTY': 'Actual QTY'})

        last_date = results_df['TANGGAL PEMESANAN'].max()

        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_quarters, freq='QS') 

        future_forecasts = []
        
     
        current_lag_features = list(qty_with_lags.iloc[-1, 2:].values) 

        
        for date in future_dates:
            features_df = pd.DataFrame([current_lag_features], columns=[f'QTY_{i}' for i in range(1, LAG + 1)])
            
            
            next_qty_log_pred = model_xgb.predict(features_df)[0]
      
            next_qty_pred = np.expm1(next_qty_log_pred)
            
            if next_qty_pred < 0: next_qty_pred = 0 
            
            future_forecasts.append(next_qty_pred)
    
            current_lag_features.pop(0) 
            current_lag_features.append(next_qty_pred)

       
        future_df = pd.DataFrame({'TANGGAL PEMESANAN': future_dates, 'Forecasted QTY': future_forecasts})
        combined_df = pd.merge(results_df, future_df, on='TANGGAL PEMESANAN', how='outer')
        combined_df = combined_df.sort_values(by='TANGGAL PEMESANAN').reset_index(drop=True)
     
        combined_df['Model Output'] = combined_df['Predicted QTY'].fillna(combined_df['Forecasted QTY'])


        fig3, ax3 = plt.subplots(figsize=(14, 7))
        ax3.plot(combined_df['TANGGAL PEMESANAN'], combined_df['Actual QTY'], label='Actual QTY', color='blue')
        ax3.plot(combined_df['TANGGAL PEMESANAN'], combined_df['Model Output'], label='Model Output (Predicted + Forecasted)', color='red', linestyle='--')
        
        ax3.set_title(f'Actual vs. Model Output Quantity Over Time ({forecast_quarters} Quarters Horizon)')
        ax3.set_xlabel('Date')
        ax3.set_ylabel('Quantity')
        ax3.legend()
        ax3.grid(True)
        ax3.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax3.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.xticks(rotation=45)
        st.pyplot(fig3)
        
        if 'Forecasted QTY' in future_df.columns:
            future_df['Forecasted QTY'] = future_df['Forecasted QTY'].round(0).astype(int)

        if 'Model Output' in combined_df.columns:
            combined_df['Model Output'] = combined_df['Model Output'].round(0)

        st.write("### Detail Data Forecast (Masa Depan)")
        col_a, col_b = st.columns([1, 2])
        with col_a:
            st.dataframe(future_df)
        with col_b:
            csv = combined_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Full Result CSV", csv, "sales_forecast_quarterly.csv", "text/csv")

  
    col_input1, col_input2 = st.columns([1, 1])
    
    with col_input1:
        uploaded_file = st.file_uploader("Upload File Excel", type=["xlsx", "xls"])
    
    with col_input2:
    
        forecast_horizon = st.slider("Prediksi berapa Kuartal ke depan?", 1, 12, 4, step=1)
        st.caption("1 Kuartal = 3 Bulan. (Default 4 = 1 Tahun)")
        st.write("") 
        run_btn = st.button("Run Forecast", use_container_width=True)


    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            
            required = ['TANGGAL PEMESANAN', 'QTY']
            missing = [c for c in required if c not in df.columns]
            
            if missing:
                st.error(f"Kolom tidak ditemukan: {', '.join(missing)}")
            else:
                if run_btn:
                    run_forecasting(df, forecast_horizon)
                else:
                    st.write("Preview Data Awal:")
                    st.dataframe(df.head(), use_container_width=True)
                    
        except Exception as e:
            st.error(f"Error membaca file: {e}")