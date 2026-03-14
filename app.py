import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import qrcode
from datetime import datetime
import os
import io

# --- 1. CONFIG & DATABASE ---
STORE_NAME = "JABALPUR KIRANA STORE"
STORE_ADDRESS = "Gali No. 2, Near Main Market, Jabalpur"
UPI_ID = "asadansari@upi"  # Yahan dukandar ki UPI ID dalni hai

inv_file = "inventory.xlsx"
sales_file = "sales_history.xlsx"

def load_df(file, columns):
    if os.path.exists(file): return pd.read_excel(file)
    return pd.DataFrame(columns=columns)

# --- 2. LOGIC FUNCTIONS ---
def generate_qr(amt):
    upi_url = f"upi://pay?pa={UPI_ID}&pn={STORE_NAME}&am={amt}&cu=INR"
    qr = qrcode.make(upi_url)
    qr.save("temp_qr.png")
    return "temp_qr.png"

def create_bill_photo(name, item, qty, rate, total, b_type):
    # Image Canvas
    img = Image.new('RGB', (500, 750), color='white')
    d = ImageDraw.Draw(img)
    
    # 1. Header (Name, Address, Date)
    d.text((120, 20), STORE_NAME, fill="black")
    d.text((100, 45), STORE_ADDRESS, fill="grey")
    d.text((20, 80), f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}", fill="black")
    d.line((20, 105, 480, 105), fill="black", width=2)
    
    # 2. Customer & Item Details
    d.text((20, 120), f"Customer: {name}", fill="black")
    d.text((20, 150), f"Type: {b_type}", fill="red" if b_type=="UDHAAR" else "green")
    d.text((20, 190), f"Item: {item}", fill="black")
    d.text((20, 220), f"Quantity: {qty} | Rate: {rate}", fill="black")
    
    d.line((20, 260, 480, 260), fill="black", width=1)
    d.text((20, 280), f"TOTAL AMOUNT: Rs. {total}", fill="black")
    
    # 3. QR Code Paste
    if b_type == "CASH":
        qr_path = generate_qr(total)
        qr_img = Image.open(qr_path).resize((150, 150))
        img.paste(qr_img, (175, 320))
        d.text((160, 480), "Scan to Pay via UPI", fill="blue")

    img.save("bill_output.png")
    return "bill_output.png"

# --- 3. UI LAYOUT ---
st.title("🚀 Jabalpur Kirana: Master Bot")

menu = st.sidebar.selectbox("Menu", ["Naya Bill / Udhaar", "Pichle Bills (History)", "Price Tracker"])

if menu == "Naya Bill / Udhaar":
    user_input = st.text_input("Boliye: Name Qty Item Price (e.g. Asad 2 Aata 50)")
    
    if user_input:
        words = user_input.split()
        if len(words) >= 3:
            name, qty, item = words[0], int(words[1]), words[2].capitalize()
            
            # Price Logic (Auto-fetch or Update)
            inv_df = load_df(inv_file, ['Item', 'Rate'])
            if len(words) > 3:
                rate = float(words[3])
                # Update Inventory
                if item in inv_df['Item'].values:
                    inv_df.loc[inv_df['Item'] == item, 'Rate'] = rate
                else:
                    inv_df = pd.concat([inv_df, pd.DataFrame([{'Item': item, 'Rate': rate}])], ignore_index=True)
                inv_df.to_excel(inv_file, index=False)
            else:
                match = inv_df[inv_df['Item'] == item]
                rate = match['Rate'].values[0] if not match.empty else 0
            
            total = qty * rate
            st.write(f"### Preview: {name} | {item} | Total: ₹{total}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Cash Bill (Photo)"):
                    path = create_bill_photo(name, item, qty, rate, total, "CASH")
                    st.image(path)
                    # Save to History
                    sales_df = load_df(sales_file, ['Date', 'Customer', 'Item', 'Qty', 'Rate', 'Total', 'Type'])
                    new_row = {'Date': datetime.now().strftime("%d-%m-%Y"), 'Customer': name, 'Item': item, 'Qty': qty, 'Rate': rate, 'Total': total, 'Type': 'CASH'}
                    pd.concat([sales_df, pd.DataFrame([new_row])], ignore_index=True).to_excel(sales_file, index=False)
            
            with col2:
                if st.button("🚩 Udhaar Chadhayein"):
                    path = create_bill_photo(name, item, qty, rate, total, "UDHAAR")
                    st.image(path)
                    sales_df = load_df(sales_file, [])
                    new_row = {'Date': datetime.now().strftime("%d-%m-%Y"), 'Customer': name, 'Item': item, 'Qty': qty, 'Rate': rate, 'Total': total, 'Type': 'UDHAAR'}
                    pd.concat([sales_df, pd.DataFrame([new_row])], ignore_index=True).to_excel(sales_file, index=False)
                    st.error("Udhaar Khata Updated!")

elif menu == "Pichle Bills (History)":
    st.subheader("Pichle Saare Bills")
    sales_df = load_df(sales_file, [])
    search = st.text_input("Customer ka naam likhein")
    if search:
        st.dataframe(sales_df[sales_df['Customer'].str.contains(search, case=False)])
    else:
        st.dataframe(sales_df)

elif menu == "Price Tracker":
    st.subheader("Purana Rate Check Karein")
    sales_df = load_df(sales_file, [])
    item_search = st.text_input("Item ka naam (e.g. Chawal)")
    if item_search:
        res = sales_df[sales_df['Item'].str.contains(item_search, case=False)]
        st.write(res[['Date', 'Item', 'Rate']])
