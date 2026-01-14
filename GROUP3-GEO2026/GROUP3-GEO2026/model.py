import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from pathlib import Path

# ---------- Load & train model ONCE ----------
BASE_DIR = Path(__file__).resolve().parent.parent
FILE_PATH = BASE_DIR / "GEO_data.xlsx"
df = pd.read_excel(FILE_PATH)

# Clean numeric columns
for col in ["QTY", "HARGA", "JUMLAH"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df[df["JUMLAH"].notna() & (df["JUMLAH"] > 0)]
df = df[df["QTY"].notna() & (df["QTY"] > 0)]
df = df.reset_index(drop=True)

# Encode SATUAN
df = pd.get_dummies(df, columns=["SATUAN"], drop_first=True)

# Impute HARGA
price_imputer = SimpleImputer(strategy="median")
df["HARGA"] = price_imputer.fit_transform(df[["HARGA"]])

# Log features
df["log_QTY"] = np.log(df["QTY"])
df["log_HARGA"] = np.log(df["HARGA"])
df["log_JUMLAH"] = np.log(df["JUMLAH"])

# Feature list
satuan_columns = [c for c in df.columns if c.startswith("SATUAN_")]
features = ["log_QTY", "log_HARGA"] + satuan_columns

X = df[features]
y = df["log_JUMLAH"]

# Train model
model = LinearRegression()
model.fit(X, y)

# Store medians for inference
log_qty_median = np.log(df["QTY"].median())
log_harga_median = np.log(df["HARGA"].median())

# ---------- Prediction function ----------

def predict_jumlah(qty=None, harga=None, satuan="pcs"):
    log_qty = np.log(qty) if qty is not None else log_qty_median
    log_harga = np.log(harga) if harga is not None else log_harga_median

    input_dict = {
        "log_QTY": log_qty,
        "log_HARGA": log_harga,
    }

    for col in satuan_columns:
        input_dict[col] = 0

    if satuan != "pcs":
        col_name = f"SATUAN_{satuan}"
        if col_name in input_dict:
            input_dict[col_name] = 1

    input_df = pd.DataFrame([input_dict])

    log_pred = model.predict(input_df)[0]
    return float(np.exp(log_pred))
