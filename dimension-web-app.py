import streamlit as st
import requests
from PIL import Image
import base64
from io import BytesIO

st.title("Dimension Measurement App")

# API URL
API_URL = "http://localhost:8000"

def upload_image(image, confidence_threshold):
    endpoint = f"{API_URL}/dimension/upload_image/"
    files = {"file": image}
    data = {"confidence_threshold": confidence_threshold}
    response = requests.post(endpoint, files=files, data=data)
    return response.json()

def process_image(reference_height, reference_width, reference_box_id):
    endpoint = f"{API_URL}/dimension/process_image/"
    data = {
        "reference_box_id": reference_box_id,
        "reference_height": reference_height,
        "reference_width": reference_width
        
    }
    response = requests.post(endpoint, data=data)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError as e:
        st.error(f"Failed to decode JSON response: {e}")
        st.error(response.text)
        return None

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)
    st.write("Processing...")

    # Convert image to binary
    img_bytes = BytesIO()
    image.save(img_bytes, format="JPEG")
    img_bytes = img_bytes.getvalue()

    # Initial confidence threshold
    confidence_threshold = st.number_input("Confidence Threshold:", min_value=0.0, max_value=1.0, value=0.6, step=0.05)

    if st.button("Change"):
        # Upload image to API with new confidence threshold
        upload_response = upload_image(img_bytes, confidence_threshold)
        if "image" in upload_response:
            st.session_state.intermediate_image = upload_response["image"]
        else:
            st.error("Failed to upload and process the image with new confidence threshold.")

# Display intermediate image if available in session state
if "intermediate_image" in st.session_state:
    intermediate_image = base64.b64decode(st.session_state.intermediate_image)
    st.image(intermediate_image, caption="Intermediate Image", use_column_width=True)

    st.write("Reference Object Details:")
    reference_box_id = st.number_input("Reference Box ID:", min_value=0, key='ref_box_id')
    reference_height = st.number_input("Reference Object Height (cm):", min_value=0.0, format="%.2f", key='ref_height')
    reference_width = st.number_input("Reference Object Width (cm):", min_value=0.0, format="%.2f", key='ref_width')
    

    if st.button("Process Image"):
        process_response = process_image(reference_height, reference_width, reference_box_id)
        if process_response and "image" in process_response:
            processed_image = base64.b64decode(process_response["image"])
            st.image(processed_image, caption="Processed Image", use_column_width=True)
        else:
            st.error("Failed to process image.")
