# core/temporal_graph.py
import networkx as nx
from typing import List, Tuple
from .ontology import EntiteOntique

class TisserandTemporal:
    def __init__(self):
        self.graphe = nx.DiGraph()

    def ajouter_entite(self, entite: EntiteOntique):
        self.graphe.add_node(entite.id, data=entite)

    def tisser_lien(self, id_source: str, id_cible: str, force: float, type_lien: str = "causal"):
        """type_lien: 'causal' (passé -> futur) ou 'retrocausal' (futur -> passé)"""
        self.graphe.add_edge(id_source, id_cible, weight=force, type=type_lien)

    def detecter_paradoxes(self) -> List[List[str]]:
        """Un paradoxe est un cycle dans le graphe orienté"""
        try:
            # nx.simple_cycles trouve toutes les boucles fermées
            cycles = list(nx.simple_cycles(self.graphe))
            return [cycle for cycle in cycles if len(cycle) >= 1]
        except nx.NetworkXError:
            return []

    def appliquer_guérison_quantique(self, cycle: List[str]):
        """Réduit le Delta des entités impliquées dans un paradoxe pour 'stabiliser' la Trame"""
        for node_id in cycle:
            if self.graphe.has_node(node_id):
                entite: EntiteOntique = self.graphe.nodes[node_id]['data']
                entite.delta_pendant = max(0.05, entite.delta_pendant * 0.5) # Effondrement contrôlé
                entite.coeur_dominant = "noir" # Le paradoxe corrompt
