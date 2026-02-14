from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import shutil
import os
import json
from datetime import datetime
from ai_engine import analyze_incident

app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

DB_FILE = "database.json"

def load_db():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, "r") as f: return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4, default=str)

@app.post("/api/submit_report")
async def submit_report(
    is_anonymous: bool = Form(...),
    village: str = Form(...),
    child_name: str = Form(...),
    abuser_name: str = Form(...),
    description: str = Form(...),
    emetteur_login: str = Form(...),
    files: List[UploadFile] = File(None)
):
    emetteur_final = "Anonyme" if is_anonymous else emetteur_login
    saved_files = []
    
    if files:
        for file in files:
            # Nettoyage nom de fichier
            safe_name = f"{int(time.time())}_{file.filename.replace(' ', '_')}"
            file_path = f"uploads/{safe_name}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files.append(safe_name)

    # Appel IA
    ai_analysis = analyze_incident(description)

    db = load_db()
    new_report = {
        "id": len(db) + 1,
        "date": datetime.now().isoformat(),
        "village": village,     # IMPORTANT : C'est ici qu'on filtre plus tard
        "child_name": child_name,
        "abuser_name": abuser_name,
        "emetteur": emetteur_final,
        "description_originale": description,
        "preuves_fichiers": saved_files,
        "categorie_ia": ai_analysis["category"],
        "urgence_ia": ai_analysis["urgency"],
        "conseil_ia": ai_analysis["recommendation"],
        "statut": "En attente",
        "validateur": ""
    }
    
    db.append(new_report)
    save_db(db)
    return {"message": "Reçu", "analysis": ai_analysis}

# --- NOUVELLE LOGIQUE DE FILTRAGE ---
@app.get("/api/reports")
def get_reports(role: str = None, village: str = None):
    data = load_db()
    
    # Le Directeur voit tout
    if role == "dir":
        return data
    
    # Le Psy ne voit QUE son village
    if role == "psy" and village and village != "all":
        # On filtre la liste Python
        filtered_data = [r for r in data if r["village"] == village]
        return filtered_data
        
    return data # Par défaut

class ValidationModel(BaseModel):
    report_id: int
    psy_name: str
    final_report: str
    decision: str 

@app.post("/api/validate_report")
def validate_report(data: ValidationModel):
    db = load_db()
    found = False
    for report in db:
        if report["id"] == data.report_id:
            report["statut"] = "Traité" if data.decision == "Valide" else "Rejeté"
            report["rapport_psy"] = data.final_report
            report["validateur"] = data.psy_name
            found = True
            break
    
    if found:
        save_db(db)
        return {"message": "Dossier traité"}
    raise HTTPException(status_code=404, detail="ID introuvable")

import time # Oubli import