
import streamlit as st
import firebase_admin
from firebase_admin import db

# Safety checks
if "uid" not in st.session_state:
    st.error("User ID not found in session. Please login again.")
    st.stop()

st.title("Deposit Waste")

uid = st.session_state["uid"]
user_ref = db.reference(f"/users/{uid}")
user_data = user_ref.get()

# Display current coin balance
if user_data:
    current_coins = user_data.get("coins", 0)
    st.info(f"💰 Your Current Coins: **{current_coins}**")
else:
    st.warning("User data not found.")
    st.stop()

# --- Measure Weight Section ---
st.subheader("📦 Measure Bin Weight")

# Replace this with selected bin ID dynamically if needed
BIN_ID = "-OOb2glfef5lDgtRYPWO"  # <-- You can make this dynamic with st.session_state["bin_id"]
bin_ref = db.reference(f"/bins/{BIN_ID}")

weight = None
if st.button("Measure Weight"):
    bin_data = bin_ref.get()
    if bin_data:
        weight = bin_data.get("weight1")
        if weight is not None:
            st.success(f"🪶 Current Weight in Bin '{BIN_ID}': **{weight} grams**")
            st.session_state["measured_weight"] = weight
        else:
            st.error("Weight not available in this bin.")
    else:
        st.error("Bin not found.")

# --- Deposit Waste Section ---
st.subheader("♻️ Deposit Waste and Earn Coins")

if "measured_weight" in st.session_state:
    if st.button("Deposit Waste"):
        weight = st.session_state["measured_weight"]
        coins_to_add = weight // 20

        updated_coins = current_coins + coins_to_add
        user_ref.update({"coins": updated_coins})

        st.success(f"✅ Waste deposited! You earned **{coins_to_add} coins** 🎉")
        st.info(f"💰 Updated Coin Balance: **{updated_coins}**")
        # Optionally clear measured weight to avoid reusing
        del st.session_state["measured_weight"]
else:
    st.warning("⚠️ Please measure the bin weight before depositing.")
