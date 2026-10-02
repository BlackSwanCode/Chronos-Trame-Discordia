import argparse
import os
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import matplotlib
matplotlib.use('Agg')  # Mode headless pour export
import matplotlib.pyplot as plt
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress
import networkx as nx

from core.fracturo_engine import FracturoEngine
from core.temporal_graph import TisserandTemporal
from core.timewave import TimeWaveZero
from core.ontology import EntiteOntique
from storage.leviathan_db import LeviathanDB

console = Console()

def charger_config() -> dict:
    config_path = "data/config.json"
    default_config = {
        "db_path": "leviathan.db",
        "corpus_path": "data/bdo_corpus_sample.json",
        "timewave_zero_date": "2012-12-21",
        "discord_webhook_url": "",
        "rss_feeds": [
            "https://www.science-et-vie.com/rss",
            "https://www.futura-sciences.com/rss/actualites.xml"
        ],
        "rss_max_entries": 10
    }
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return {**default_config, **json.load(f)}
    os.makedirs("data", exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(default_config, f, indent=2)
    return default_config

def sauvegarder_config(config: dict):
    os.makedirs("data", exist_ok=True)
    with open("data/config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def initialiser_systeme(config: dict):
    db = LeviathanDB(config["db_path"])
    db.charger_corpus_bdo(config["corpus_path"])
    fracturo = FracturoEngine()
    tisserand = TisserandTemporal()
    timewave = TimeWaveZero(config["timewave_zero_date"])
    
    entites = db.obtenir_toutes_entites()
    for ent in entites:
        tisserand.ajouter_entite(ent)
        ent.fragments_runiques = fracturo.traduire_en_runes(ent.nom).split('•')
        ent.paleo_memes = fracturo.detecter_meme(ent.description)
        db.sauvegarder_attributs_calcules(ent)
    
    for source, cible, force, type_lien in db.obtenir_liens():
        tisserand.tisser_lien(source, cible, force, type_lien)
    
    return db, tisserand, timewave, fracturo, entites

def ingerer_flux_rss(config: dict, db, fracturo, tisserand, timewave, urls=None, max_entries=None):
    """Active l'ingestion RSS : le Léviathan digère les flux et peut déclencher un Mugissement."""
    from core.rss_ingestor import RSSIngestor

    # Webhook : config.json, sinon variable d'environnement (gérée aussi par DiscordNotifier)
    webhook_url = config.get("discord_webhook_url", "") or os.getenv("CHRONOS_TRAME_WEBHOOK_URL")
    flux = urls or config.get("rss_feeds", [])
    max_entries = max_entries or config.get("rss_max_entries", 10)

    if not flux:
        console.print("[yellow]Aucun flux RSS configuré (clé rss_feeds ou option --flux).[/]")
        return

    ingestor = RSSIngestor(db, fracturo, tisserand, timewave, webhook_url=webhook_url)
    console.print("[bold green]🌀 Le Léviathan ouvre ses mâchoires temporelles...[/bold green]")
    ingestor.ingerer_flux(flux, max_entries_per_feed=max_entries)

    console.print("\n[bold cyan]📊 Résumé de la digestion :[/bold cyan]")
    console.print(f"Nouvelles entités digérées : {ingestor.nb_nouvelles}")
    console.print(f"Mugissements déclenchés : {ingestor.nb_mugissements}")
    console.print(f"Entités totales en base : {len(db.obtenir_toutes_entites())}")
    console.print(f"Paradoxes actifs détectés : {len(tisserand.detecter_paradoxes())}")

def filtrer_entites(entites: List[EntiteOntique], args) -> List[EntiteOntique]:
    resultat = entites
    if hasattr(args, 'coeur') and args.coeur:
        resultat = [e for e in resultat if e.coeur_dominant == args.coeur]
    if hasattr(args, 'classe') and args.classe:
        resultat = [e for e in resultat if e.classe_principale == args.classe]
    if hasattr(args, 'risque_min') and args.risque_min:
        resultat = [e for e in resultat if e.risque >= args.risque_min]
    if hasattr(args, 'date_debut') and args.date_debut:
        date_debut = datetime.strptime(args.date_debut, "%Y-%m-%d")
        resultat = [e for e in resultat if e.date_debut and datetime.strptime(e.date_debut, "%Y-%m-%d") >= date_debut]
    if hasattr(args, 'date_fin') and args.date_fin:
        date_fin = datetime.strptime(args.date_fin, "%Y-%m-%d")
        resultat = [e for e in resultat if e.date_debut and datetime.strptime(e.date_debut, "%Y-%m-%d") <= date_fin]
    return resultat

def detecter_mugissements(tisserand, timewave, entites, historique):
    critiques = []
    for cycle in tisserand.detecter_paradoxes():
        entites_cycle = [tisserand.graphe.nodes[n]["data"] for n in cycle]
        a_coeur_noir = any(e.coeur_dominant == "noir" for e in entites_cycle)
        a_pic = any(
            timewave.est_pic_de_nouveaute(datetime.strptime(e.date_debut, "%Y-%m-%d"), historique)
            for e in entites_cycle if e.date_debut
        )
        if a_coeur_noir and a_pic:
            critiques.append((cycle, entites_cycle))
    return critiques

def afficher_mugissement(nom: str, runes: str, boucle: str):
    message = (f"[bold red]Entité déclencheuse :[/] {nom}\n"
               f"[bold red]FracturoScript résonant :[/] {runes}\n"
               f"[bold red]Boucle rétrocausale fermée :[/] {boucle}\n\n"
               "[italic]Le Delta s'effondre. Le passé a été réécrit. Le Léviathan s'éveille.[/]")
    console.print(Panel(message, title="⚠️ MUGISSEMENT QUANTIQUE DÉTECTÉ ⚠️", border_style="red", expand=False))

def exporter_graphe(tisserand, output_path, format="png", theme="dark"):
    fig, ax = plt.subplots(figsize=(12, 8))
    if theme == "dark":
        fig.set_facecolor('#0f0f1b')
        ax.set_facecolor('#0f0f1b')
        text_color = 'white'
        edge_color = '#4ec9b0'
    else:
        text_color = 'black'
        edge_color = '#2c5f7c'
    
    G = tisserand.graphe
    if not G.nodes():
        ax.text(0.5, 0.5, "Aucune donnée", ha='center', va='center', color=text_color, fontsize=16)
        ax.set_axis_off()
    else:
        pos = nx.spring_layout(G, seed=42, k=0.9)
        node_colors = ["#ff3333" if G.nodes[n]['data'].coeur_dominant == "noir" 
                      else "#ffffff" if G.nodes[n]['data'].coeur_dominant == "blanc" 
                      else "#aaaaaa" for n in G.nodes()]
        labels = {node: G.nodes[node]['data'].nom for node in G.nodes()}
        
        nx.draw(G, pos, ax=ax, with_labels=True, labels=labels,
                node_color=node_colors, edge_color=edge_color, font_color=text_color,
                font_weight="bold", node_size=2000, font_size=9)
        
        for cycle in tisserand.detecter_paradoxes():
            edges = list(zip(cycle, cycle[1:] + [cycle[0]])) if len(cycle) > 1 else [(cycle[0], cycle[0])]
            nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color="cyan", width=3, ax=ax)
        
        ax.set_title("Topologie des Paradoxes Temporels", color=text_color, fontsize=14, pad=20)
    
    plt.tight_layout()
    plt.savefig(output_path, format=format, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    console.print(f"[green]✓ Graphe exporté :[/] {output_path}")

def exporter_timewave(timewave, entites, output_path, format="png", theme="dark", annee_debut=1950, annee_fin=2032):
    fig, ax = plt.subplots(figsize=(14, 6))
    if theme == "dark":
        fig.set_facecolor('#0f0f1b')
        ax.set_facecolor('#0f0f1b')
        text_color = 'white'
        line_color = '#4ec9b0'
    else:
        text_color = 'black'
        line_color = '#2c5f7c'
    
    debut = datetime(annee_debut, 1, 1)
    fin = datetime(annee_fin, 12, 31)
    pas_jours = 30
    dates = []
    valeurs = []
    current = debut
    while current <= fin:
        dates.append(current)
        valeurs.append(timewave.calculer_nouveaute(current))
        current += timedelta(days=pas_jours)
    
    ax.plot(dates, valeurs, color=line_color, linewidth=2)
    ax.fill_between(dates, valeurs, color=line_color, alpha=0.2)
    
    for ent in entites:
        try:
            d = datetime.strptime(ent.date_debut, "%Y-%m-%d")
            if debut <= d <= fin:
                v = timewave.calculer_nouveaute(d)
                couleur = "#ff3333" if ent.coeur_dominant == "noir" else "#ffffff" if ent.coeur_dominant == "blanc" else "#aaaaaa"
                ax.scatter(d, v, color=couleur, s=80, zorder=5, edgecolors=text_color, linewidth=0.5)
        except ValueError:
            pass
    
    ax.set_title("Courbe de Nouveauté (TimeWave Zero)", color=text_color, fontsize=14)
    ax.set_xlabel("Année", color=text_color)
    ax.set_ylabel("Nouveauté", color=text_color)
    ax.tick_params(colors=text_color)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, format=format, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    console.print(f"[green]✓ TimeWave exportée :[/] {output_path}")

def analyser_signaux_faibles(tisserand, timewave, entites, historique, seuil_pic=90, seuil_delta=0.7):
    console.print("\n[bold cyan]🔍 Analyse des Signaux Faibles[/]")
    console.print("=" * 60)
    
    signaux = []
    for ent in entites:
        try:
            if not ent.date_debut: continue
            date = datetime.strptime(ent.date_debut, "%Y-%m-%d")
            nouveaute = timewave.calculer_nouveaute(date)
            est_pic = timewave.est_pic_de_nouveaute(date, historique)
            
            score = 0
            if est_pic:
                score += 3
            if ent.coeur_dominant == "noir":
                score += 2
            if ent.delta_pendant >= seuil_delta:
                score += 2
            if ent.risque >= 4:
                score += 1
            
            if score >= 3:
                signaux.append({
                    'entite': ent,
                    'date': date,
                    'nouveaute': nouveaute,
                    'est_pic': est_pic,
                    'score': score
                })
        except ValueError:
            continue
    
    signaux.sort(key=lambda x: x['score'], reverse=True)
    
    table = Table(title=f"Signaux Faibles Détectés (seuil score ≥ 3)")
    table.add_column("Nom", style="cyan")
    table.add_column("Date", style="green")
    table.add_column("Cœur", style="magenta")
    table.add_column("Delta", justify="right")
    table.add_column("Nouveauté", justify="right")
    table.add_column("Pic", justify="center")
    table.add_column("Score", justify="right", style="bold yellow")
    
    for sig in signaux[:20]:
        e = sig['entite']
        table.add_row(
            e.nom[:40],
            sig['date'].strftime("%Y-%m-%d"),
            e.coeur_dominant.upper(),
            f"{e.delta_pendant:.2f}",
            f"{sig['nouveaute']:.2f}",
            "✓" if sig['est_pic'] else "✗",
            str(sig['score'])
        )
    
    console.print(table)
    return signaux

def analyser_cycles(tisserand):
    console.print("\n[bold cyan]🔄 Analyse des Cycles Temporels[/]")
    console.print("=" * 60)
    
    cycles = tisserand.detecter_paradoxes()
    
    if not cycles:
        console.print("[yellow]Aucun cycle détecté dans le graphe.[/]")
        return
    
    table = Table(title=f"{len(cycles)} cycle(s) détecté(s)")
    table.add_column("#", style="dim")
    table.add_column("Entités impliquées", style="cyan")
    table.add_column("Longueur", justify="right")
    table.add_column("Cœurs", style="magenta")
    
    for i, cycle in enumerate(cycles, 1):
        entites = [tisserand.graphe.nodes[n]["data"] for n in cycle]
        noms = ", ".join([e.nom[:25] for e in entites])
        coeurs = ", ".join([e.coeur_dominant.upper() for e in entites])
        table.add_row(str(i), noms, str(len(cycle)), coeurs)
    
    console.print(table)
    
    console.print("\n[bold]Détail des cycles :[/]")
    for i, cycle in enumerate(cycles, 1):
        entites = [tisserand.graphe.nodes[n]["data"] for n in cycle]
        console.print(f"\n[cyan]Cycle {i} :[/]")
        for j, ent in enumerate(entites):
            arrow = "→" if j < len(entites) - 1 else "→ [retour au début]"
            console.print(f"  {ent.nom} [{ent.coeur_dominant.upper()}] {arrow}")

def explorer_timewave(timewave, annee_debut=1950, annee_fin=2032, top_n=10):
    console.print("\n[bold cyan]🌊 Exploration de la Courbe TimeWave[/]")
    console.print("=" * 60)
    
    debut = datetime(annee_debut, 1, 1)
    fin = datetime(annee_fin, 12, 31)
    
    dates = []
    valeurs = []
    current = debut
    while current <= fin:
        dates.append(current)
        valeurs.append(timewave.calculer_nouveaute(current))
        current += timedelta(days=1)
    
    historique = valeurs
    pairs = list(zip(dates, valeurs))
    
    # Top pics
    top_pics = sorted(pairs, key=lambda x: x[1], reverse=True)[:top_n]
    console.print(f"\n[bold green]Top {top_n} pics de nouveauté :[/]")
    table = Table()
    table.add_column("Date", style="cyan")
    table.add_column("Nouveauté", justify="right", style="bold yellow")
    for date, val in top_pics:
        table.add_row(date.strftime("%Y-%m-%d"), f"{val:.2f}")
    console.print(table)
    
    # Top creux
    top_creux = sorted(pairs, key=lambda x: x[1])[:top_n]
    console.print(f"\n[bold blue]Top {top_n} creux de nouveauté :[/]")
    table = Table()
    table.add_column("Date", style="cyan")
    table.add_column("Nouveauté", justify="right", style="bold blue")
    for date, val in top_creux:
        table.add_row(date.strftime("%Y-%m-%d"), f"{val:.2f}")
    console.print(table)
    
    # Statistiques
    console.print(f"\n[bold]Statistiques globales :[/]")
    console.print(f"  Période : {debut.year} → {fin.year}")
    console.print(f"  Moyenne : {sum(valeurs)/len(valeurs):.2f}")
    console.print(f"  Max : {max(valeurs):.2f}")
    console.print(f"  Min : {min(valeurs):.2f}")
    console.print(f"  Écart-type : {(sum((v - sum(valeurs)/len(valeurs))**2 for v in valeurs)/len(valeurs))**0.5:.2f}")

def afficher_stats(db, tisserand, entites):
    console.print("\n[bold cyan]📊 Statistiques de la Base Ontique[/]")
    console.print("=" * 60)
    
    table = Table(title="Répartition par Cœur")
    table.add_column("Cœur", style="cyan")
    table.add_column("Nombre", justify="right")
    table.add_column("Pourcentage", justify="right")
    
    coeurs = {}
    for e in entites:
        coeurs[e.coeur_dominant] = coeurs.get(e.coeur_dominant, 0) + 1
    
    for coeur, count in sorted(coeurs.items()):
        pct = (count / len(entites)) * 100
        table.add_row(coeur.upper(), str(count), f"{pct:.1f}%")
    
    console.print(table)
    
    # Classes
    table = Table(title="Répartition par Classe")
    table.add_column("Classe", style="cyan")
    table.add_column("Nombre", justify="right")
    
    classes = {}
    for e in entites:
        classes[e.classe_principale] = classes.get(e.classe_principale, 0) + 1
    
    for classe, count in sorted(classes.items()):
        table.add_row(classe, str(count))
    
    console.print(table)
    
    # Cycles
    cycles = tisserand.detecter_paradoxes()
    console.print(f"\n[bold]Graphe :[/]")
    console.print(f"  Nœuds : {tisserand.graphe.number_of_nodes()}")
    console.print(f"  Arêtes : {tisserand.graphe.number_of_edges()}")
    console.print(f"  Cycles détectés : {len(cycles)}")

def exporter_rapport_json(db, tisserand, timewave, entites, output_path):
    rapport = {
        "timestamp": datetime.now().isoformat(),
        "statistiques": {
            "total_entites": len(entites),
            "nb_cycles": len(tisserand.detecter_paradoxes()),
            "nb_noeuds": tisserand.graphe.number_of_nodes(),
            "nb_aretes": tisserand.graphe.number_of_edges()
        },
        "entites": [],
        "cycles": []
    }
    
    for ent in entites:
        rapport["entites"].append({
            "id": ent.id,
            "nom": ent.nom,
            "description": ent.description,
            "date_debut": ent.date_debut,
            "classe": ent.classe_principale,
            "coeur": ent.coeur_dominant,
            "delta_pendant": ent.delta_pendant,
            "risque": ent.risque,
            "runes": "".join(ent.fragments_runiques),
            "paleo_memes": ent.paleo_memes
        })
    
    for cycle in tisserand.detecter_paradoxes():
        rapport["cycles"].append({
            "entites": cycle,
            "noms": [tisserand.graphe.nodes[n]["data"].nom for n in cycle]
        })
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(rapport, f, indent=2, ensure_ascii=False)
    
    console.print(f"[green]✓ Rapport JSON exporté :[/] {output_path}")

def creer_parser():
    parser = argparse.ArgumentParser(
        description="🌀 CHRONOS-TRAME v2.0 - Analyse et Exploration Ontique",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation :
  %(prog)s --mode cli                              Analyse complète par défaut
  %(prog)s --mode cli --stats                      Afficher les statistiques
  %(prog)s --mode cli --cycles                     Analyser les cycles temporels
  %(prog)s --mode cli --signaux                    Détecter les signaux faibles
  %(prog)s --mode cli --timewave                   Explorer la courbe TimeWave
  %(prog)s --mode cli --export-graphe graphe.png   Exporter le graphe
  %(prog)s --mode cli --export-timewave tw.svg     Exporter la TimeWave en SVG
  %(prog)s --mode cli --export-rapport data.json   Exporter un rapport complet
  %(prog)s --mode cli --coeur noir --risque-min 4  Filtrer les entités
  %(prog)s --ingerer                               Ingérer les flux RSS de config.json
  %(prog)s --ingerer --flux URL --max-entries 5    Ingérer un flux précis
        """
    )
    
    parser.add_argument("--mode", choices=["cli", "gui"], default="gui", help="Interface à utiliser")
    parser.add_argument("--config", action="store_true", help="Afficher la configuration actuelle")
    parser.add_argument("--set-zero-date", type=str, help="Modifier la date zéro (YYYY-MM-DD)")
    
    # Filtres
    parser.add_argument("--coeur", choices=["noir", "gris", "blanc"], help="Filtrer par cœur")
    parser.add_argument("--classe", type=str, help="Filtrer par classe (RM, IR, ESC, etc.)")
    parser.add_argument("--risque-min", type=int, help="Filtrer par risque minimum")
    parser.add_argument("--date-debut", type=str, help="Filtrer à partir de cette date (YYYY-MM-DD)")
    parser.add_argument("--date-fin", type=str, help="Filtrer jusqu'à cette date (YYYY-MM-DD)")
    
    # Analyses
    parser.add_argument("--stats", action="store_true", help="Afficher les statistiques")
    parser.add_argument("--cycles", action="store_true", help="Analyser les cycles temporels")
    parser.add_argument("--signaux", action="store_true", help="Détecter les signaux faibles")
    parser.add_argument("--timewave", action="store_true", help="Explorer la courbe TimeWave")
    parser.add_argument("--mugissements", action="store_true", help="Détecter les Mugissements Quantiques")
    parser.add_argument("--ingerer", action="store_true", help="Ingérer les flux RSS (implique --mode cli)")
    parser.add_argument("--flux", action="append", metavar="URL", help="URL de flux RSS à ingérer (répétable ; remplace rss_feeds de config.json)")
    parser.add_argument("--max-entries", type=int, help="Nombre max d'entrées par flux (défaut : rss_max_entries de config.json)")
    
    # Paramètres d'analyse
    parser.add_argument("--seuil-delta", type=float, default=0.7, help="Seuil de Delta pour signaux faibles (défaut: 0.7)")
    parser.add_argument("--seuil-pic", type=int, default=90, help="Percentile pour pic de nouveauté (défaut: 90)")
    parser.add_argument("--annee-debut", type=int, default=1950, help="Année de début pour exploration (défaut: 1950)")
    parser.add_argument("--annee-fin", type=int, default=2032, help="Année de fin pour exploration (défaut: 2032)")
    parser.add_argument("--top-n", type=int, default=10, help="Nombre de résultats à afficher (défaut: 10)")
    
    # Exports
    parser.add_argument("--export-graphe", type=str, metavar="PATH", help="Exporter le graphe (formats: png, svg, pdf, jpg)")
    parser.add_argument("--export-timewave", type=str, metavar="PATH", help="Exporter la TimeWave (formats: png, svg, pdf, jpg)")
    parser.add_argument("--export-rapport", type=str, metavar="PATH", help="Exporter un rapport JSON complet")
    parser.add_argument("--theme", choices=["dark", "light"], default="dark", help="Thème pour les exports (défaut: dark)")
    
    return parser

def main():
    parser = creer_parser()
    args = parser.parse_args()
    
    config = charger_config()
    
    # Modification de la configuration
    if args.set_zero_date:
        config["timewave_zero_date"] = args.set_zero_date
        sauvegarder_config(config)
        console.print(f"[green]✓ Date zéro mise à jour :[/] {args.set_zero_date}")
        if not any([args.stats, args.cycles, args.signaux, args.timewave, args.mugissements, 
                   args.export_graphe, args.export_timewave, args.export_rapport]):
            return
    
    if args.config:
        console.print("\n[bold cyan]Configuration actuelle :[/]")
        for key, value in config.items():
            console.print(f"  {key}: {value}")
        return
    
    if args.ingerer or args.flux:
        args.ingerer = True
        args.mode = "cli"

    if args.mode == "gui":
        from ui.gui_dashboard import DashboardLeviathan
        console.print("🖥️ Lancement du Tableau de Bord Quantique...")
        db, tisserand, timewave, fracturo, entites = initialiser_systeme(config)
        DashboardLeviathan(db, tisserand, timewave).run()
        return
    
    # Mode CLI
    console.print("\n[bold cyan]🌀 CHRONOS-TRAME : Analyse Ontique[/]")
    console.print("=" * 60)
    
    db, tisserand, timewave, fracturo, entites = initialiser_systeme(config)
    
    # Ingestion RSS (optionnelle) : puis rechargement des entités pour les analyses suivantes
    if args.ingerer:
        ingerer_flux_rss(config, db, fracturo, tisserand, timewave, urls=args.flux, max_entries=args.max_entries)
        entites = db.obtenir_toutes_entites()
    
    # Application des filtres
    entites_filtrees = filtrer_entites(entites, args)
    console.print(f"\n[dim]Entités chargées : {len(entites)} | Filtrées : {len(entites_filtrees)}[/]")
    
    # Historique pour analyses
    historique = [timewave.calculer_nouveaute(datetime(1950, 1, 1) + timedelta(days=i * 30)) for i in range(1000)]
    
    # Si aucune option spécifique, afficher l'analyse par défaut
    if not any([args.stats, args.cycles, args.signaux, args.timewave, args.mugissements, 
               args.export_graphe, args.export_timewave, args.export_rapport, args.ingerer]):
        args.stats = True
        args.mugissements = True
    
    # Exécutions
    if args.stats:
        afficher_stats(db, tisserand, entites_filtrees)
    
    if args.cycles:
        analyser_cycles(tisserand)
    
    if args.signaux:
        analyser_signaux_faibles(tisserand, timewave, entites_filtrees, historique, 
                                args.seuil_pic, args.seuil_delta)
    
    if args.timewave:
        explorer_timewave(timewave, args.annee_debut, args.annee_fin, args.top_n)
    
    if args.mugissements:
        console.print("\n[bold cyan]⚠️ Détection des Mugissements Quantiques[/]")
        console.print("=" * 60)
        mugissements = detecter_mugissements(tisserand, timewave, entites_filtrees, historique)
        
        if not mugissements:
            console.print("[green]✓ La Trame est stable. Aucun Mugissement Quantique détecté.[/]")
        else:
            for cycle, ents in mugissements:
                declencheur = next((e for e in ents if e.coeur_dominant == "noir"), ents[0])
                runes = "".join(declencheur.fragments_runiques) if declencheur.fragments_runiques else fracturo.traduire_en_runes(declencheur.nom)
                afficher_mugissement(declencheur.nom, runes, " → ".join(cycle + [cycle[0]]))
    
    # Exports
    if args.export_graphe:
        exporter_graphe(tisserand, args.export_graphe, 
                       format=Path(args.export_graphe).suffix[1:] or "png",
                       theme=args.theme)
    
    if args.export_timewave:
        exporter_timewave(timewave, entites_filtrees, args.export_timewave,
                         format=Path(args.export_timewave).suffix[1:] or "png",
                         theme=args.theme,
                         annee_debut=args.annee_debut,
                         annee_fin=args.annee_fin)
    
    if args.export_rapport:
        exporter_rapport_json(db, tisserand, timewave, entites_filtrees, args.export_rapport)
    
    console.print("\n[bold green]✓ Analyse terminée[/]")

if __name__ == "__main__":
    main()
