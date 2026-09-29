import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from datetime import datetime, timedelta

class DashboardLeviathan:
    def __init__(self, db, graph_engine, timewave_engine):
        self.db = db
        self.tisserand = graph_engine
        self.timewave = timewave_engine
        
        self.root = tk.Tk()
        self.root.title("🌀 CHRONOS-TRAME : Tableau de Bord Quantique")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0f0f1b")
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tab_graphe = ttk.Frame(self.notebook)
        self.tab_tw = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_graphe, text="🕸️ Graphe des Âges (Paradoxes)")
        self.notebook.add(self.tab_tw, text="🌊 Onde de Nouveauté (TimeWave)")
        
        # Figure Graphe
        self.fig_graphe = Figure(figsize=(8, 6), dpi=100)
        self.fig_graphe.set_facecolor('#0f0f1b') # CORRECTION FOND BLANC
        self.ax_graphe = self.fig_graphe.add_subplot(111)
        self.ax_graphe.set_facecolor('#0f0f1b')
        self.canvas_graphe = FigureCanvasTkAgg(self.fig_graphe, master=self.tab_graphe)
        self.canvas_graphe.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Figure TimeWave
        self.fig_tw = Figure(figsize=(8, 6), dpi=100)
        self.fig_tw.set_facecolor('#0f0f1b')
        self.ax_tw = self.fig_tw.add_subplot(111)
        self.ax_tw.set_facecolor('#0f0f1b')
        self.ax_tw.tick_params(colors='white')
        self.ax_tw.xaxis.label.set_color('white')
        self.ax_tw.yaxis.label.set_color('white')
        self.ax_tw.title.set_color('white')
        self.canvas_tw = FigureCanvasTkAgg(self.fig_tw, master=self.tab_tw)
        self.canvas_tw.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self._tracer_graphe()
        self._tracer_timewave()

    def _tracer_graphe(self):
        self.ax_graphe.clear()
        G = self.tisserand.graphe
        
        if not G.nodes():
            self.ax_graphe.text(0.5, 0.5, "Le Léviathan dort... (Aucune donnée)", color='white', ha='center', va='center', fontsize=14)
            self.ax_graphe.set_axis_off()
            self.canvas_graphe.draw()
            return

        pos = nx.spring_layout(G, seed=42, k=0.9)
        node_colors = ["#ff3333" if G.nodes[n]['data'].coeur_dominant == "noir" else "#ffffff" if G.nodes[n]['data'].coeur_dominant == "blanc" else "#aaaaaa" for n in G.nodes()]
        
        # CORRECTION : Labels avec les noms au lieu des IDs
        labels = {node: G.nodes[node]['data'].nom for node in G.nodes()}
        
        nx.draw(G, pos, ax=self.ax_graphe, with_labels=True, labels=labels, 
                node_color=node_colors, edge_color="#4ec9b0", font_color="black", 
                font_weight="bold", node_size=1500, font_size=8)
        
        # Surligner les cycles
        for cycle in self.tisserand.detecter_paradoxes():
            edges = list(zip(cycle, cycle[1:] + [cycle[0]])) if len(cycle) > 1 else [(cycle[0], cycle[0])]
            nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color="cyan", width=3, ax=self.ax_graphe)
            
        self.ax_graphe.set_title("Topologie des Paradoxes Temporels", color="white", fontsize=12)
        self.canvas_graphe.draw()

    def _tracer_timewave(self):
        self.ax_tw.clear()
        debut = datetime(1950, 1, 1)
        dates = [debut + timedelta(days=i * 60) for i in range(500)]
        valeurs = [self.timewave.calculer_nouveaute(d) for d in dates]
        
        self.ax_tw.plot(dates, valeurs, color="#4ec9b0", linewidth=1.5)
        self.ax_tw.fill_between(dates, valeurs, color="#4ec9b0", alpha=0.2)
        
        for ent in self.db.obtenir_toutes_entites()[:20]:
            try:
                d = datetime.strptime(ent.date_debut, "%Y-%m-%d")
                v = self.timewave.calculer_nouveaute(d)
                couleur = "#ff3333" if ent.coeur_dominant == "noir" else "#ffffff"
                self.ax_tw.scatter(d, v, color=couleur, s=50, zorder=5)
            except ValueError:
                pass
                
        self.ax_tw.set_title("Courbe de Nouveauté (TimeWave Zero)", color="white", fontsize=12)
        self.ax_tw.grid(True, alpha=0.3)
        self.canvas_tw.draw()

    def run(self):
        self.root.mainloop()
