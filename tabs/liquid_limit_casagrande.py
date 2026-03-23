import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

def run():
    st.subheader("Liquid Limit - Casagrande Method (IS 2720 Part 5)")

    # ---------------- PROCEDURE ----------------
    procedure_text = """
1. Take soil passing 425 µm sieve.
2. Mix with water to form paste.
3. Place in Casagrande cup.
4. Cut groove and apply blows.
5. Record blows required to close groove.
6. Repeat for different moisture contents.
7. Plot flow curve (log scale).
8. Determine LL at 25 blows.
"""

    st.markdown("### 🧪 Test Procedure")
    st.markdown(procedure_text)

    # ---------------- SAFE FUNCTION ----------------
    def calculate_moisture_content(w1, w2, w3):

        # Invalid order
        if not (w2 >= w3 >= w1):
            return np.nan

        denominator = (w3 - w1)

        # ✅ FIX: prevent division by zero
        if denominator == 0:
            return np.nan

        return ((w2 - w3) / denominator) * 100

    # ---------------- INPUT ----------------
    num_samples = st.number_input("Number of Trials", 2, 10, 4)

    if "trial_data" not in st.session_state:
        st.session_state.trial_data = {}

    # Initialize trials
    for i in range(num_samples):
        key = f"trial_{i+1}"
        if key not in st.session_state.trial_data:
            st.session_state.trial_data[key] = {
                "Number of Blows":0.0,
                "W1":0.0,
                "W2":0.0,
                "W3":0.0,
                "Moisture Content (%)":np.nan
            }

    # ---------------- INPUT FIELDS ----------------
    for i in range(num_samples):
        key = f"trial_{i+1}"

        st.markdown(f"### Trial {i+1}")

        st.session_state.trial_data[key]["Number of Blows"] = st.number_input(
            f"Blows {i+1}", key=f"b{i}", min_value=0.0
        )

        st.session_state.trial_data[key]["W1"] = st.number_input(
            f"W1 (Empty Cup) {i+1}", key=f"w1{i}", min_value=0.0
        )

        st.session_state.trial_data[key]["W2"] = st.number_input(
            f"W2 (Wet Soil) {i+1}", key=f"w2{i}", min_value=0.0
        )

        st.session_state.trial_data[key]["W3"] = st.number_input(
            f"W3 (Dry Soil) {i+1}", key=f"w3{i}", min_value=0.0
        )

        # Calculate MC safely
        mc = calculate_moisture_content(
            st.session_state.trial_data[key]["W1"],
            st.session_state.trial_data[key]["W2"],
            st.session_state.trial_data[key]["W3"]
        )

        st.session_state.trial_data[key]["Moisture Content (%)"] = mc

        if np.isnan(mc):
            st.error(f"Trial {i+1}: Invalid input (check W1, W2, W3)")
        else:
            st.info(f"Moisture Content = {mc:.2f}%")

    # ---------------- CALCULATE ----------------
    if st.button("Calculate Liquid Limit"):

        df = pd.DataFrame.from_dict(
            st.session_state.trial_data, orient='index'
        ).reset_index(drop=True)

        # ✅ Filter valid data
        df_filtered = df[
            (df["Number of Blows"] > 0) &
            (~df["Moisture Content (%)"].isna())
        ]

        if len(df_filtered) < 2:
            st.error("Enter at least 2 valid data points")
            return None

        try:
            x = np.log10(df_filtered["Number of Blows"])
            y = df_filtered["Moisture Content (%)"]

            coeffs = np.polyfit(x, y, 1)
            a, b = coeffs

            LL = a * np.log10(25) + b

            # ---------------- GRAPH ----------------
            fig, ax = plt.subplots()
            ax.scatter(x, y)

            x_line = np.linspace(min(x), max(x), 100)
            ax.plot(x_line, a*x_line + b)

            ax.plot(np.log10(25), LL, 'ro')

            ax.set_xlabel("Log(Number of Blows)")
            ax.set_ylabel("Moisture Content (%)")
            ax.set_title("Flow Curve")

            st.pyplot(fig)

            # Save image
            img_buf = BytesIO()
            fig.savefig(img_buf, format="png")
            img_buf.seek(0)

            # ---------------- STORE RESULTS ----------------
            return {
                "procedure": procedure_text,
                "data": df,
                "graph": img_buf,
                "Liquid Limit (LL)": f"{LL:.2f}%",
                "Remarks": "Liquid Limit determined at 25 blows using flow curve"
            }

        except np.linalg.LinAlgError:
            st.error("Curve fitting failed (check inputs)")
            return None

        except Exception as e:
            st.error(f"Error: {e}")
            return None

    return None