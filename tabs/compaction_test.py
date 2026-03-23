import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

def run():

    st.header("Standard Proctor Compaction Test")
    st.caption("As per IS 2720 (Part 7): 1980")

    # --------------------------------------------------
    # PROCEDURE SECTION
    # --------------------------------------------------
    with st.expander("📘 Test Procedure"):
        procedure_text = """
1. Take about 3 kg of air-dried soil sample.
2. Add calculated quantity of water and mix thoroughly.
3. Compact soil into mould in 3 layers with 25 blows each.
4. Determine bulk density.
5. Determine moisture content.
6. Repeat for different water contents.
7. Plot Moisture Content vs Dry Density curve.
8. Determine OMC and MDD from peak of curve.
"""
        st.markdown(procedure_text)

    # --------------------------------------------------
    # FORMULA SECTION
    # --------------------------------------------------
    with st.expander("📐 Formulas Used"):
        formula_text = """
Bulk Density (γ) = Weight of Compacted Soil / Volume of Mould

Dry Density (γd) = γ / (1 + w)

Where:
γ  = Bulk Density (g/cc)
γd = Dry Density (g/cc)
w  = Water Content (decimal)

Optimum Moisture Content (OMC) = Water content at Maximum Dry Density
Maximum Dry Density (MDD) = Peak value of Dry Density
"""
        st.markdown(formula_text)

    st.markdown("---")

    # --------------------------------------------------
    # INPUT SECTION
    # --------------------------------------------------
    st.subheader("📊 Enter Test Data")

    default_data = {
        "Water Content (%)": [10, 12, 14, 16, 18],
        "Bulk Density (g/cc)": [1.60, 1.72, 1.78, 1.76, 1.72]
    }

    df = pd.DataFrame(default_data)
    edited_df = st.data_editor(df, num_rows="dynamic")

    # --------------------------------------------------
    # CALCULATION
    # --------------------------------------------------
    if st.button("📈 Compute Compaction Results"):

        try:
            edited_df["Dry Density (g/cc)"] = (
                edited_df["Bulk Density (g/cc)"] /
                (1 + edited_df["Water Content (%)"] / 100)
            )

            opt_idx = edited_df["Dry Density (g/cc)"].idxmax()
            omc = edited_df.loc[opt_idx, "Water Content (%)"]
            mdd = edited_df.loc[opt_idx, "Dry Density (g/cc)"]

            st.success(f"Optimum Moisture Content (OMC) = {omc:.2f} %")
            st.success(f"Maximum Dry Density (MDD) = {mdd:.3f} g/cc")

            # --------------------------------------------------
            # CONCLUSION
            # --------------------------------------------------
            if mdd < 1.6:
                conclusion = "Soil has low compaction characteristics."
            elif mdd < 1.9:
                conclusion = "Soil has moderate compaction characteristics."
            else:
                conclusion = "Soil has good compaction characteristics."

            st.info(conclusion)

            # --------------------------------------------------
            # GRAPH
            # --------------------------------------------------
            fig, ax = plt.subplots()
            ax.plot(
                edited_df["Water Content (%)"],
                edited_df["Dry Density (g/cc)"],
                marker='o'
            )
            ax.set_xlabel("Water Content (%)")
            ax.set_ylabel("Dry Density (g/cc)")
            ax.set_title("Compaction Curve")
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

        except Exception as e:
            st.error(f"Calculation error: {e}")
            return None

    return None