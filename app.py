import streamlit as st
from docx import Document
from docx.shared import Inches
from io import BytesIO
import pandas as pd

# --------------------------
# PAGE CONFIG
# --------------------------
st.set_page_config(
    page_title="ANITS Soil Tests",
    layout="wide"
)

# --------------------------
# CSS
# --------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #e6f0ff, #c9e0ff);
    font-family: "Segoe UI";
}
.center-box {
    text-align: center;
    padding: 40px;
    background: white;
    border-radius: 15px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
}
.header-banner {
    background: linear-gradient(90deg, #0a68cc, #0a4d94);
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    color: white;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------
# IMPORT MODULES
# --------------------------
from tabs import (
    sieve_analysis,
    liquid_limit_casagrande,
    liquid_limit_cone,
    plastic_limit,
    core_cutter,
    specific_gravity,
    constant_head,
    variable_head,
    light_compaction,
    direct_shear,
    ucs_test,
    consolidation,
    cbr_test,
    vane_shear,
    triaxial_test
)

tests = {
    "Sieve Analysis": sieve_analysis,
    "Liquid Limit (Casagrande)": liquid_limit_casagrande,
    "Liquid Limit (Cone)": liquid_limit_cone,
    "Plastic Limit": plastic_limit,
    "Core Cutter": core_cutter,
    "Specific Gravity": specific_gravity,
    "Constant Head": constant_head,
    "Variable Head": variable_head,
    "Light Compaction": light_compaction,
    "Direct Shear": direct_shear,
    "UCS Test": ucs_test,
    "Triaxial Test": triaxial_test,
    "Vane Shear": vane_shear,
    "CBR Test": cbr_test,
    "Consolidation Test": consolidation
}

# --------------------------
# SESSION STATE
# --------------------------
if "app_started" not in st.session_state:
    st.session_state.app_started = False

if "completed_tests" not in st.session_state:
    st.session_state.completed_tests = {}

# --------------------------
# WELCOME SCREEN
# --------------------------
if not st.session_state.app_started:

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.image("assets/anits_logo.png", width=120)
        st.title("Anil Neerukonda Institute of Technology and Sciences")
        st.markdown("#### Department of Civil Engineering")
        st.markdown("### 🧪 Soil Testing & Analysis System")
        st.markdown("> *Understanding soil is the foundation of every great structure.*")

        if st.button("🚀 Start Soil Testing", use_container_width=True):
            st.session_state.app_started = True
            st.rerun()

# --------------------------
# MAIN APP
# --------------------------
else:

    # Sidebar
    st.sidebar.image("assets/anits_logo.png", width=120)
    st.sidebar.title("ANITS Civil Dept")
    st.sidebar.subheader("Soil Tests")

    selected_test = st.sidebar.radio("Select Test", list(tests.keys()))
    selected_module = tests[selected_test]

    # Header
    st.markdown("""
    <div class="header-banner">
        <h2>Soil Tests Analysis Dashboard</h2>
        <p>Professional Civil Engineering Lab System</p>
    </div>
    """, unsafe_allow_html=True)

    # Run selected test
    result = selected_module.run()

    if result is not None:
        st.session_state.completed_tests[selected_test] = result

    # --------------------------
    # REPORT GENERATION
    # --------------------------
    if st.session_state.completed_tests:

        st.sidebar.markdown("---")
        st.sidebar.subheader("📄 Generate Report")

        doc = Document()
        doc.add_heading("ANITS Soil Test Report", 0)

        first_test = True

        for name, result in st.session_state.completed_tests.items():

            if not first_test:
                doc.add_page_break()
            first_test = False

            doc.add_heading(name, 1)

            # Procedure
            if "procedure" in result:
                doc.add_heading("Procedure", 2)
                for line in result["procedure"].split("\n"):
                    doc.add_paragraph(line.strip())

            # Formulas
            if "formulas" in result:
                doc.add_heading("Formulas", 2)
                for line in result["formulas"].split("\n"):
                    doc.add_paragraph(line.strip())

            # Data Table
            if "data" in result and isinstance(result["data"], pd.DataFrame):
                df = result["data"]

                doc.add_heading("Results Data", 2)
                table = doc.add_table(rows=1, cols=len(df.columns))
                table.style = "Table Grid"

                for i, col in enumerate(df.columns):
                    table.rows[0].cells[i].text = str(col)

                for _, row in df.iterrows():
                    cells = table.add_row().cells
                    for i, val in enumerate(row):
                        cells[i].text = str(val)

            # Graph
            if "graph" in result and result["graph"] is not None:
                doc.add_heading("Graph", 2)
                try:
                    result["graph"].seek(0)
                    doc.add_picture(result["graph"], width=Inches(5))
                except:
                    pass

            # Diagram
            if "diagram" in result and result["diagram"] is not None:
                doc.add_heading("Diagram", 2)
                try:
                    result["diagram"].seek(0)
                    doc.add_picture(result["diagram"], width=Inches(4))
                except:
                    pass

            # Additional Results
            for key, value in result.items():
                if isinstance(value, str) and key not in ["procedure", "formulas"]:
                    doc.add_paragraph(f"{key}: {value}")

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.sidebar.download_button(
            label="📥 Download Report",
            data=buffer.getvalue(),
            file_name="ANITS_Soil_Report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )