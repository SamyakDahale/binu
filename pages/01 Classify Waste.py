import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import time
import openai  


openai.api_key = "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" 


# ✅ Ensure user is logged in
if "user" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

# ✅ Store UID (for forwarding to other pages)
st.session_state["uid"] = st.session_state["user"]["uid"]

# ✅ Load trained model
@st.cache_resource
def load_model():
    model = tf.keras.models.load_model("best_trashnet_model.h5")  # Path to your .h5 model
    return model

model = load_model()

# ✅ Image preprocessing function
def preprocess_image(image, target_size=(224, 224)):
    image = image.resize(target_size)
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image

# ✅ App UI
st.title("Waste Classification")
st.markdown("Choose how you'd like to provide the image:")

option = st.radio("Select Image Input Method", ["Upload Image", "Use Camera"])
st.write("Model input shape:", model.input_shape)

img = None

# ✅ Upload or camera input
if option == "Upload Image":
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file)

elif option == "Use Camera":
    camera_image = st.camera_input("Take a picture")
    if camera_image:
        img = Image.open(camera_image)

# ✅ Show image and run prediction
if img is not None:
    st.image(img, caption="Selected Image", use_column_width=True)

    if st.button("Submit"):
        processed = preprocess_image(img)
        prediction = model.predict(processed)
        class_index = np.argmax(prediction)
        class_names = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]  # Change if needed
        predicted_class = class_names[class_index]

        # ✅ Store result for next page
        st.session_state["predicted_class"] = predicted_class

        st.success(f"Predicted Class: **{predicted_class}**")

                # 💬 Ask ChatGPT for disposal tip
        with st.spinner("🔍 Getting disposal tip from ChatGPT..."):
            prompt = f"""
            I have a waste item that has been classified as '{predicted_class}'.
            Please provide:
            - A short description of this waste type.
            - Safe and eco-friendly disposal or recycling tips.
            - Environmental impact if not handled properly.
            Make it user-friendly and practical.
            """
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    temperature=0.6
                )
                disposal_tip = response['choices'][0]['message']['content']
                st.markdown("### 🧠 ChatGPT Disposal Tip")
                st.info(disposal_tip)
            except Exception as e:
                st.error(f"❌ Error while contacting ChatGPT: {e}")
        
        time.sleep(3)

        # ✅ Navigate to map page
        st.switch_page("pages/02 Display Bins.py")
