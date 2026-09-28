# ui/gui_dashboard.py
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from datetime import datetime, timedelta
import numpy as np

class DashboardLeviathan:
    def __init__(self, db, graph_engine, timewave_engine):
        self.db = db
        self.graph = graph_engine
        self.tw = timewave_engine
        
        self.root = tk.Tk()
        self.root.title("🌀 CHRONOS-TRAME : Tableau de Bord du Léviathan")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0f0f1b")
        
        self._creer_interface()
        self._tracer_graphe()
        self._tracer_timewave()

    def _creer_interface(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Onglet 1: Graphe Temporel
        self.tab_graphe = ttk.Frame(notebook)
        notebook.add(self.tab_graphe, text="🕸️ Graphe des Âges (Paradoxes)")
        self.fig_graphe, self.ax_graphe = plt.subplots(figsize=(10, 6))
        self.fig_graphe.patch.set_facecolor('#0f0f1b')
        self.ax_graphe.set_facecolor('#1a1a2e')
        self.canvas_graphe = FigureCanvasTkAgg(self.fig_graphe, self.tab_graphe)
        self.canvas_graphe.get_tk_widget().pack(fill="both", expand=True)
        
        # Onglet 2: Onde TimeWave
        self.tab_tw = ttk.Frame(notebook)
        notebook.add(self.tab_tw, text="🌊 Onde de Nouveauté (TimeWave Zero)")
        self.fig_tw, self.ax_tw = plt.subplots(figsize=(10, 6))
        self.fig_tw.patch.set_facecolor('#0f0f1b')
        self.ax_tw.set_facecolor('#1a1a2e')
        self.canvas_tw = FigureCanvasTkAgg(self.fig_tw, self.tab_tw)
        self.canvas_tw.get_tk_widget().pack(fill="both", expand=True)

    def _tracer_graphe(self):
        self.ax_graphe.clear()
        G = self.graph.graphe
        
        if len(G.nodes) == 0:
            self.ax_graphe.text(0.5, 0.5, "Le Léviathan dort. Aucune entité dans le graphe.", 
                                color='white', ha='center', va='center')
        else:
            pos = nx.spring_layout(G, seed=42, k=0.9)
            
            # Couleurs des nœuds selon le cœur
            node_colors = []
            for node in G.nodes():
                coeur = G.nodes[node]['data'].coeur_dominant
                if coeur == 'noir': node_colors.append('#ff3333')
                elif coeur == 'blanc': node_colors.append('#ffffff')
                else: node_colors.append('#aaaaaa')
            
            nx.draw(G, pos, ax=self.ax_graphe, with_labels=True, node_color=node_colors, 
                    node_size=800, font_size=8, font_weight='bold', edge_color='#4ec9b0', 
                    arrows=True, arrowsize=15)
            
            # Mise en évidence des paradoxes
            paradoxes = self.graph.detecter_paradoxes()
            if paradoxes:
                for cycle in paradoxes:
                    if len(cycle) >= 1:
                        nx.draw_networkx_edges(G, pos, edgelist=list(zip(cycle, cycle[1:] + [cycle[0]])), 
                                               edge_color='cyan', width=3, ax=self.ax_graphe)
                        
        self.ax_graphe.set_title("Topologie Ontique & Cycles Rétrocausaux", color='white')
        self.canvas_graphe.draw()

    def _tracer_timewave(self):
        self.ax_tw.clear()
        # Générer 500 points entre 1950 et 2030
        start = datetime(1950, 1, 1)
        dates = [start + timedelta(days=i*60) for i in range(500)]
        novelty = [self.tw.calculer_nouveaute(d) for d in dates]
        
        self.ax_tw.plot(dates, novelty, color='#00ffff', linewidth=1, alpha=0.7)
        self.ax_tw.fill_between(dates, novelty, color='#00ffff', alpha=0.1)
        
        # Superposition des entités BDO (simulée)
        entites = self.db.obtenir_toutes_entites()
        for ent in entites[:20]: # Limiter pour la démo
            try:
                d = datetime.strptime(ent.date_debut, "%Y-%m-%d")
                nov = self.tw.calculer_nouveaute(d)
                color = 'red' if ent.coeur_dominant == 'noir' else 'white'
                self.ax_tw.scatter(d, nov, color=color, s=30, edgecolors='black', zorder=5)
            except ValueError:
                pass
                
        self.ax_tw.set_title("Courbe de Nouveauté & Superposition des Anomalies BDO", color='white')
        self.ax_tw.tick_params(colors='lightgray')
        self.canvas_tw.draw()

    def run(self):
        self.root.mainloop()
