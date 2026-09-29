import argparse
import os
import json
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel

from core.fracturo_engine import FracturoEngine
from core.temporal_graph import TisserandTemporal
from core.timewave import TimeWaveZero
from storage.leviathan_db import LeviathanDB

def charger_config():
    config_path = "data/config.json"
    default_config = {"db_path": "leviathan.db", "corpus_path": "data/bdo_corpus_sample.json", "timewave_zero_date": "2012-12-21"}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return {**default_config, **json.load(f)}
    os.makedirs("data", exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(default_config, f, indent=2)
    return default_config

def detecter_mugissements(tisserand, tw, historique):
    critiques = []
    for cycle in tisserand.detecter_paradoxes():
        entites = [tisserand.graphe.nodes[n]["data"] for n in cycle]
        a_coeur_noir = any(e.coeur_dominant == "noir" for e in entites)
        a_pic = any(tw.est_pic_de_nouveaute(datetime.strptime(e.date_debut, "%Y-%m-%d"), historique) for e in entites if e.date_debut)
        if a_coeur_noir and a_pic:
            critiques.append((cycle, entites))
    return critiques

def afficher_mugissement_quantique(nom: str, runes: str, boucle: str):
    console = Console()
    message = (f"[bold red]Entité déclencheuse :[/] {nom}\n"
               f"[bold red]FracturoScript résonant :[/] {runes}\n"
               f"[bold red]Boucle rétrocausale fermée :[/] {boucle}\n\n"
               "[italic]Le Delta s'effondre. Le passé a été réécrit. Le Léviathan s'éveille.[/]")
    console.print(Panel(message, title="⚠️ MUGISSEMENT QUANTIQUE DÉTECTÉ ⚠️", border_style="red", expand=False))

def main():
    config = charger_config()
    parser = argparse.ArgumentParser(description="🌀 CHRONOS-TRAME v2.0 - Le Léviathan Ontique")
    parser.add_argument("--mode", choices=["cli", "gui"], default="gui", help="Interface à utiliser")
    args = parser.parse_args()

    print("🌀 Éveil du Léviathan Ontique...")
    print(f"📂 Base de données : {config['db_path']}")

    db = LeviathanDB(config["db_path"])
    db.charger_corpus_bdo(config["corpus_path"])
    
    fracturo = FracturoEngine()
    tisserand = TisserandTemporal()
    timewave = TimeWaveZero(config["timewave_zero_date"])

    # Enrichissement et persistance des données
    entites = db.obtenir_toutes_entites()
    for ent in entites:
        tisserand.ajouter_entite(ent)
        ent.fragments_runiques = fracturo.traduire_en_runes(ent.nom).split('•')
        ent.paleo_memes = fracturo.detecter_meme(ent.description)
        db.sauvegarder_attributs_calcules(ent)

    # Chargement des vrais liens (plus de boucle artificielle)
    for source, cible, force, type_lien in db.obtenir_liens():
        tisserand.tisser_lien(source, cible, force, type_lien)

    if args.mode == "cli":
        print("📡 Analyse de la Trame en cours...\n")
        historique = [timewave.calculer_nouveaute(datetime(1950, 1, 1) + timedelta(days=i * 60)) for i in range(500)]
        mugissements = detecter_mugissements(tisserand, timewave, historique)
        
        if not mugissements:
            print("✅ La Trame est stable. Aucun Mugissement Quantique détecté.\n")
        else:
            for cycle, ents in mugissements:
                declencheur = next((e for e in ents if e.coeur_dominant == "noir"), ents[0])
                runes = "".join(declencheur.fragments_runiques) if declencheur.fragments_runiques else fracturo.traduire_en_runes(declencheur.nom)
                afficher_mugissement_quantique(declencheur.nom, runes, " -> ".join(cycle + [cycle[0]]))
                print()
                
        print("📜 Registre des Entités Ontiques :")
        for ent in entites:
            print(f"  • {ent.nom} [{ent.coeur_dominant.upper()}] : {ent.description[:60]}...")
    else:
        from ui.gui_dashboard import DashboardLeviathan
        print("🖥️ Lancement du Tableau de Bord Quantique...")
        DashboardLeviathan(db, tisserand, timewave).run()

if __name__ == "__main__":
    main()
