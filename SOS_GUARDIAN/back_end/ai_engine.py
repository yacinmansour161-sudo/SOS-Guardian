import time
from textblob import TextBlob

# Dictionnaire de "poids" pour les mots
KEYWORDS_WEIGHTS = {
    # DROGUE / ADDICTION
    "drogue": 5, "zatla": 5, "ecstasy": 5, "pilule": 4, "seringue": 5, 
    "inconscient": 5, "overdose": 5, "fumer": 3,
    
    # VIOLENCE
    "sang": 5, "frapper": 4, "coup": 4, "bleu": 3, "trace": 3, 
    "brulure": 5, "couteau": 5, "arme": 5, "battu": 4, "tuer": 5,
    
    # ABUS
    "viol": 5, "attouchement": 5, "nu": 4, "force": 4, "lit": 3,
    
    # DETRESSE
    "suicide": 5, "mourir": 5, "triste": 2, "pleure": 2
}

def analyze_incident(text: str):
    time.sleep(0.5) 
    
    text_lower = text.lower()
    total_score = 0
    detected_categories = set()

    # ANALYSE MOTS CLÉS
    for word, weight in KEYWORDS_WEIGHTS.items():
        if word in text_lower:
            total_score += weight
            
            # Catégorisation
            if weight >= 4:
                if word in ["drogue", "zatla", "pilule", "inconscient"]:
                    detected_categories.add("DANGER IMMÉDIAT (Drogues/Addiction)")
                else:
                    detected_categories.add("DANGER IMMÉDIAT (Violence/Abus)")
            elif word in ["triste", "pleure"]:
                detected_categories.add("Psychologique")

    # CALCUL URGENCE (Plafond à 5)
    final_urgency = 1
    if total_score >= 5: final_urgency = 5
    elif total_score >= 3: final_urgency = 3
    elif total_score >= 1: final_urgency = 2

    # Si aucune catégorie n'est trouvée mais qu'il y a des mots clés
    cat_str = ", ".join(detected_categories) if detected_categories else "Autre / A vérifier"

    # PRINT DE DEBUG (Regarde ton terminal noir quand tu envoies !)
    print(f"--- ANALYSE IA --- Texte: {text} | Mots trouvés (Score {total_score}) -> Urgence {final_urgency}")

    return {
        "category": cat_str,
        "urgency": final_urgency,
        "recommendation": "Intervention immédiate" if final_urgency >= 4 else "Suivi requis"
    }