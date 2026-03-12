import streamlit as st
import pandas as pd
import os
import speech_recognition as sr

def get_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎤 Sun raha hoon... Boliye!")
        # Background noise saaf karne ke liye
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        try:
            # Awaaz ko Google AI se text mein badlo
            text = r.recognize_google(audio, language='hi-IN') # Hindi/English dono samjhega
            return text
        except:
            return "Awaaz samajh nahi aayi, fir se boliye."

# --- UI mein Mic Button ---
if st.button("🎤 Bol kar Entry Karein"):
    voice_text = get_voice_input()
    st.success(f"Aapne kaha: {voice_text}")
    # Ab is text se 'Asad' aur 'Aata' nikalne ka kaam shuru hoga
# --- 1. Database Setup (Excel Check) ---
file_name = "inventory.xlsx"

if not os.path.exists(file_name):
    # Agar file nahi hai toh naya banao
    initial_data = {
        'Item': ['Aata', 'Chawal', 'Doodh', 'Shakkar', 'Tel'],
        'Rate': [45, 60, 66, 42, 160],
        'Stock': [100, 50, 20, 80, 30]
    }
    pd.DataFrame(initial_data).to_excel(file_name, index=False)

# Data load karo
df = pd.read_excel(file_name)

# --- 2. Design ---
st.set_page_config(page_title="Jabalpur Kirana AI", layout="wide")
st.title("🛒 Jabalpur Kirana: Smart Billing & Stock")

# --- 3. Sidebar (Stock Display) ---
st.sidebar.header("📦 Live Stock")
st.sidebar.dataframe(df)

# --- 4. Billing Area ---
st.subheader("New Bill Entry")
col1, col2 = st.columns(2)

with col1:
    customer = st.text_input("Customer Name", placeholder="Asad")
    item_select = st.selectbox("Select Item", df['Item'])

with col2:
    qty = st.number_input("Quantity", min_value=1, value=1)
    # Rate nikalo
    rate = df[df['Item'] == item_select]['Rate'].values[0]
    current_stock = df[df['Item'] == item_select]['Stock'].values[0]
    st.info(f"Rate: ₹{rate} | Stock available: {current_stock}")

total = rate * qty
st.write(f"### Total: ₹{total}")

# --- 5. Logic: Button click karne par kya hoga? ---
if st.button("Finalize & Print Bill"):
    if qty <= current_stock:
        # 1. Stock minus karo
        df.loc[df['Item'] == item_select, 'Stock'] -= qty
        # 2. Excel save karo
        df.to_excel(file_name, index=False)
        
        st.success(f"Bill Generated for {customer}! Final: ₹{total}")
        st.balloons() # Ab balloons udne chahiye!
        st.rerun() # Screen update karega naye stock ke sath
    else:
        st.error("❌ Stock kam hai! Itna maal nahi hai dukan mein.")