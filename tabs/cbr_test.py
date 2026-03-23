import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

def run():

    st.header("California Bearing Ratio (CBR) Test")
    st.caption("As per IS 2720 (Part 16)")

    # --------------------------------------------------
    # THEORY SECTION
    # --------------------------------------------------
    with st.expander("📘 Test Procedure"):
        procedure_text = """
1. Prepare soil sample at Optimum Moisture Content.
2. Compact soil into CBR mould in layers.
3. Place surcharge weight on specimen.
4. Apply load at rate of 1.25 mm/min.
5. Record dial readings at standard penetrations.
6. Calculate CBR at 2.5 mm and 5.0 mm.
7. Higher value is taken as Final CBR.
"""
        st.markdown(procedure_text)

    with st.expander("📐 Formulas Used"):
        formula_text = """
CBR (%) = (Test Load / Standard Load) × 100

Standard Loads:
• At 2.5 mm penetration = 1370 kg
• At 5.0 mm penetration = 2055 kg

Final CBR = Higher of CBR at 2.5 mm or 5.0 mm
"""
        st.markdown(formula_text)

    st.markdown("---")

    # --------------------------------------------------
    # INPUT SECTION
    # --------------------------------------------------
    st.subheader("🔧 Enter Test Parameters")

    ring_constant = st.number_input(
        "Proving Ring Constant (kg/div)", 
        min_value=0.01, 
        value=1.0
    )

    st.subheader("📊 Enter Load Data")

    default_data = {
        "Penetration (mm)": [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0],
        "Dial Reading (div)": [5, 8, 12, 16, 20, 25, 32, 40]
    }

    df = pd.DataFrame(default_data)
    edited_df = st.data_editor(df, num_rows="dynamic")

    # --------------------------------------------------
    # CALCULATION
    # --------------------------------------------------
    if st.button("📈 Calculate CBR"):

        edited_df["Load (kg)"] = (
            edited_df["Dial Reading (div)"] * ring_constant
        )

        # Check if required penetrations exist
        if 2.5 not in edited_df["Penetration (mm)"].values or \
           5.0 not in edited_df["Penetration (mm)"].values:
            st.error("Penetration values must include 2.5 mm and 5.0 mm.")
            return None

        load_2_5 = edited_df.loc[
            edited_df["Penetration (mm)"] == 2.5,
            "Load (kg)"
        ].values[0]

        load_5_0 = edited_df.loc[
            edited_df["Penetration (mm)"] == 5.0,
            "Load (kg)"
        ].values[0]

        # IS Standard Formula
        cbr_2_5 = (load_2_5 / 1370) * 100
        cbr_5_0 = (load_5_0 / 2055) * 100

        final_cbr = max(cbr_2_5, cbr_5_0)

        edited_df["CBR (%)"] = (
            edited_df["Load (kg)"] / 1370 * 100
        )

        # --------------------------------------------------
        # CONCLUSION
        # --------------------------------------------------
        if final_cbr < 3:
            conclusion = "Very weak subgrade soil. Stabilization recommended."
        elif final_cbr < 7:
            conclusion = "Poor subgrade. Provide thicker pavement."
        elif final_cbr < 15:
            conclusion = "Moderate subgrade. Suitable for flexible pavements."
        else:
            conclusion = "Good subgrade. Suitable for heavy traffic."

        st.success(f"CBR at 2.5 mm = {cbr_2_5:.2f} %")
        st.success(f"CBR at 5.0 mm = {cbr_5_0:.2f} %")
        st.success(f"Final CBR = {final_cbr:.2f} %")
        st.info(conclusion)

        # --------------------------------------------------
        # GRAPH
        # --------------------------------------------------
        fig, ax = plt.subplots()
        ax.plot(
            edited_df["Penetration (mm)"],
            edited_df["Load (kg)"],
            marker="o"
        )
        ax.set_xlabel("Penetration (mm)")
        ax.set_ylabel("Load (kg)")
        ax.set_title("Load vs Penetration Curve")
        ax.grid(True)

        image_stream = BytesIO()
        plt.savefig(image_stream, format="png")
        image_stream.seek(0)

        st.pyplot(fig)

        # --------------------------------------------------
        # RETURN FOR COMBINED REPORT
        # --------------------------------------------------
        return {
            "data": edited_df,
            "graph": image_stream,
            "procedure": procedure_text,
            "formulas": formula_text
        }

    return None