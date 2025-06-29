import streamlit as st
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
import os
import uuid
import base64

# Page configuration
st.set_page_config(page_title="🏥 Hospital Report Analyzer", layout="wide")

# Title and Description
st.title("🏥 Hospital Report Analyzer")
st.markdown("Upload patient reports (PDF/Image), analyze content, and track health performance over time.")

# Sidebar: Patient Info
st.sidebar.header("🧑‍⚕️ Patient Section")
patient_name = st.sidebar.text_input("Enter Patient Name:")
session_id = f"{patient_name}_{uuid.uuid4().hex[:6]}"

# OCR Functions
def extract_text_from_image(img):
    image = Image.open(img)
    text = pytesseract.image_to_string(image)
    return text

def extract_text_from_pdf(uploaded_pdf):
    pdf_bytes = uploaded_pdf.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Download link function
def get_download_link(text, filename):
    b64 = base64.b64encode(text.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">📥 Download This Report</a>'
    return href

# Main Upload Area
if patient_name:
    st.sidebar.success(f"Tracking reports for: **{patient_name}**")

    uploaded_file = st.file_uploader("📤 Upload Report (Image or PDF)", type=["png", "jpg", "jpeg", "pdf"])

    if uploaded_file:
        st.info("🧠 Processing the uploaded report...")

        try:
            # Extract Text
            if uploaded_file.type == "application/pdf":
                extracted_text = extract_text_from_pdf(uploaded_file)
            else:
                extracted_text = extract_text_from_image(uploaded_file)

            # Show Extracted Text
            st.subheader("📄 Extracted Report Text")
            st.text_area("Extracted Content", extracted_text, height=300)

            # Save to file
            report_folder = f"reports/{patient_name}"
            os.makedirs(report_folder, exist_ok=True)
            file_path = os.path.join(report_folder, f"{session_id}.txt")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(extracted_text)

            st.success(f"✅ Report saved successfully under: `{file_path}`")

            # Download link
            st.markdown(get_download_link(extracted_text, f"{patient_name}_report.txt"), unsafe_allow_html=True)

            # Display Previous Reports
            st.subheader("📚 Previous Reports for Comparison")
            files = sorted(os.listdir(report_folder))

            if len(files) > 1:
                for f_name in files:
                    with open(os.path.join(report_folder, f_name), "r", encoding="utf-8") as file:
                        content = file.read()
                        st.markdown(f"**📝 {f_name}**")
                        st.code(content[:300] + "..." if len(content) > 300 else content)
            else:
                st.info("No previous reports found yet for this patient.")

        except Exception as e:
            st.error(f"❌ Error: {e}")
else:
    st.warning("⚠️ Please enter the patient name in the sidebar to begin.")
