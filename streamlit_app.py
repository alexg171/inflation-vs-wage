import os
import sys
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from analysis import chart1_plotly, chart2_plotly  # noqa: E402

st.set_page_config(page_title="Inflation vs Wages", layout="wide")

st.title("Have Wages Kept Up With Inflation?")
st.markdown(
    "Interactive charts using data from [FRED](https://fred.stlouisfed.org/) "
    "and [BLS](https://www.bls.gov/developers/)."
)

tab1, tab2 = st.tabs(["Wages vs CPI", "CPI by Category"])

with tab1:
    st.subheader("Nominal Wages, CPI, and Real Wages (Jan 2019 = 100)")
    fig1 = chart1_plotly()
    if fig1:
        st.plotly_chart(fig1, use_container_width=True)

with tab2:
    st.subheader("Price Change by Category vs. Overall Inflation")
    fig2 = chart2_plotly()
    if fig2:
        st.plotly_chart(fig2, use_container_width=True)
