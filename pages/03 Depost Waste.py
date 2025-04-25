import streamlit as st
import firebase_admin
from firebase_admin import db

# ✅ Safety check for login
if "uid" not in st.session_state:
    st.error("User ID not found in session. Please login again.")
    st.stop()

st.title("Deposit Waste")

# 🔐 Get user data
uid = st.session_state["uid"]
user_ref = db.reference(f"/users/{uid}")
user_data = user_ref.get()

if user_data:
    current_coins = user_data.get("coins", 0)
    st.info(f"💰 Your Current Coins: **{current_coins}**")
else:
    st.warning("User data not found.")
    st.stop()

# 🔁 Bin info (hardcoded or can be dynamic)
BIN_ID = "-OOgBJewCIm0cx-tZ66f"  # Optionally: st.session_state["bin_id"]
bin_ref = db.reference(f"/bins/{BIN_ID}")

# --- STEP 1: Get Initial Weight ---
st.subheader("Step 1: 🪶 Get Initial Bin Weight")

if st.button("Get Current Weight (Before Deposit)"):
    bin_data = bin_ref.get()
    if bin_data and "weight1" in bin_data:
        initial_weight = bin_data["weight1"]
        st.session_state["initial_weight"] = initial_weight
        st.success(f"Initial Weight: **{initial_weight} grams** saved.")
    else:
        st.error("Unable to retrieve initial weight.")

# --- STEP 2: Update New Weight After Deposit ---
st.subheader("Step 2: ➕ Update Bin Weight (After Deposit)")

if st.button("Save New Bin Weight"):
    bin_data = bin_ref.get()
    if bin_data and "weight1" in bin_data:
        new_weight = bin_data["weight1"]
        st.session_state["new_weight"] = new_weight
        st.success(f"New Weight: **{new_weight} grams** saved.")
    else:
        st.error("Unable to retrieve new weight.")

# --- STEP 3: Calculate Coins Earned ---
st.subheader("Step 3: 🎁 Earn Coins Based on Waste Added")

if "initial_weight" in st.session_state and "new_weight" in st.session_state:
    if st.button("Get Coins"):
        initial = st.session_state["initial_weight"]
        new = st.session_state["new_weight"]

        if new > initial:
            weight_diff = new - initial
            coins_earned = weight_diff // 20
            updated_coins = current_coins + coins_earned

            # ✅ Update user's coins in Firebase
            user_ref.update({"coins": updated_coins})

            st.success(f"✅ You added {weight_diff} grams and earned **{coins_earned} coins**!")
            st.info(f"💰 Updated Coin Balance: **{updated_coins}**")

            # Clean up session vars to prevent duplicate coin claims
            del st.session_state["initial_weight"]
            del st.session_state["new_weight"]
        else:
            st.warning("⚠️ New weight must be greater than initial weight.")
else:
    st.warning("ℹ️ Please complete Step 1 and Step 2 before claiming coins.")
