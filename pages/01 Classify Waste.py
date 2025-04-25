import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import time
import google.generativeai as genai

# 🔐 Set your Gemini API Key
genai.configure(api_key="AIzaSyDKLv-h6XeVTnMiZNMPYNutQhgur4DV65Y")  # Preferably from st.secrets["GEMINI_API_KEY"]

# ✅ Ensure user is logged in
if "user" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

st.session_state["uid"] = st.session_state["user"]["uid"]

@st.cache_resource
def load_model():
    return tf.keras.models.load_model("best_trashnet_model.h5")

model = load_model()

def preprocess_image(image, target_size=(224, 224)):
    image = image.resize(target_size)
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image

st.title("Waste Classification")
st.markdown("Choose how you'd like to provide the image:")

option = st.radio("Select Image Input Method", ["Upload Image", "Use Camera"])
st.write("Model input shape:", model.input_shape)

img = None
if option == "Upload Image":
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file)
elif option == "Use Camera":
    camera_image = st.camera_input("Take a picture")
    if camera_image:
        img = Image.open(camera_image)

if img is not None:
    st.image(img, caption="Selected Image", use_column_width=True)

    if st.button("Submit"):
        processed = preprocess_image(img)
        prediction = model.predict(processed)
        class_index = np.argmax(prediction)
        class_names = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]
        predicted_class = class_names[class_index]
        st.session_state["predicted_class"] = predicted_class

        st.success(f"Predicted Class: **{predicted_class}**")

        # 💬 Get Gemini tip
        with st.spinner("🔍 Getting disposal tip from Gemini..."):
            prompt = f"""
            I have a waste item that has been classified as '{predicted_class}'.
            Please provide:
            - A short description of this waste type.
            - Safe and eco-friendly disposal or recycling tips.
            - Environmental impact if not handled properly.
            Make it user-friendly and practical.
            """
            try:
                model = genai.GenerativeModel("gemini-1.5-pro")
                response = model.generate_content(prompt)
                disposal_tip = response.text
                st.markdown("### 🧠 Gemini Disposal Tip")
                st.info(disposal_tip)
            except Exception as e:
                st.error(f"❌ Error while contacting Gemini: {e}")
        
        time.sleep(3)
        st.switch_page("pages/02 Display Bins.py")
