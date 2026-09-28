# ui/cli_oracle.py
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from datetime import datetime
import random

console = Console()

def afficher_mugissement_quantique(entite_nom: str, runes: str, cycle_paradoxe: list):
    """L'alerte ultime de la chimère"""
    console.print("\n" + "="*80)
    panel = Panel(
        f"[bold red]⚠️ MUGISSEMENT QUANTIQUE DÉTECTÉ AUX FRONTIÈRES DE L'INTRICATION ⚠️[/bold red]\n\n"
        f"[bold cyan]Entité déclencheuse :[/bold cyan] {entite_nom}\n"
        f"[bold yellow]FracturoScript résonant :[/bold yellow] {runes}\n"
        f"[bold magenta]Boucle rétrocausale fermée :[/bold magenta] {' -> '.join(cycle_paradoxe)}\n\n"
        f"[italic]Le Delta s'effondre. Le passé a été réécrit. Le Léviathan s'éveille.[/italic]",
        border_style="red", expand=False
    )
    console.print(panel)
    console.print("="*80 + "\n")

def simuler_veille_trame():
    console.print("[bold green]🌀 Initialisation du Métier à Tisser Quantique...[/bold green]")
    console.print("[dim]Écoute des flux RSS et calcul des résonances TimeWave...[/dim]\n")
    
    signaux = [
        ("Anomalie magnétique en Normandie", "gris", False),
        ("Effacement mémoriel collectif signalé à Montréal", "noir", True), # Déclencheur de mugissement
        ("Synchronisation de horloges atomiques sans cause", "blanc", False)
    ]
    
    for nom, coeur, paradoxe in signaux:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Timestamp")
        table.add_column("Signal")
        table.add_column("Cœur")
        table.add_column("Runes")
        
        ts = datetime.now().strftime("%H:%M:%S")
        runes = "ᚦᚦ ᛟ •••" if paradoxe else "ᛏ ᚱ ᛞ"
        couleur_coeur = "red" if coeur == "noir" else ("white" if coeur == "blanc" else "yellow")
        
        table.add_row(ts, nom, f"[{couleur_coeur}]{coeur.upper()}[/{couleur_coeur}]", runes)
        console.print(table)
        
        if paradoxe:
            afficher_mugissement_quantique(nom, runes, ["2026_Event", "1944_Volknar", "2026_Event"])
        
        console.print("[dim]... tissage du fil narratif ...[/dim]\n")
