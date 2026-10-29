"""
Module de validation arithmétique des données extraites.
Vérifie la cohérence comptable :
1. Somme des articles (HT ou TTC)
2. Total HT + TVA = Total TTC
Tolérance de 0.05 € pour absorber les arrondis de centimes.
"""

def validate_invoice_math(data: dict, tolerance: float = 0.05) -> dict:
    """
    Contrôle les montants extraits par le LLM et signale toute incohérence.
    
    Retourne un dictionnaire avec :
    - is_valid : bool (True si les comptes tombent juste)
    - sum_lines : somme calculée de toutes les lignes d'articles
    - checks : liste de diagnostics détaillés
    - warning_level : "success" | "warning" | "error"
    """
    checks = []
    
    # 1. Extraction et conversion sécurisée des valeurs numériques
    try:
        total_ht = float(data.get("total_ht") or 0.0)
    except (ValueError, TypeError):
        total_ht = 0.0

    try:
        montant_tva = float(data.get("montant_tva") or 0.0)
    except (ValueError, TypeError):
        montant_tva = 0.0

    try:
        total_ttc = float(data.get("total_ttc") or 0.0)
    except (ValueError, TypeError):
        total_ttc = 0.0

    # 2. Calcul de la somme des lignes d'articles
    lignes = data.get("lignes", []) or []
    sum_lines = 0.0
    for idx, item in enumerate(lignes, 1):
        try:
            tot = float(item.get("total_ligne") or 0.0)
            if tot == 0.0:
                qte = float(item.get("quantite") or 1.0)
                pu = float(item.get("prix_unitaire") or 0.0)
                tot = qte * pu
            sum_lines += tot
        except (ValueError, TypeError):
            checks.append(f"⚠️ Ligne {idx} : Valeur numérique non analysable.")

    sum_lines = round(sum_lines, 2)
    total_ht = round(total_ht, 2)
    montant_tva = round(montant_tva, 2)
    total_ttc = round(total_ttc, 2)

    is_valid = True
    warning_level = "success"

    # 3. Test 1 : Cohérence HT + TVA = TTC
    expected_ttc = round(total_ht + montant_tva, 2)
    diff_tva_ttc = round(abs(expected_ttc - total_ttc), 2)

    if total_ttc > 0 and (total_ht > 0 or montant_tva > 0):
        if diff_tva_ttc <= tolerance:
            checks.append(f"✅ Équation légale vérifiée : HT ({total_ht:.2f} €) + TVA ({montant_tva:.2f} €) = TTC ({total_ttc:.2f} €).")
        else:
            is_valid = False
            warning_level = "warning"
            checks.append(
                f"❌ Écart TVA/TTC détecté : HT ({total_ht:.2f} €) + TVA ({montant_tva:.2f} €) = {expected_ttc:.2f} € au lieu de {total_ttc:.2f} € (écart de {diff_tva_ttc:.2f} €)."
            )

    # 4. Test 2 : Cohérence de la somme des lignes
    if lignes and total_ttc > 0:
        diff_lines_vs_ttc = round(abs(sum_lines - total_ttc), 2)
        diff_lines_vs_ht = round(abs(sum_lines - total_ht), 2)

        # Les lignes d'un ticket de supermarché sont généralement exprimées en TTC
        if diff_lines_vs_ttc <= tolerance:
            checks.append(f"✅ Somme des lignes ({sum_lines:.2f} €) correspond au Total TTC ({total_ttc:.2f} €).")
        # Les lignes d'une facture pro B2B sont généralement exprimées en HT
        elif total_ht > 0 and diff_lines_vs_ht <= tolerance:
            checks.append(f"✅ Somme des lignes ({sum_lines:.2f} €) correspond au Total HT ({total_ht:.2f} €).")
        # Ou vérification directe : Somme des lignes HT + TVA = TTC
        elif total_ht == 0 and montant_tva > 0 and round(abs((sum_lines + montant_tva) - total_ttc), 2) <= tolerance:
            checks.append(f"✅ Somme des lignes ({sum_lines:.2f} €) + TVA ({montant_tva:.2f} €) = Total TTC ({total_ttc:.2f} €).")
        else:
            is_valid = False
            warning_level = "warning"
            checks.append(
                f"⚠️ Somme des {len(lignes)} article(s) = {sum_lines:.2f} €. Elle ne correspond ni au Total HT ({total_ht:.2f} €) ni au Total TTC ({total_ttc:.2f} €)."
            )
    elif not lignes and total_ttc > 0:
        checks.append("ℹ️ Aucun article détaillé n'a été trouvé dans le document (ticket simplifié ou OCR incomplet).")

    return {
        "is_valid": is_valid,
        "warning_level": warning_level,
        "sum_lines": sum_lines,
        "total_ht": total_ht,
        "montant_tva": montant_tva,
        "total_ttc": total_ttc,
        "expected_ttc": expected_ttc,
        "checks": checks
    }
