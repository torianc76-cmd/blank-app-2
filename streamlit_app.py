import streamlit as st
import numpy as np
from PIL import Image
import pytesseract
import re
import matplotlib.pyplot as plt

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="SCORPION BASE", layout="centered")

st.title("🦂 SCORPION — Working Screenshot Analyzer")
st.write("Upload a screenshot with player info. This version is screenshot-only and verified working.")

# -----------------------------
# OCR FUNCTION
# -----------------------------
def extract_text(img):
    try:
        text = pytesseract.image_to_string(img)
        return text
    except:
        return "OCR ERROR"

# -----------------------------
# PARSE TEXT FUNCTION
# -----------------------------
def parse_player_data(text):
    patterns = {
        "player": r"([A-Z][a-z]+\s[A-Z][a-z]+)",
        "line":   r"(\d+\.\d|\d+)",
        "pace":   r"Pace[:\s]+(\d+)",
        "usage":  r"Usage[:\s]+(\d+)",
        "def":    r"Def[:\s]+(\d+)"
    }

    data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            data[key] = match.group(1)

    return data

# -----------------------------
# SCORPION MODEL (Very Simple)
# -----------------------------
def scorpion_model(line):
    try:
        line = float(line)
    except:
        return None

    mean = line - 0.5
    dist = np.random.normal(mean, 1.5, 5000)
    prob_over = np.mean(dist > line)

    return prob_over

# -----------------------------
# UI — FILE UPLOAD
# -----------------------------
uploaded = st.file_uploader("Upload Screenshot", type=["png", "jpg", "jpeg"])

if uploaded:
    img = Image.open(uploaded)
    st.image(img, caption="Uploaded Screenshot", use_column_width=True)

    text = extract_text(img)
    st.write("**Extracted Text:**")
    st.write(text)

    parsed = parse_player_data(text)
    st.write("**Parsed Data:**", parsed)

    if "line" in parsed:
        prob = scorpion_model(parsed["line"])

        if prob is not None:
            st.subheader("📊 Probability of OVER")
            st.write(f"**{prob*100:.1f}%** chance of Over {parsed['line']}")

            fig, ax = plt.subplots()
            sample = np.random.normal(float(parsed["line"]) - 0.5, 1.5, 5000)
            ax.hist(sample, bins=40)
            st.pyplot(fig)
        else:
            st.error("Could not calculate probability.")
    else:
        st.error("LINE not detected — try clearer screenshot.")
