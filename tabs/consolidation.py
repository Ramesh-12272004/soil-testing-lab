import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

def run():

    st.header("Consolidation Test")
    st.caption("As per IS 2720 (Part 15): 1986")

    # --------------------------------------------------
    # PROCEDURE
    # --------------------------------------------------
    with st.expander("📘 Test Procedure"):
        procedure_text = """
1. Prepare undisturbed soil sample in consolidation ring.
2. Measure initial height and diameter.
3. Apply load increments in stages.
4. Record dial gauge readings at each increment.
5. Compute settlement and void ratio.
6. Plot e – log(P) curve.
7. Determine Compression Index (Cc).
"""
        st.markdown(procedure_text)

    # --------------------------------------------------
    # FORMULAS
    # --------------------------------------------------
    with st.expander("📐 Formulas Used"):
        formula_text = """
Area of Sample:
A = (π/4) × d²

Settlement (mm):
= (Final Reading − Initial Reading) × Least Count

Strain:
= Compression / Initial Height

Void Ratio:
e = e₀ − Strain × (1 + e₀)

Compression Index (Cc):
Slope of e – log(P) curve in virgin compression region

Coefficient of Volume Compressibility (mv):
mv = Δe / [(1 + e₀) × Δσ]
"""
        st.markdown(formula_text)

    st.markdown("---")

    # --------------------------------------------------
    # INPUT SECTION
    # --------------------------------------------------
    st.subheader("🔧 Sample Details")

    h0 = st.number_input("Initial Height (cm)", value=2.0, min_value=0.1)
    d = st.number_input("Diameter (cm)", value=6.0, min_value=0.1)
    dial_lc = st.number_input("Dial Gauge Least Count (mm/div)", value=0.01)
    e0 = st.number_input("Initial Void Ratio (e₀)", value=0.9, min_value=0.0)

    A = (np.pi / 4) * d ** 2
    st.info(f"Cross-sectional Area = {A:.2f} cm²")

    st.subheader("📊 Load Increment Data")

    num_readings = st.number_input(
        "Number of Load Increments",
        min_value=2,
        max_value=20,
        value=6
    )

    loads, init_readings, final_readings = [], [], []

    for i in range(num_readings):
        col1, col2, col3 = st.columns(3)
        with col1:
            load = st.number_input(
                f"Load (kg/cm²) - {i+1}",
                key=f"load_{i}"
            )
        with col2:
            init = st.number_input(
                f"Initial Reading (div) - {i+1}",
                key=f"init_{i}"
            )
        with col3:
            final = st.number_input(
                f"Final Reading (div) - {i+1}",
                key=f"final_{i}"
            )

        loads.append(load)
        init_readings.append(init)
        final_readings.append(final)

    # --------------------------------------------------
    # CALCULATION
    # --------------------------------------------------
    if st.button("📈 Calculate Consolidation Results"):

        try:
            df = pd.DataFrame({
                "Load (kg/cm²)": loads,
                "Initial Reading (div)": init_readings,
                "Final Reading (div)": final_readings
            })

            df["Settlement (mm)"] = (
                (df["Final Reading (div)"] -
                 df["Initial Reading (div)"]) * dial_lc
            )

            df["Compression (cm)"] = df["Settlement (mm)"] / 10
            df["Strain"] = df["Compression (cm)"] / h0
            df["Void Ratio (e)"] = e0 - df["Strain"] * (1 + e0)

            df = df[df["Void Ratio (e)"] > 0]

            df["log(Load)"] = np.log10(df["Load (kg/cm²)"])

            st.subheader("📋 Result Table")
            st.dataframe(df.style.format(precision=4))

            # --------------------------------------------------
            # GRAPH
            # --------------------------------------------------
            fig, ax = plt.subplots()
            ax.plot(df["log(Load)"], df["Void Ratio (e)"], marker='o')
            ax.set_xlabel("log(Load)")
            ax.set_ylabel("Void Ratio (e)")
            ax.set_title("e – log(P) Curve")
            ax.invert_yaxis()
            ax.grid(True)

            image_stream = BytesIO()
            plt.savefig(image_stream, format="png")
            image_stream.seek(0)

            st.pyplot(fig)

            # --------------------------------------------------
            # Compression Index (Cc)
            # --------------------------------------------------
            if len(df) >= 3:
                slope, intercept = np.polyfit(
                    df["log(Load)"].iloc[-3:],
                    df["Void Ratio (e)"].iloc[-3:], 1
                )
                Cc = -slope
                st.success(f"Compression Index (Cc) ≈ {Cc:.4f}")
            else:
                Cc = None
                st.warning("Not enough points to calculate Cc.")

            # --------------------------------------------------
            # Coefficient of Volume Compressibility (mv)
            # --------------------------------------------------
            if len(df) >= 2:
                delta_e = df["Void Ratio (e)"].iloc[1] - df["Void Ratio (e)"].iloc[0]
                delta_sigma = df["Load (kg/cm²)"].iloc[1] - df["Load (kg/cm²)"].iloc[0]
                mv = delta_e / ((1 + e0) * delta_sigma)
                st.success(f"Coefficient of Volume Compressibility (mv) ≈ {mv:.6f} cm²/kg")
            else:
                mv = None
                st.warning("Not enough data to calculate mv.")

            # --------------------------------------------------
            # CONCLUSION
            # --------------------------------------------------
            if Cc:
                if Cc < 0.1:
                    conclusion = "Soil has low compressibility."
                elif Cc < 0.3:
                    conclusion = "Soil has moderate compressibility."
                else:
                    conclusion = "Soil has high compressibility."
                st.info(conclusion)
            else:
                conclusion = "Insufficient data for compressibility classification."

            # --------------------------------------------------
            # RETURN FOR COMBINED REPORT
            # --------------------------------------------------
            return {
                "data": df,
                "graph": image_stream,
                "procedure": procedure_text,
                "formulas": formula_text
            }

        except Exception as e:
            st.error(f"Calculation Error: {e}")
            return None

    return None