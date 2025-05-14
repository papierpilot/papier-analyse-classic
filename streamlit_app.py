import streamlit as st
import numpy as np
import cv2
from PIL import Image

# HSV-Schwellen für Karton (braun)
BRAUN_MIN = np.array([10, 50, 50])
BRAUN_MAX = np.array([30, 255, 255])

# HSV-Schwellen für Zeitung (weiß)
WEISS_MIN = np.array([0, 0, 180])
WEISS_MAX = np.array([180, 50, 255])

# Region of Interest (Papierhaufen)
ROI_MIN = np.array([0, 0, 60])
ROI_MAX = np.array([180, 80, 255])

def analysiere_bild(pil_bild):
    img = np.array(pil_bild.convert("RGB"))
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    roi_mask = cv2.inRange(hsv, ROI_MIN, ROI_MAX)
    braun = cv2.inRange(hsv, BRAUN_MIN, BRAUN_MAX)
    weiss = cv2.inRange(hsv, WEISS_MIN, WEISS_MAX)

    braun_im_roi = cv2.bitwise_and(braun, roi_mask)
    weiss_im_roi = cv2.bitwise_and(weiss, roi_mask)

    gesamt = np.count_nonzero(roi_mask)
    braun_px = np.count_nonzero(braun_im_roi)
    weiss_px = np.count_nonzero(weiss_im_roi)

    relevant = braun_px + weiss_px
    if relevant == 0:
        return 0.0, 0.0

    braun_prozent = braun_px / relevant * 100
    weiss_prozent = weiss_px / relevant * 100
    return braun_prozent, weiss_prozent

# 🟢 Streamlit UI
st.set_page_config(page_title="📦📄 Farb-Analyse", layout="centered")
st.title("📦📸 Klassische Papieranalyse")
st.write("Bitte lade **genau 5 Bilder** hoch – wir analysieren den Anteil an Karton und Zeitung.")

bilder = st.file_uploader("📷 Bilder auswählen", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if bilder and len(bilder) == 5:
    st.success("5 Bilder erhalten – starte Analyse...")

    gesamt_braun = 0
    gesamt_weiss = 0

    for datei in bilder:
        bild = Image.open(datei)
        b, w = analysiere_bild(bild)
        gesamt_braun += b
        gesamt_weiss += w
        st.write(f"🖼️ **{datei.name}** → Karton: {b:.1f} %, Zeitung: {w:.1f} %")

    mittel_braun = gesamt_braun / 5
    mittel_weiss = gesamt_weiss / 5

    st.markdown("### 📊 Durchschnitt:")
    st.success(f"📦 Karton: **{mittel_braun:.1f} %**, 📰 Zeitung: **{mittel_weiss:.1f} %**")

    if mittel_braun >= 60:
        st.success("✅ Empfehlung: **Verpressen**")
    else:
        st.warning("⚠️ Empfehlung: **Sortieren**")

elif bilder:
    st.error("❌ Bitte lade **genau 5 Bilder** hoch, um die Analyse zu starten.")
else:
    st.info("Bitte lade mindestens 1 Bild hoch.")
