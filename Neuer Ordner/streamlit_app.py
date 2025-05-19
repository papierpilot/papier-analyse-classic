import streamlit as st
import numpy as np
import cv2
from PIL import Image

# Farbdefinitionen (HSV)
BRAUN_MIN = np.array([10, 50, 50])
BRAUN_MAX = np.array([30, 255, 255])
WEISS_MIN = np.array([0, 0, 180])
WEISS_MAX = np.array([180, 50, 255])
ROI_MIN = np.array([0, 0, 60])
ROI_MAX = np.array([180, 80, 255])

# Analysefunktion
def analysiere_bild(pil_bild):
    img = np.array(pil_bild.convert("RGB"))
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    roi_mask = cv2.inRange(hsv, ROI_MIN, ROI_MAX)
    braun = cv2.inRange(hsv, BRAUN_MIN, BRAUN_MAX)
    weiss = cv2.inRange(hsv, WEISS_MIN, WEISS_MAX)

    braun_im_roi = cv2.bitwise_and(braun, roi_mask)
    weiss_im_roi = cv2.bitwise_and(weiss, roi_mask)

    relevant = np.count_nonzero(braun_im_roi) + np.count_nonzero(weiss_im_roi)
    if relevant == 0:
        return 0.0, 0.0

    braun_prozent = np.count_nonzero(braun_im_roi) / relevant * 100
    weiss_prozent = np.count_nonzero(weiss_im_roi) / relevant * 100
    return braun_prozent, weiss_prozent

# Streamlit UI
st.set_page_config(page_title="AVG Papieranalyse", layout="centered")
st.title("📦📸 AVG Papieranalyse")

# Kennzeichenfoto erfassen
st.markdown("### 📷 Schritt 1: Kennzeichen fotografieren")
kennzeichen_bild = st.camera_input("Bitte fotografiere das Kennzeichen")

if kennzeichen_bild:
    st.success("✅ Kennzeichenbild gespeichert.")
    
    st.markdown("### 📁 Schritt 2: 5 Bilder der Ladung hochladen")
    bilder = st.file_uploader("Bitte genau 5 Bilder auswählen", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if bilder and len(bilder) != 5:
        st.warning("⚠️ Du musst genau 5 Bilder hochladen.")
    
    elif bilder and len(bilder) == 5:
        gesamt_braun = 0
        gesamt_weiss = 0

        for bild in bilder:
            img = Image.open(bild)
            b, w = analysiere_bild(img)
            gesamt_braun += b
            gesamt_weiss += w
            st.write(f"🖼️ {bild.name} → Karton: {b:.1f} %, Zeitung: {w:.1f} %")

        mittel_braun = gesamt_braun / 5
        mittel_weiss = gesamt_weiss / 5

        st.markdown("### 📊 Durchschnitt:")
        st.success(f"📦 Karton: **{mittel_braun:.1f} %**, 📰 Zeitung: **{mittel_weiss:.1f} %**")

        if mittel_braun >= 49:
            st.success("✅ Empfehlung: **Verpressen**")
        else:
            st.warning("⚠️ Empfehlung: **Sortieren**")
else:
    st.info("⬆️ Bitte zuerst das Kennzeichen fotografieren.")
