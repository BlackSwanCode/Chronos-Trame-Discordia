# main.py
import argparse
import os
from core.fracturo_engine import FracturoEngine
from core.temporal_graph import TisserandTemporal
from core.timewave import TimeWaveZero
from storage.leviathan_db import LeviathanDB
from ui.cli_oracle import simuler_veille_trame

def main():
    parser = argparse.ArgumentParser(description="🌀 CHRONOS-TRAME v1.0 - Le Léviathan Ontique")
    parser.add_argument("--mode", choices=["cli", "gui"], default="gui", help="Interface à utiliser")
    args = parser.parse_args()

    print("🌀 Éveil du Léviathan Ontique...")
    
    # 1. Initialisation des moteurs
    db = LeviathanDB("leviathan.db")
    
    # Charger le corpus BDO s'il existe (ou créer un mock pour la démo)
    if not os.path.exists("data/bdo_corpus_sample.json"):
        os.makedirs("data", exist_ok=True)
        with open("data/bdo_corpus_sample.json", "w", encoding="utf-8") as f:
            import json
            json.dump([{
                "id": "demo_001", "nom": "Synchronicité de Vauville", "description": "Alignement runique spontané",
                "date_debut": "1999-12-31", "taxonomie": {"classe_principale": "ESC"}, 
                "coeur_dominant": "gris", "delta_estime": {"pendant": 0.4}, "risque": 2
            }], f)
            
    db.charger_corpus_bdo("data/bdo_corpus_sample.json")
    
    fracturo = FracturoEngine()
    tisserand = TisserandTemporal()
    timewave = TimeWaveZero()
    
    # 2. Peupler le graphe avec les données de la DB
    entites = db.obtenir_toutes_entites()
    for ent in entites:
        tisserand.ajouter_entite(ent)
        ent.fragments_runiques = fracturo.traduire_en_runes(ent.nom).split('•')
        ent.paleo_memes = fracturo.detecter_meme(ent.description)
        
    # Créer un lien rétrocausal artificiel pour la démo du paradoxe
    if len(entites) >= 1:
        tisserand.tisser_lien(entites[0].id, entites[0].id, 0.9, "retrocausal") # Boucle sur soi-même = paradoxe

    # 3. Lancement
    if args.mode == "cli":
        simuler_veille_trame()
    else:
        from ui.gui_dashboard import DashboardLeviathan
        print("🖥️ Lancement du Tableau de Bord Quantique...")
        app = DashboardLeviathan(db, tisserand, timewave)
        app.run()

if __name__ == "__main__":
    main()
