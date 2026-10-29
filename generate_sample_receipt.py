"""
Générateur de ticket de caisse d'exemple pour tester l'OCR et l'extraction.
Crée une image réaliste 'sample_ticket.png' avec Pillow.
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_receipt(filename="sample_ticket.png"):
    width = 500
    height = 680
    bg_color = (252, 252, 250)  # Papier thermique légèrement beige
    text_color = (30, 30, 30)   # Encre noire / grise foncée

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Chargement d'une police par défaut
    font = ImageFont.load_default()

    lines = [
        ("BIO EXPRESS MARCHE", True),
        ("14 RUE DU COMMERCE, 75015 PARIS", False),
        ("SIRET: 842 195 412 00021", False),
        ("TEL: 01 45 78 92 10", False),
        ("--------------------------------------------", False),
        ("DATE: 28/10/2026 15:42   TICKET N: TK-8491", False),
        ("CAISSE: 02               CAISSIER: PIERRE", False),
        ("--------------------------------------------", False),
        ("ARTICLES                     QTE    PRIX", False),
        ("--------------------------------------------", False),
        ("PAIN COMPLET BIO 500G        1.0    2.20", False),
        ("LAIT DEMI-ECREME 1L          2.0    2.50", False),
        ("POMMES GALA 1.5KG            1.0    3.80", False),
        ("BEURRE DOUX 250G             1.0    2.40", False),
        ("JUS D'ORANGE PUR JUS 1L      1.0    2.10", False),
        ("--------------------------------------------", False),
        ("SOUS-TOTAL HT                     12.32 EUR", True),
        ("TVA (5.5%)                         0.68 EUR", False),
        ("============================================", False),
        ("TOTAL TTC                         13.00 EUR", True),
        ("============================================", False),
        ("PAIEMENT PAR CARTE BANCAIRE       13.00 EUR", False),
        ("--------------------------------------------", False),
        ("        MERCI DE VOTRE VISITE !", False),
        ("            A TRES BIENTOT", False),
    ]

    y = 30
    for text, bold in lines:
        # Centrer ou aligner
        if "---" in text or "===" in text or "MERCI" in text or "BIO EXPRESS" in text or "RUE DU" in text or "A TRES" in text or "SIRET" in text or "TEL:" in text:
            bbox = draw.textbbox((0, 0), text, font=font)
            line_w = bbox[2] - bbox[0]
            x = (width - line_w) // 2
        else:
            x = 35

        draw.text((x, y), text, fill=text_color, font=font)
        if bold:
            # Effet gras léger par décalage de 1 pixel
            draw.text((x + 1, y), text, fill=text_color, font=font)
        y += 24

    img.save(filename)
    print(f"Ticket d'exemple généré avec succès : {filename}")

if __name__ == "__main__":
    create_sample_receipt()
