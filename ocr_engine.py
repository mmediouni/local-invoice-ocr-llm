"""
Module OCR hybride ultra-léger (CPU uniquement, < 100 Mo RAM).
Prend en charge :
1. RapidOCR (Moteur ONNX local ultra-rapide, 0 configuration, 0 droits admin)
2. Tesseract OCR (si installé sur la machine)
3. Extraction directe PDF numérique via pdfplumber
"""

import gc
import io
import os
from PIL import Image, ImageEnhance, ImageFilter
from config import find_tesseract_path

# Initialisation du moteur RapidOCR (léger, local, CPU)
_rapid_ocr_engine = None

def get_rapid_ocr():
    global _rapid_ocr_engine
    if _rapid_ocr_engine is None:
        try:
            from rapidocr_onnxruntime import RapidOCR
            _rapid_ocr_engine = RapidOCR()
        except ImportError:
            _rapid_ocr_engine = None
    return _rapid_ocr_engine


def get_available_engines() -> list[str]:
    """Retourne la liste des moteurs OCR disponibles."""
    engines = []
    if get_rapid_ocr() is not None:
        engines.append("RapidOCR (Recommandé - Sans installation)")
    if find_tesseract_path() is not None:
        engines.append("Tesseract OCR")
    return engines


def preprocess_image(image: Image.Image, max_dim: int = 1800) -> Image.Image:
    """
    Prétraitement Pillow optimisé pour tickets et factures :
    1. Réduction sous 1800px pour diviser par 4 le temps CPU et la RAM.
    2. Conversion en niveaux de gris.
    3. Rehaussement du contraste thermique.
    """
    w, h = image.size
    if max(w, h) > max_dim:
        scale = max_dim / max(w, h)
        image = image.resize((int(w * scale), int(h * scale)), Image.Resampling.BILINEAR)

    gray = image.convert("L")
    contrasted = ImageEnhance.Contrast(gray).enhance(1.8)
    return contrasted.filter(ImageFilter.SHARPEN)


def extract_with_rapidocr(image: Image.Image) -> str:
    """Extraction via RapidOCR ONNX."""
    import numpy as np
    engine = get_rapid_ocr()
    if engine is None:
        return ""
    img_np = np.array(image.convert("RGB"))
    results, _ = engine(img_np)
    if not results:
        return ""
    # Assembler les lignes de texte ordonnées
    lines = [item[1] for item in results if item and len(item) > 1]
    return "\n".join(lines)


def extract_with_tesseract(image: Image.Image, lang: str = "fra+eng") -> str:
    """Extraction via Tesseract OCR."""
    import pytesseract
    tess_path = find_tesseract_path()
    if tess_path:
        pytesseract.pytesseract.tesseract_cmd = tess_path
    
    processed = preprocess_image(image)
    try:
        raw_text = pytesseract.image_to_string(
            processed, lang=lang, config=r"--oem 1 --psm 6"
        )
    except pytesseract.TesseractError:
        raw_text = pytesseract.image_to_string(processed, lang=lang)
    return raw_text.strip()


def extract_text_from_image(image_input, engine_choice: str = "auto") -> str:
    """
    Extrait le texte brut d'une image (PIL.Image, bytes ou chemin).
    """
    img = None
    try:
        if isinstance(image_input, (str, bytes)):
            img = Image.open(image_input if isinstance(image_input, str) else io.BytesIO(image_input))
        else:
            img = image_input

        # Choix du moteur
        if "tesseract" in engine_choice.lower() and find_tesseract_path():
            return extract_with_tesseract(img)
        
        # Par défaut : RapidOCR
        rapid = get_rapid_ocr()
        if rapid is not None:
            text = extract_with_rapidocr(img)
            if text.strip():
                return text.strip()

        # Fallback Tesseract
        if find_tesseract_path():
            return extract_with_tesseract(img)

        return ""
    finally:
        del img
        gc.collect()


def extract_text_from_pdf(pdf_bytes_or_file) -> str:
    """
    Extrait le texte d'un PDF :
    1. Directement si le PDF contient du texte vectoriel (0 Mo RAM, 0.05s).
    2. Via OCR sur l'image si c'est un document scanné.
    """
    try:
        import pdfplumber
        with pdfplumber.open(pdf_bytes_or_file) as pdf:
            full_text = []
            for page in pdf.pages[:3]:
                txt = page.extract_text()
                if txt and len(txt.strip()) > 30:
                    full_text.append(txt.strip())
                else:
                    page_img = page.to_image(resolution=180).original
                    ocr_res = extract_text_from_image(page_img)
                    if ocr_res:
                        full_text.append(ocr_res)
            return "\n\n".join(full_text).strip()
    except Exception as e:
        return f"Erreur lors du traitement du PDF : {str(e)}"
