import streamlit as st
import numpy as np
from PIL import Image
import io
import time
import base64
from google.cloud import aiplatform

# Setup Vertex AI
PROJECT_ID = "your-gcp-project-id"
REGION = "your-region"  # e.g., "us-central1"
ENDPOINT_ID = "your-endpoint-id"

# Authenticate with GCP
aiplatform.init(project=PROJECT_ID, location=REGION)

# Helper: send image to Vertex AI endpoint
def predict_image(image: Image.Image):
    # Convert image to bytes
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    byte_data = buffer.getvalue()
    encoded_image = base64.b64encode(byte_data).decode("utf-8")

    endpoint = aiplatform.Endpoint(endpoint_name=ENDPOINT_ID)

    response = endpoint.predict(instances=[{"content": encoded_image}])
    return response

# UI
st.title("Waste Classification (AutoML)")

st.markdown("Choose how you'd like to provide the image:")

option = st.radio("Select Image Input Method", ["Upload Image", "Use Camera"])

img = None

if option == "Upload Image":
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")

elif option == "Use Camera":
    camera_image = st.camera_input("Take a picture")
    if camera_image:
        img = Image.open(camera_image).convert("RGB")

if img is not None:
    st.image(img, caption="Selected Image", use_column_width=True)

    if st.button("Submit"):
        st.info("Sending image to AutoML model...")
        result = predict_image(img)

        try:
            predicted_class = result.predictions[0].get("displayName")
            confidence = result.predictions[0].get("confidence", 0)

            st.success(f"Predicted Class: **{predicted_class}** ({confidence*100:.2f}% confidence)")
            st.session_state["predicted_class"] = predicted_class
            time.sleep(5)
            st.switch_page("pages/showmap.py")
        except Exception as e:
            st.error(f"Prediction failed: {e}")
