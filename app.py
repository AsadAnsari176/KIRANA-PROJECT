import streamlit as st
import pandas as pd
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from pydub import AudioSegment
import io
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
st.set_page_config(page_title="Kirana AI Jabalpur", layout="wide")
st.title("🛒 Jabalpur Kirana: Smart Voice Billing")

if 'cust_name' not in st.session_state: st.session_state['cust_name'] = ""
if 'qty_input' not in st.session_state: st.session_state['qty_input'] = 1
if 'item_input' not in st.session_state: st.session_state['item_input'] = "Aata"

# --- 3. VOICE LOGIC (Final Fixed) ---
st.subheader("🎤 Voice Entry (Boliye: Name Qty Item)")
audio = mic_recorder(start_prompt="Record Start", stop_prompt="Stop & Process", key='recorder')

if audio:
    try:
        # Step A: Convert to WAV
        audio_bio = io.BytesIO(audio['bytes'])
        audio_segment = AudioSegment.from_file(audio_bio)
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format="wav")
        wav_io.seek(0)

        # Step B: Speech to Text
        r = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language='hi-IN')
            st.info(f"🎤 Aapne kaha: {text}")
            
            words = text.split()
            if len(words) >= 3:
                st.session_state['cust_name'] = words[0]
                st.session_state['qty_input'] = int(words[1])
                st.session_state['item_input'] = words[2].capitalize()
    except Exception as e:
        st.error("Bhai, awaaz saaf nahi thi ya mic ki permission ka chakkar hai. Phir se try karein.")

# --- 4. BILLING FORM ---
col1, col2 = st.columns(2)
with col1:
    customer = st.text_input("Customer Name", value=st.session_state['cust_name'])
    items_list = list(df['Item'])
    default_idx = items_list.index(st.session_state['item_input']) if st.session_state['item_input'] in items_list else 0
    item_select = st.selectbox("Select Item", items_list, index=default_idx)

with col2:
    qty = st.number_input("Quantity", min_value=1, value=st.session_state['qty_input'])
    rate = df[df['Item'] == item_select]['Rate'].values[0]
    stock = df[df['Item'] == item_select]['Stock'].values[0]
    st.write(f"**Rate:** ₹{rate} | **Stock:** {stock}")

total = rate * qty
st.markdown(f"## Total: ₹{total}")

if st.button("Finalize Bill"):
    if qty <= stock:
        df.loc[df['Item'] == item_select, 'Stock'] -= qty
        df.to_excel(file_name, index=False)
        st.success(f"Bill Ban Gaya! Total ₹{total}")
        st.balloons()
    else:
        st.error("Stock khatam!")
