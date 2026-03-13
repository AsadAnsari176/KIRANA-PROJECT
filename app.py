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

# --- 2. UI DESIGN ---
st.set_page_config(page_title="Jabalpur Kirana AI", layout="wide")
st.title("🛒 Jabalpur Kirana: Smart Billing & Stock")

# Sidebar
st.sidebar.header("📦 Live Stock")
st.sidebar.dataframe(df)

# --- 3. VOICE LOGIC (Web Version) ---
st.subheader("New Bill Entry")
col1, col2 = st.columns(2)

with col1:
    st.write("🎤 Mic Button Dabayein aur Bolein:")
    # Naya Browser Mic
    audio = mic_recorder(start_prompt="Record Start", stop_prompt="Stop & Process", key='recorder')
    
    # Jab record ho jaye toh ye chalega
    if audio:
        st.audio(audio['bytes'])
        st.info("Bhai, awaaz record ho gayi! (Abhi main ise text mein badalne wala logic update kar raha hoon...)")

    cust_name = st.text_input("Customer Name", value="Asad")
    item_select = st.selectbox("Select Item", df['Item'])

with col2:
    qty = st.number_input("Quantity", min_value=1, value=1)
    rate = df[df['Item'] == item_select]['Rate'].values[0]
    stock = df[df['Item'] == item_select]['Stock'].values[0]
    st.info(f"Rate: ₹{rate} | Stock available: {stock}")

# --- 4. FINAL BILL ---
total = rate * qty
st.markdown(f"### Total: ₹{total}")

if st.button("Finalize & Print Bill"):
    if qty <= stock:
        df.loc[df['Item'] == item_select, 'Stock'] -= qty
        df.to_excel(file_name, index=False)
        st.success(f"Bill Done! Total ₹{total} for {cust_name}")
        st.balloons()
    else:
        st.error("Stock nahi hai dukan mein!")
