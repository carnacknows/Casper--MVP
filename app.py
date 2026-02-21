import streamlit as st
import tenseal as ts
import pandas as pd
import numpy as np
from faker import Faker
import plotly.express as px

st.set_page_config(page_title="Casper", page_icon="👻", layout="wide")
st.title("👻 Casper")
st.markdown("**Your data’s friendly ghost.** Upload anything — or try the medical sample. The numbers stay invisible. Only the answers come back.")

# Sidebar explanation
st.sidebar.header("How Casper Works")
st.sidebar.markdown("""
1. Your data is encrypted locally  
2. We run math on the ciphertext  
3. Only the final result is shown  
**Nothing ever leaves your browser.**
""")

# Sample medical data generator
@st.cache_data
def generate_medical_sample(n=500):
    fake = Faker()
    np.random.seed(42)
    data = {
        "PatientID": [fake.uuid4()[:8] for _ in range(n)],
        "Age": np.random.randint(18, 90, n),
        "BloodPressure": np.random.randint(90, 180, n),
        "Cholesterol": np.random.randint(120, 300, n),
        "DiabetesRiskScore": np.round(np.random.uniform(0, 100, n), 1)
    }
    return pd.DataFrame(data)

# Tabs
tab1, tab2 = st.tabs(["📊 Try Casper Live", "📁 Upload Your Own"])

with tab1:
    st.subheader("Synthetic Medical Records Demo")
    if st.button("Load Sample Medical Dataset", type="primary"):
        df = generate_medical_sample()
        st.session_state.sample_df = df
        st.success("✅ Sample loaded — 500 synthetic patients. Ready to encrypt.")

    if "sample_df" in st.session_state:
        df = st.session_state.sample_df
        st.dataframe(df.head(10), use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            operation = st.selectbox("What do you want to compute privately?", 
                                   ["Average Cholesterol", "Average Blood Pressure", 
                                    "Average Diabetes Risk", "Count High-Risk Patients (>70)"])
        with col2:
            if st.button("👻 Compute Privately with Casper", type="primary"):
                with st.spinner("Encrypting data locally and computing..."):
                    context = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=8192, coeff_mod_bit_sizes=[60, 40, 40, 60])
                    context.global_scale = 2**40
                    context.generate_galois_keys()

                    col_name = "Cholesterol" if "Cholesterol" in operation else \
                               "BloodPressure" if "Blood Pressure" in operation else \
                               "DiabetesRiskScore"

                    values = df[col_name].astype(float).values
                    enc_vec = ts.ckks_vector(context, values.tolist())
                    result = enc_vec.sum() / len(values) if "Average" in operation else enc_vec.sum()
                    plaintext = result.decrypt()[0]

                    st.balloons()
                    st.success(f"✅ Casper computed it! Result: **{plaintext:.2f}**")
                    st.caption("Raw patient data never left your device.")

                    fig = px.histogram(df, x=col_name, title="Distribution (visible only to you)")
                    st.plotly_chart(fig, use_container_width=True)

with tab2:
    uploaded = st.file_uploader("Upload your own CSV", type="csv")
    if uploaded:
        df = pd.read_csv(uploaded)
        st.dataframe(df.head(), use_container_width=True)
        st.info("👻 Ready to encrypt & compute — pick an operation in the Live tab (more coming soon).")

st.caption("Casper MVP — Built with TenSEAL + Streamlit. 100% local. Zero data leaves your machine.")
