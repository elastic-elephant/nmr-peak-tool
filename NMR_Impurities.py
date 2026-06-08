import streamlit as st
import pandas as pd

# Load Excel file
df = pd.read_excel("NMR_Impurities.xlsx", sheet_name="Shift Table")

st.title("🧪 NMR Peak Finder")

# Inputs
compound = st.text_input("Compound (e.g. acetone)")
solvent = st.selectbox("Solvent", df.columns[3:])  # solvent columns
nucleus = st.selectbox("Nucleus", df.iloc[:,0].unique())

# Process
if compound and solvent and nucleus:

    # Clean ppm column
    ppm = pd.to_numeric(
        df[solvent].astype(str).str.replace("−","-"),
        errors="coerce"
    )

    # Filter
    results = df[
        (df.iloc[:,0] == nucleus) &
        (df.iloc[:,1].str.contains(compound, case=False, na=False)) &
        (ppm.notna())
    ].copy()

    results["ppm"] = ppm

    # Display
    if not results.empty:
        st.subheader("Results")
        st.dataframe(
            results.iloc[:, [1,2]].assign(
                ppm=results["ppm"],
                Multiplicity=results.iloc[:,3]
            )
        )
    else:
        st.warning("No matches found")
