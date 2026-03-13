import streamlit as st
import pandas as pd
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import io
import os

# --- 1. SETUP: Inventory Management ---
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
st.set_page_config(page_title="Kirana AI Jabalpur", layout="wide")
st.title("🛒 Jabalpur Kirana: Smart Voice Billing")

# Sidebar for Stock
st.sidebar.header("📦 Current Stock")
st.sidebar.dataframe(df)

# --- 3. VOICE LOGIC ---
st.subheader("🎤 Voice Entry (Boliye: Name Qty Item)")
audio = mic_recorder(start_prompt="Record Start", stop_prompt="Stop & Process", key='recorder')

# Session State to hold values
if 'cust_name' not in st.session_state: st.session_state['cust_name'] = ""
if 'qty_input' not in st.session_state: st.session_state['qty_input'] = 1
if 'item_input' not in st.session_state: st.session_state['item_input'] = "Aata"

if audio:
    audio_bio = io.BytesIO(audio['bytes'])
    r = sr.Recognizer()
    with sr.AudioFile(audio_bio) as source:
        audio_data = r.record(source)
        try:
            # Hindi-English mix recognition
            text = r.recognize_google(audio_data, language='hi-IN')
            st.info(f"🎤 Aapne kaha: {text}")
            
            words = text.split()
            if len(words) >= 3:
                st.session_state['cust_name'] = words[0]
                # Try to handle numbers if spoken in Hindi
                st.session_state['qty_input'] = int(words[1]) 
                st.session_state['item_input'] = words[2].capitalize()
        except:
            st.error("Awaaz samajh nahi aayi, dobara boliye.")

# --- 4. BILLING FORM ---
col1, col2 = st.columns(2)
with col1:
    customer = st.text_input("Customer Name", value=st.session_state['cust_name'])
    item_select = st.selectbox("Select Item", df['Item'], index=list(df['Item']).index(st.session_state['item_input']) if st.session_state['item_input'] in list(df['Item']) else 0)

with col2:
    qty = st.number_input("Quantity", min_value=1, value=st.session_state['qty_input'])
    rate = df[df['Item'] == item_select]['Rate'].values[0]
    current_stock = df[df['Item'] == item_select]['Stock'].values[0]
    st.write(f"**Rate:** ₹{rate} | **Stock:** {current_stock}")

total = rate * qty
st.markdown(f"## Total Amount: **₹{total}**")

if st.button("Finalize & Update Stock"):
    if qty <= current_stock:
        df.loc[df['Item'] == item_select, 'Stock'] -= qty
        df.to_excel(file_name, index=False)
        st.success(f"Bill Ban Gaya! Total ₹{total}")
        st.balloons()
    else:
        st.error("Dukan mein itna maal nahi hai!")