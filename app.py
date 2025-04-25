import streamlit as st
from firebase_auth import sign_up, sign_in
from firebase_admin import db  # use your existing firebase_init
import firebase_admin
import firebase_init

st.title("Firebase Auth")

menu = st.sidebar.selectbox("Choose", ["Login", "Sign Up"])

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if menu == "Sign Up":
    if st.button("Create Account"):
        result = sign_up(email, password)
        if "idToken" in result:
            st.success("Account created successfully!")

            # Add user to Firebase Realtime Database under 'users' node
            uid = result["localId"]
            user_ref = db.reference(f'/users/{uid}')
            user_ref.set({
                "email": email,
                "coins": 0
            })

            st.info("User profile created in database.")
        else:
            st.error(result.get("error", {}).get("message", "Signup failed"))

elif menu == "Login":
    if st.button("Login"):
        result = sign_in(email, password)
        if "idToken" in result:
            st.success(f"Welcome, {email}!")

            # Store user session info
            st.session_state["user"] = {
                "idToken": result["idToken"],
                "email": email,
                "uid": result["localId"]  # This is the UID you want to use later
            }
            # ✅ Navigate to map page
            st.switch_page("pages/01 Classify Waste.py")
        else:
            st.error(result.get("error", {}).get("message", "Login failed"))

