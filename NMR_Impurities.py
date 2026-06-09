import streamlit as st
import pandas as pd

# Load data
df = pd.read_excel("NMR_Impurities.xlsx", sheet_name="Shift Table")

st.title("🧪 NMR Impurity Finder")

# Inputs (ppm-based search)
ppm_input = st.number_input("Enter ppm value", value=2.10)
tolerance = st.number_input("Tolerance (+/-)", value=0.05)
solvent = st.selectbox("Solvent", df.columns[4:])  # solvents start after multiplicity
nucleus = st.selectbox("Nucleus", df.iloc[:,0].unique())

# Clean ppm column (CRITICAL)
def clean_ppm(series):
    return pd.to_numeric(
        series.astype(str)
        .str.replace("−", "-", regex=False)   # fix minus
        .str.replace("–", "-", regex=False)   # fix dash
        .str.replace(r"[a-zA-Z]", "", regex=True)  # remove letters
        .str.split("-").str[0]   # take FIRST value if range
        .str.strip(),
        errors="coerce"
    )

ppm_series = clean_ppm(df[solvent])

# Apply filtering
results = df[
    (df.iloc[:,0] == nucleus) &
    (ppm_series.notna()) &
    (abs(ppm_series - ppm_input) <= tolerance)
].copy()

results["ppm"] = ppm_series
results["Δ ppm"] = abs(results["ppm"] - ppm_input)

# Sort best matches first
results = results.sort_values("Δ ppm")

# Display
if not results.empty:
    st.subheader("Matches")
    st.dataframe(
        results.iloc[:, [1,2]].assign(
            ppm=results["ppm"],
            Multiplicity=results.iloc[:,3],
            delta=results["Δ ppm"]
        )
    )
else:
    st.warning("No matches found")
