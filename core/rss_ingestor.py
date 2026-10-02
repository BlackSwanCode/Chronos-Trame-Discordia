# core/rss_ingestor.py
import re
import socket
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import feedparser
from rich.console import Console
from rich.markup import escape

from .ontology import EntiteOntique
from .fracturo_engine import FracturoEngine
from .temporal_graph import TisserandTemporal
from .timewave import TimeWaveZero
from .webhook_notifier import DiscordNotifier
from storage.leviathan_db import LeviathanDB

console = Console()

# Mots-clés pour la classification heuristique automatique (sans LLM)
TRIGGERS_NOIR = ["anomalie", "inexpliqué", "effondrement", "disparition", "secret",
                 "crise", "bug", "glitch", "paradoxe", "mystère"]
TRIGGERS_BLANC = ["harmonie", "découverte", "synchronicité", "lumière", "paix",
                  "résolution", "miracle"]

_TAGS_HTML = re.compile(r"<[^>]+>")


class RSSIngestor:
    def __init__(self, db: LeviathanDB, fracturo: FracturoEngine, tisserand: TisserandTemporal,
                 timewave: TimeWaveZero, webhook_url: Optional[str] = None):
        self.db = db
        self.fracturo = fracturo
        self.tisserand = tisserand
        self.timewave = timewave
        self.notifier = DiscordNotifier(webhook_url)
        # Pré-calculer l'historique de nouveauté pour les pics
        self.historique_nouveaute = self._generer_historique_nouveaute()
        # Cache local des entités connues (évite de relire toute la base à chaque entrée)
        self._entites: Dict[str, EntiteOntique] = {e.id: e for e in self.db.obtenir_toutes_entites()}
        # Les objets du graphe font foi (ce sont eux que la "guérison" modifie)
        for node_id, attrs in self.tisserand.graphe.nodes(data=True):
            if "data" in attrs:
                self._entites[node_id] = attrs["data"]
        self.nb_nouvelles = 0
        self.nb_mugissements = 0

    def _generer_historique_nouveaute(self) -> List[float]:
        """Génère un échantillon de nouveauté pour le calcul des percentiles"""
        debut = datetime(1950, 1, 1)
        return [self.timewave.calculer_nouveaute(debut + timedelta(days=i * 60)) for i in range(500)]

    def _classifier_heuristique(self, texte: str) -> Dict[str, Any]:
        """Détermine le Cœur et le Delta de base selon les mots-clés"""
        texte_lower = texte.lower()
        score_noir = sum(1 for mot in TRIGGERS_NOIR if mot in texte_lower)
        score_blanc = sum(1 for mot in TRIGGERS_BLANC if mot in texte_lower)

        if score_noir >= 2 or (score_noir > 0 and score_noir > score_blanc):
            return {"coeur": "noir", "delta": 0.25}
        elif score_blanc > score_noir:
            return {"coeur": "blanc", "delta": 0.85}
        else:
            return {"coeur": "gris", "delta": 0.55}

    def _parser_date_rss(self, entry) -> str:
        """Extrait une date YYYY-MM-DD propre d'une entrée feedparser"""
        if getattr(entry, "published_parsed", None):
            return datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")
        elif getattr(entry, "updated_parsed", None):
            return datetime(*entry.updated_parsed[:6]).strftime("%Y-%m-%d")
        return datetime.now().strftime("%Y-%m-%d")  # Fallback à aujourd'hui

    def ingerer_flux(self, urls: List[str], max_entries_per_feed: int = 5):
        """Le cycle de digestion du Léviathan"""
        console.print("[bold cyan]📡 Activation des capteurs de la Trame...[/bold cyan]")
        socket.setdefaulttimeout(20)  # feedparser n'a pas de timeout propre

        for url in urls:
            console.print(f"  ↳ Aspiration de : {url}")
            try:
                feed = feedparser.parse(url)
                if feed.bozo:
                    console.print("    [yellow]⚠️ Flux malformé, mais tentative de lecture...[/yellow]")
                if not feed.entries:
                    console.print("    [yellow]⚠️ Aucune entrée récupérée.[/yellow]")
                    continue

                for entry in feed.entries[:max_entries_per_feed]:
                    self._traiter_entree(entry)
            except Exception as e:
                console.print(f"    [red]❌ Échec de l'aspiration : {e}[/red]")

    def _traiter_entree(self, entry):
        """Transforme une entrée RSS brute en Entité Ontique et vérifie les paradoxes"""
        titre = _TAGS_HTML.sub("", entry.get("title", "Sans titre")).strip() or "Sans titre"
        resume = _TAGS_HTML.sub("", entry.get("summary", entry.get("description", ""))).strip()
        date_str = self._parser_date_rss(entry)

        # 1. ID déterministe (évite les doublons lors des prochains scans)
        id_hash = hashlib.sha256(f"{titre}_{date_str}".encode("utf-8")).hexdigest()[:12]
        if id_hash in self._entites:
            return  # Déjà digéré

        # 2. Classification et enrichissement
        classification = self._classifier_heuristique(f"{titre} {resume}")
        entite = EntiteOntique(
            id=id_hash,
            nom=titre,
            description=resume[:200],  # Limite pour la DB
            date_debut=date_str,
            date_fin=None,
            classe_principale="IR",  # Par défaut : Information Réfractaire
            coeur_dominant=classification["coeur"],
            delta_avant=classification["delta"],
            delta_pendant=classification["delta"],
            delta_apres=classification["delta"],
            risque=4 if classification["coeur"] == "noir" else 2,
        )

        # Enrichissement Fracturo
        entite.fragments_runiques = self.fracturo.traduire_en_runes(entite.nom).split("•")
        entite.paleo_memes = self.fracturo.detecter_meme(entite.description)

        # 3. Injection dans le graphe temporel
        self.tisserand.ajouter_entite(entite)

        # 4. Tissage rétrocausal : le présent influence le passé.
        # On cherche une ancienne entité qui partage un paléo-mème, ou qui est déjà "noire".
        anciennes = [e for e in self._entites.values() if e.date_debut and e.date_debut < date_str]
        for ancienne in anciennes:
            if set(entite.paleo_memes) & set(ancienne.paleo_memes) or ancienne.coeur_dominant == "noir":
                self._tisser_boucle(entite, ancienne)
                break  # Un seul lien rétrocausal majeur par événement pour éviter le bruit

        # 5. Persistance en base
        self._entites[entite.id] = entite
        self.db.sauvegarder_entite(entite)
        self.nb_nouvelles += 1

        # 6. Vérification du Mugissement Quantique
        self._verifier_mugissement(entite)

    def _tisser_boucle(self, entite: EntiteOntique, ancienne: EntiteOntique):
        """Lien rétrocausal (nouveau ➜ ancien) + lien causal de retour (ancien ➜ nouveau).

        Sans le lien de retour, le graphe orienté ne contiendrait jamais de cycle
        impliquant la nouvelle entité : aucun paradoxe, donc aucun Mugissement possible.
        """
        self.tisserand.tisser_lien(entite.id, ancienne.id, force=0.85, type_lien="retrocausal")
        self.tisserand.tisser_lien(ancienne.id, entite.id, force=0.60, type_lien="causal")
        self.db.sauvegarder_lien(entite.id, ancienne.id, 0.85, "retrocausal")
        self.db.sauvegarder_lien(ancienne.id, entite.id, 0.60, "causal")
        console.print(f"    [magenta]🕸️ Lien rétrocausal tissé : {escape(entite.nom[:30])}... ➜ {escape(ancienne.nom[:30])}...[/magenta]")

    def _verifier_mugissement(self, entite: EntiteOntique):
        """Le cœur battant de l'alerte"""
        if entite.coeur_dominant != "noir":
            return

        # A. Y a-t-il un paradoxe impliquant cette entité ?
        cycles = self.tisserand.detecter_paradoxes()
        cycle_actif = next((c for c in cycles if entite.id in c), None)
        if not cycle_actif:
            return

        # B. Sommes-nous dans un pic de nouveauté TimeWave ?
        date_evt = datetime.strptime(entite.date_debut, "%Y-%m-%d")
        if self.timewave.est_pic_de_nouveaute(date_evt, self.historique_nouveaute):
            # 🚨 LE MUGISSEMENT SE PRODUIT 🚨
            self._declencher_alerte_omega(entite, cycle_actif)
            self.nb_mugissements += 1
            # Application de la "guérison" (corruption) puis sauvegarde de tout le cycle
            self.tisserand.appliquer_guérison_quantique(cycle_actif)
            for node_id in cycle_actif:
                if self.tisserand.graphe.has_node(node_id):
                    self.db.sauvegarder_entite(self.tisserand.graphe.nodes[node_id]["data"])

    def _declencher_alerte_omega(self, entite: EntiteOntique, cycle: List[str]):
        """Affiche en console, notifie Discord et persiste l'alerte critique"""
        runes = "".join(entite.fragments_runiques) if entite.fragments_runiques else "ᚦᚦ ᛟ •••"

        message_console = (
            f"⚠️ MUGISSEMENT QUANTIQUE DÉTECTÉ ⚠️\n"
            f"Entité : {entite.nom}\n"
            f"FracturoScript : {runes}\n"
            f"Boucle rétrocausale : {' ➜ '.join(cycle + [cycle[0]])}\n"
            f"Paléo-mèmes activés : {', '.join(entite.paleo_memes)}\n"
            f"Le Delta s'effondre. Le passé a été réécrit."
        )

        console.print("\n" + "=" * 70)
        console.print(f"[bold red on black]{escape(message_console)}[/bold red on black]")
        console.print("=" * 70 + "\n")

        # 🚨 Webhook Discord (silencieux si non configuré)
        self.notifier.send_omega_alert(
            entite_nom=entite.nom,
            runes=runes,
            cycle=cycle,
            paleo_memes=entite.paleo_memes,
            delta=entite.delta_pendant,
        )

        # Persistance locale de l'alerte
        self.db.sauvegarder_alerte(entite.id, "MUGISSEMENT_QUANTIQUE", message_console)
