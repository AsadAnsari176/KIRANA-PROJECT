import streamlit as st
import pandas as pd
from streamlit_mic_recorder import mic_recorder
import os

# --- 1. SETUP ---
file_name = "inventory.xlsx"
if not os.path.exists(file_name):
    df = pd.DataFrame({
        'Item': ['Aata', 'Chawal', 'Doodh', 'Shakkar', 'Tel'],
        'Rate': [45, 60, 66, 42, 160],
        'Stock': [100, 50, 20, 80, 30]
    })
    df.to_excel(file_name, index=False)
else:
    df = pd.read_excel(file_name)

# --- 2. UI ---
st.set_page_config(page_title="Jabalpur Kirana AI", layout="wide")
st.title("🛒 Jabalpur Kirana: Smart Billing")

st.sidebar.header("📦 Live Stock")
st.sidebar.dataframe(df)

# --- 3. MIC LOGIC ---
st.subheader("New Bill Entry")
# Ye button ab aapke mobile ka mic use karega
audio = mic_recorder(start_prompt="🎤 Record Start", stop_prompt="🛑 Stop", key='recorder')

if audio:
    st.audio(audio['bytes'])
    st.success("Awaaz record ho gayi! Abhi text conversion baaki hai.")

# Manual Entry (Jab tak voice fully connect na ho)
cust_name = st.text_input("Customer Name", value="Asad")
item_select = st.selectbox("Select Item", df['Item'])
qty = st.number_input("Quantity", min_value=1, value=1)

rate = df[df['Item'] == item_select]['Rate'].values[0]
total = rate * qty
st.markdown(f"### Total: ₹{total}")

if st.button("Finalize Bill"):
    st.balloons()
    st.success(f"Bill Ban Gaya: ₹{total}")
