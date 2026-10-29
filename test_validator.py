"""
Test unitaire de la logique de validation arithmétique.
"""
import sys
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
from validator import validate_invoice_math

def test_valid_receipt():
    sample_data = {
        "emetteur": "Supermarché Express",
        "date": "2026-10-25",
        "lignes": [
            {"description": "Pain de mie", "quantite": 2.0, "prix_unitaire": 1.50, "total_ligne": 3.00},
            {"description": "Lait 1L", "quantite": 1.0, "prix_unitaire": 1.20, "total_ligne": 1.20},
            {"description": "Pommes Gala", "quantite": 1.0, "prix_unitaire": 2.80, "total_ligne": 2.80}
        ],
        "total_ht": 6.35,
        "montant_tva": 0.65,
        "total_ttc": 7.00
    }
    
    result = validate_invoice_math(sample_data)
    print("Test 1 - Ticket cohérent :", result["is_valid"], result["checks"])
    assert result["is_valid"] is True
    assert result["sum_lines"] == 7.00

def test_inconsistent_receipt():
    sample_data = {
        "emetteur": "Quincaillerie Pro",
        "date": "2026-10-20",
        "lignes": [
            {"description": "Vis inox", "quantite": 10.0, "prix_unitaire": 1.00, "total_ligne": 10.00}
        ],
        "total_ht": 10.00,
        "montant_tva": 2.00,
        "total_ttc": 15.00  # Erreur voulue : 10 + 2 != 15
    }
    
    result = validate_invoice_math(sample_data)
    print("Test 2 - Ticket avec erreur :", result["is_valid"], result["checks"])
    assert result["is_valid"] is False

if __name__ == "__main__":
    test_valid_receipt()
    test_inconsistent_receipt()
    print("Tous les tests arithmétiques sont validés avec succès !")
