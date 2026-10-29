import sys
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
import json
from ocr_engine import extract_text_from_image
from extractor import extract_invoice_data
from validator import validate_invoice_math

print("1. Lecture OCR...")
raw_text = extract_text_from_image("sample_ticket.png")
print(f"   OCR extrait ({len(raw_text)} caractères) :")
for l in raw_text.splitlines()[:5]:
    print("   >", l)

print("\n2. Extraction structurée LLM via Ollama (qwen2.5:3b)...")
data = extract_invoice_data(raw_text, "qwen2.5:3b")
print(json.dumps(data, indent=2, ensure_ascii=False))

print("\n3. Contrôle arithmétique...")
val = validate_invoice_math(data)
print("   Valide :", val["is_valid"])
for c in val["checks"]:
    print("   >", c)
