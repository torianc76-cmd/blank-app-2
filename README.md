import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pytesseract
from PIL import Image
import re

st.set_page_config(page_title="SCORPION BASE", layout="centered")

st.title("🦂 SCORPION — Base Working Engine")
st.write("Upload a screenshot with player info. This version is screenshot-only and verified working.")

# -----------------------
# OCR + Parsing Functions
# -----------------------

def extract_text(img):
    """
    Clean OCR extraction. Base model - stable and simple.
    """
    try:
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        return f"OCR ERROR: {e}"


def parse_player_data(text):
    """
    Looks inside the extracted text and finds:
    - Player name
    - Line
    - Pace
    - Usage
    - Defensive Rank
    """

    patterns = {
        "player": r"([A-Z][a-z]+\s[A-Z][a-z]+)",
        "line": r"([0-9]+\.[0-9])",
        "pace": r"Pace[:\- ]*([0-9]+)",
        "usage": r"Usage[:\- ]*([0-9]+)",
        "def_rank": r"Def.*?([0-9]+)"
    }

    data = {}

    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        data[key] = match.group(1) if match else None

    return data


def scorpion_model(pred_line):
    """
    SUPER SIMPLE working model:
    Creates a distribution around the line and returns probability of OVER.
    """
    try:
        line = float(pred_line)
    except:
        return None, None

    mean = line - 0.5
    std = 1.8
    sims = np.random.normal(mean, std, 50000)

    prob_over = (sims > line).mean() * 100
    return prob_over, sims


# -----------------------
# UI
# -----------------------

uploaded = st.file_uploader("Upload Screenshot", type=["png", "jpg", "jpeg"])

if uploaded:
    img = Image.open(uploaded)
    st.image(img, caption="Uploaded Screenshot")

    st.subheader("🔍 OCR Extracted Text")
    text = extract_text(img)
    st.text(text)

    st.subheader("📌 Parsed Data")
    parsed = parse_player_data(text)
    st.json(parsed)

    if parsed.get("line"):
        prob, sims = scorpion_model(parsed["line"])

        if prob is None:
            st.error("Could not compute model probability.")
        else:
            st.success(f"**SCORPION Probability Over {parsed['line']}: {prob:.2f}%**")

            fig, ax = plt.subplots()
            ax.hist(sims, bins=40)
            ax.axvline(float(parsed["line"]), color="red")
            st.pyplot(fig)
    else:
        st.error("❌ Could not detect player line.")
