import streamlit as st
import pandas as pd

# --- Page config (WIDER LAYOUT) ---
st.set_page_config(layout="wide")

# Load data
df = pd.read_excel("NMR_Impurities.xlsx", sheet_name="Shift Table")

# Clean column names
df.columns = ["Nucleus", "Compound", "Group", "Multiplicity", *df.columns[4:]]

# Remove NaN from nucleus options
df = df[df["Nucleus"].notna()]

st.title("NMR Impurity Finder")

# --- Helper function ---
def clean_ppm(series):
    return pd.to_numeric(
        series.astype(str)
        .str.replace("−", "-", regex=False)
        .str.replace("–", "-", regex=False)
        .str.replace(r"[a-zA-Z]", "", regex=True)
        .str.split("-").str[0]
        .str.strip(),
        errors="coerce"
    )

# --- Layout with spacing ---
col1, spacer, col2 = st.columns([1, 0.1, 1])

# =========================
# LEFT: ppm → compound
# =========================
with col1:
    st.subheader("ppm → Compound")

    ppm_input = st.number_input("ppm", value=2.10)
    tolerance = st.number_input("Tolerance", value=0.05)
    solvent = st.selectbox("Solvent", df.columns[4:], key="solvent1")
    nucleus = st.selectbox("Nucleus", df["Nucleus"].dropna().unique(), key="nuc1")

    EPS = 1e-6

    ppm_series = clean_ppm(df[solvent])

    # 🔥 attach BEFORE filtering
    df_temp = df.copy()
    df_temp["ppm"] = ppm_series
    df_temp["Δ ppm"] = abs(ppm_series - ppm_input)

    # ✅ now filter correctly
    results = df_temp[
        (df_temp["Nucleus"] == nucleus) &
        (df_temp["ppm"].notna()) &
        (df_temp["Δ ppm"] <= (tolerance + EPS))
    ].copy()

    # ✅ sort BEFORE converting to string
    results = results.sort_values("Δ ppm")
    
    # ✅ format AFTER everything
    results["ppm"] = results["ppm"].map(lambda x: f"{x:.2f}")
    results["Δ ppm"] = results["Δ ppm"].map(lambda x: f"{x:.2f}")

    st.write("Matches")

    if not results.empty:
        styled = results[["Compound", "Group", "ppm", "Multiplicity", "Δ ppm"]]\
    .style.highlight_min(subset=["Δ ppm"], color="lightgreen")

        st.dataframe(styled, use_container_width=True)  # ✅ no horizontal scroll
    else:
        st.info("No matches found")


# =========================
# RIGHT: compound → ppm
# =========================
with col2:
    st.subheader("Compound → ppm")

    compound = st.selectbox("Compound", compound_list)
    solvent2 = st.selectbox("Solvent", df.columns[4:], key="solvent2")
    nucleus2 = st.selectbox("Nucleus", df["Nucleus"].dropna().unique(), key="nuc2")

    ppm_series2 = clean_ppm(df[solvent2])

    results2 = df[
    (df["Nucleus"] == nucleus2) &
    (df["Compound"] == compound) &
    (ppm_series2.notna())
].copy()

    results2["ppm_num"] = ppm_series2
    results2 = results2.sort_values("ppm_num")

    results2["ppm"] = results2["ppm_num"].map(lambda x: f"{x:.2f}")
    
    st.write("Expected peaks")

    if not results2.empty:
        st.dataframe(
            results2[["Compound", "Group", "ppm", "Multiplicity"]],
            use_container_width=True  # ✅ full width
        )
    else:
        if compound:
            st.info("No matches found")
