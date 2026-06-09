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

    ppm_series = clean_ppm(df[solvent])

    results = df[
        (df["Nucleus"] == nucleus) &
        (ppm_series.notna()) &
        (abs(ppm_series - ppm_input) <= tolerance)
    ].copy()

    results["ppm"] = ppm_series.round(2)  # ✅ round
    results["Δ ppm"] = abs(results["ppm"] - ppm_input).round(2)

    results = results.sort_values("Δ ppm")

    st.write("Matches")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

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

    compound = st.text_input("Compound name")
    solvent2 = st.selectbox("Solvent", df.columns[4:], key="solvent2")
    nucleus2 = st.selectbox("Nucleus", df["Nucleus"].dropna().unique(), key="nuc2")

    ppm_series2 = clean_ppm(df[solvent2])

    results2 = df[
        (df["Nucleus"] == nucleus2) &
        (df["Compound"].str.contains(compound, case=False, na=False)) &
        (ppm_series2.notna())
    ].copy()

    results2["ppm"] = ppm_series2.round(2)  # ✅ round

    results2 = results2.sort_values("ppm")

    st.write("Expected peaks")
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("---")

    if not results2.empty:
        st.dataframe(
            results2[["Compound", "Group", "ppm", "Multiplicity"]],
            use_container_width=True  # ✅ full width
        )
    else:
        if compound:
            st.info("No matches found")
