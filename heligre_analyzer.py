#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 CHRONOS-TRAME : MODULE D'ANALYSE POST-TISSAGE "HÉLIGRESQUE" 🐅
Filtre les paradoxes temporels par résonance mémétique et distance sémantique.
Génère des prophéties de cluster et exporte :
  - le graphe épuré en GraphML
  - les prophéties en JSON
  - une interface d'exploration HTML/JS autonome (D3.js)
"""

import sqlite3
import json
import re
import html
import networkx as nx
from collections import Counter
from datetime import datetime
from pathlib import Path

# --- CONFIGURATION DU FILTRE DE L'HÉLIGRE ---
SEUIL_RESONANCE_MEMETIQUE = 0.3
SEUIL_DISTANCE_SEMANTIQUE = 0.15
OUTPUT_GRAPHML = "leviathan_heligre_pur.graphml"
OUTPUT_PROPHETIES = "propheties_cluster.json"
OUTPUT_HTML = "trame_heligre_explorateur.html"

STOPWORDS = {
    "le", "la", "les", "un", "une", "des", "du", "de", "et", "ou", "à", "au", "aux",
    "en", "dans", "pour", "par", "sur", "ce", "cette", "ces", "son", "sa", "ses",
    "leur", "leurs", "qui", "que", "quoi", "dont", "où", "il", "elle", "on", "nous",
    "vous", "ils", "elles", "est", "sont", "a", "ont", "été", "être", "avoir", "plus",
    "très", "bien", "tout", "tous", "toute", "toutes", "avec", "sans", "sous", "après",
    "avant", "contre", "entre", "vers", "chez", "comme", "si", "mais", "donc", "or",
    "ni", "car", "ne", "pas", "point", "jamais", "rien", "aucun", "aucune", "y", "en",
    "the", "and", "is", "in", "to", "of", "a", "for", "on", "with", "as", "by", "at",
    "from", "an", "are", "was", "were", "be", "has", "have", "had", "do", "does", "did"
}


def normaliser_texte(texte: str) -> set:
    if not texte:
        return set()
    texte = re.sub(r'[^\w\s]', ' ', texte.lower())
    mots = set(texte.split())
    return mots - STOPWORDS


def calculer_resonance_memetique(memes_a: list, memes_b: list) -> float:
    set_a, set_b = set(memes_a), set(memes_b)
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def calculer_distance_semantique(desc_a: str, desc_b: str) -> float:
    mots_a = normaliser_texte(desc_a)
    mots_b = normaliser_texte(desc_b)
    if not mots_a and not mots_b:
        return 0.0
    intersection = len(mots_a & mots_b)
    union = len(mots_a | mots_b)
    return intersection / union if union > 0 else 0.0


def generer_prophetie_cluster(entites: list, score_global: float) -> str:
    noms = [e['nom'] for e in entites]
    coeurs = [e['coeur'] for e in entites]
    memes_tous = []
    for e in entites:
        memes_tous.extend(e.get('paleo_memes', []))

    meme_commun = Counter(memes_tous).most_common(1)
    meme_str = meme_commun[0][0] if meme_commun else "RÉSONANCE INCONNUE"

    polarite = "NOIR" if "noir" in coeurs else ("GRIS" if "gris" in coeurs else "BLANC")

    return (
        f"⚠️ [MUGISSEMENT QUANTIQUE VALIDÉ - Score: {score_global:.2f}] ⚠️\n"
        f"🌀 ENTITÉS LIÉES : {' <-> '.join(noms)}\n"
        f"👁️ POLARITÉ DOMINANTE : {polarite}\n"
        f"🔮 PALÉO-MÈME RÉSONNANT : {meme_str}\n"
        f"📜 SYNTHÈSE DU TISSEUR : La boucle est fermée. Ces événements ne sont pas des coïncidences, "
        f"mais les nœuds d'une même rétrocausalité {polarite}. Le FracturoScript vibre à l'unisson. "
        f"Le Delta s'effondre vers le Néant, révélant la géométrie sous-jacente de la Trame."
    )


def charger_donnees(db_path: str = "leviathan.db"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nom, description, date_debut, classe, coeur,
               delta_avant, delta_pendant, delta_apres, risque,
               runes, paleo_memes
        FROM entites
    """)
    entites = {row['id']: dict(row) for row in cursor.fetchall()}

    cursor.execute("SELECT source, cible, force, type FROM liens_temporels")
    liens = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return entites, liens


def reconstruire_graphe(entites: dict, liens: list) -> nx.DiGraph:
    G = nx.DiGraph()
    for nid, data in entites.items():
        G.add_node(nid, **data)
    for lien in liens:
        if lien['source'] in G and lien['cible'] in G:
            G.add_edge(lien['source'], lien['cible'],
                       force=lien.get('force', 0.5),
                       type=lien.get('type', 'causal'))
    return G


def appliquer_filtre_heligre(G: nx.DiGraph, entites: dict):
    cycles = list(nx.simple_cycles(G))
    print(f"️ {len(cycles)} cycles (paradoxes) bruts détectés dans la Trame.")

    clusters_valides = []
    propheties = []

    for i, cycle in enumerate(cycles):
        if len(cycle) < 2:
            continue

        entites_cycle = [entites[nid] for nid in cycle if nid in entites]
        if len(entites_cycle) < 2:
            continue

        scores_memetiques = []
        scores_semantiques = []

        for j in range(len(entites_cycle)):
            for k in range(j + 1, len(entites_cycle)):
                e1, e2 = entites_cycle[j], entites_cycle[k]
                scores_memetiques.append(
                    calculer_resonance_memetique(e1.get('paleo_memes', []),
                                                 e2.get('paleo_memes', []))
                )
                scores_semantiques.append(
                    calculer_distance_semantique(e1.get('description', ''),
                                                 e2.get('description', ''))
                )

        score_meme_moyen = sum(scores_memetiques) / len(scores_memetiques) if scores_memetiques else 0.0
        score_sem_moyen = sum(scores_semantiques) / len(scores_semantiques) if scores_semantiques else 0.0
        score_heligre = (0.6 * score_meme_moyen) + (0.4 * score_sem_moyen)

        if score_heligre >= SEUIL_RESONANCE_MEMETIQUE or score_sem_moyen >= SEUIL_DISTANCE_SEMANTIQUE:
            clusters_valides.append({
                "cycle_ids": cycle,
                "score_heligre": score_heligre,
                "score_meme": score_meme_moyen,
                "score_sem": score_sem_moyen,
                "entites": entites_cycle
            })
            propheties.append(generer_prophetie_cluster(entites_cycle, score_heligre))

    return clusters_valides, propheties


def exporter_graphml(clusters: list, entites: dict, output_path: str):
    G_pur = nx.DiGraph()
    for cluster in clusters:
        for nid in cluster["cycle_ids"]:
            if nid in entites:
                G_pur.add_node(nid, **entites[nid])
        for j in range(len(cluster["cycle_ids"])):
            src = cluster["cycle_ids"][j]
            tgt = cluster["cycle_ids"][(j + 1) % len(cluster["cycle_ids"])]
            if src in G_pur and tgt in G_pur:
                G_pur.add_edge(src, tgt,
                               weight=cluster["score_heligre"],
                               type="heligre_validated")

    nx.write_graphml(G_pur, output_path)
    print(f"🕸️ Graphe épuré exporté : {output_path}")


def exporter_propheties(propheties: list, output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(propheties, f, ensure_ascii=False, indent=2)
    print(f"💾 Prophéties sauvegardées : {output_path}")


def generer_html_autonome(clusters: list, entites: dict, propheties: list, output_path: str):
    """Génère un fichier HTML/JS autonome avec D3.js pour explorer le graphe."""

    # Préparation des données pour D3.js
    nodes_data = []
    links_data = []
    node_id_to_index = {}

    # Collecter tous les nœuds uniques des clusters
    all_node_ids = set()
    for cluster in clusters:
        all_node_ids.update(cluster["cycle_ids"])

    for idx, nid in enumerate(all_node_ids):
        if nid not in entites:
            continue
        e = entites[nid]
        node_id_to_index[nid] = idx
        nodes_data.append({
            "id": nid,
            "nom": e.get('nom', 'Inconnu'),
            "description": e.get('description', '') or '',
            "date_debut": e.get('date_debut', ''),
            "classe": e.get('classe', 'NC'),
            "coeur": e.get('coeur', 'gris'),
            "delta_pendant": e.get('delta_pendant', 0.5),
            "risque": e.get('risque', 1),
            "runes": e.get('runes', ''),
            "paleo_memes": e.get('paleo_memes', []) or [],
            "score_cluster": 0.0
        })

    # Calculer le score max par nœud (pour la taille)
    for cluster in clusters:
        score = cluster["score_heligre"]
        for nid in cluster["cycle_ids"]:
            if nid in node_id_to_index:
                idx = node_id_to_index[nid]
                if score > nodes_data[idx]["score_cluster"]:
                    nodes_data[idx]["score_cluster"] = score

    # Arêtes des cycles
    for cluster in clusters:
        cycle = cluster["cycle_ids"]
        for j in range(len(cycle)):
            src = cycle[j]
            tgt = cycle[(j + 1) % len(cycle)]
            if src in node_id_to_index and tgt in node_id_to_index:
                links_data.append({
                    "source": node_id_to_index[src],
                    "target": node_id_to_index[tgt],
                    "score": cluster["score_heligre"]
                })

    # Statistiques
    stats = {
        "total_entites": len(entites),
        "total_cycles_bruts": len(list(nx.simple_cycles(reconstruire_graphe(entites, [])))),
        "clusters_valides": len(clusters),
        "noeuds_affiches": len(nodes_data),
        "aretes_affichees": len(links_data),
        "score_moyen": sum(c["score_heligre"] for c in clusters) / len(clusters) if clusters else 0,
        "score_max": max((c["score_heligre"] for c in clusters), default=0)
    }

    # Injection JSON sécurisée
    nodes_json = json.dumps(nodes_data, ensure_ascii=False)
    links_json = json.dumps(links_data, ensure_ascii=False)
    propheties_json = json.dumps(propheties, ensure_ascii=False)
    stats_json = json.dumps(stats, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>🌀 Chronos-Trame : Explorateur Héligresque</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Segoe UI', Tahoma, sans-serif;
    background: #0f0f1b;
    color: #e0e0e0;
    overflow: hidden;
    height: 100vh;
  }}
  #app {{ display: flex; height: 100vh; }}

  /* Sidebar */
  #sidebar {{
    width: 340px;
    background: #16162a;
    border-right: 1px solid #2a2a4a;
    padding: 16px;
    overflow-y: auto;
    flex-shrink: 0;
  }}
  #sidebar h1 {{
    font-size: 18px;
    color: #4ec9b0;
    margin-bottom: 12px;
    border-bottom: 1px solid #2a2a4a;
    padding-bottom: 8px;
  }}
  .stat-box {{
    background: #1e1e36;
    padding: 10px;
    border-radius: 6px;
    margin-bottom: 8px;
    font-size: 13px;
  }}
  .stat-box .label {{ color: #888; font-size: 11px; }}
  .stat-box .value {{ color: #4ec9b0; font-size: 16px; font-weight: bold; }}

  #search {{
    width: 100%;
    padding: 8px;
    background: #0f0f1b;
    border: 1px solid #2a2a4a;
    color: #e0e0e0;
    border-radius: 4px;
    margin-bottom: 12px;
  }}
  .filter-group {{ margin-bottom: 12px; }}
  .filter-group label {{
    display: block;
    font-size: 12px;
    color: #888;
    margin-bottom: 4px;
  }}
  .filter-btn {{
    background: #1e1e36;
    border: 1px solid #2a2a4a;
    color: #e0e0e0;
    padding: 4px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    margin-right: 4px;
    margin-bottom: 4px;
  }}
  .filter-btn.active {{ background: #4ec9b0; color: #0f0f1b; }}
  .filter-btn.noir.active {{ background: #ff3333; }}
  .filter-btn.blanc.active {{ background: #ffffff; color: #0f0f1b; }}
  .filter-btn.gris.active {{ background: #aaaaaa; color: #0f0f1b; }}

  #propheties {{
    margin-top: 16px;
    border-top: 1px solid #2a2a4a;
    padding-top: 12px;
  }}
  #propheties h2 {{
    font-size: 14px;
    color: #ff6b6b;
    margin-bottom: 8px;
  }}
  .prophetie {{
    background: #1e1e36;
    padding: 8px;
    border-radius: 4px;
    margin-bottom: 6px;
    font-size: 11px;
    cursor: pointer;
    border-left: 3px solid #ff3333;
    transition: background 0.2s;
  }}
  .prophetie:hover {{ background: #2a2a4a; }}
  .prophetie .score {{ color: #ffd700; font-weight: bold; }}

  /* Main graph area */
  #main {{ flex: 1; position: relative; overflow: hidden; }}
  #graph {{ width: 100%; height: 100%; }}

  /* Tooltip */
  #tooltip {{
    position: absolute;
    background: rgba(22, 22, 42, 0.95);
    border: 1px solid #4ec9b0;
    padding: 10px;
    border-radius: 6px;
    font-size: 12px;
    pointer-events: none;
    max-width: 300px;
    display: none;
    z-index: 100;
  }}
  #tooltip .nom {{ color: #4ec9b0; font-weight: bold; font-size: 14px; }}
  #tooltip .coeur {{ font-size: 11px; }}
  #tooltip .coeur.noir {{ color: #ff3333; }}
  #tooltip .coeur.blanc {{ color: #ffffff; }}
  #tooltip .coeur.gris {{ color: #aaaaaa; }}

  /* Modal détails */
  #modal {{
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.7);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 200;
  }}
  #modal.active {{ display: flex; }}
  #modal-content {{
    background: #16162a;
    border: 1px solid #4ec9b0;
    border-radius: 8px;
    padding: 24px;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
  }}
  #modal-content h2 {{ color: #4ec9b0; margin-bottom: 12px; }}
  #modal-content .field {{ margin-bottom: 8px; }}
  #modal-content .field .label {{ color: #888; font-size: 11px; }}
  #modal-content .field .value {{ color: #e0e0e0; }}
  #modal-content .runes {{
    font-family: monospace;
    color: #ffd700;
    word-break: break-all;
  }}
  #modal-close {{
    background: #4ec9b0;
    color: #0f0f1b;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 16px;
  }}

  /* Legend */
  #legend {{
    position: absolute;
    bottom: 16px;
    right: 16px;
    background: rgba(22, 22, 42, 0.9);
    padding: 10px;
    border-radius: 6px;
    font-size: 12px;
  }}
  .legend-item {{ display: flex; align-items: center; margin-bottom: 4px; }}
  .legend-color {{
    width: 14px; height: 14px;
    border-radius: 50%;
    margin-right: 8px;
  }}
</style>
</head>
<body>
<div id="app">
  <div id="sidebar">
    <h1> Explorateur Héligresque</h1>

    <div class="stat-box">
      <div class="label">Entités totales</div>
      <div class="value" id="stat-total">{stats['total_entites']}</div>
    </div>
    <div class="stat-box">
      <div class="label">Clusters validés</div>
      <div class="value" id="stat-clusters">{stats['clusters_valides']}</div>
    </div>
    <div class="stat-box">
      <div class="label">Nœuds affichés</div>
      <div class="value" id="stat-nodes">{stats['noeuds_affiches']}</div>
    </div>
    <div class="stat-box">
      <div class="label">Score moyen / max</div>
      <div class="value">{stats['score_moyen']:.2f} / {stats['score_max']:.2f}</div>
    </div>

    <input type="text" id="search" placeholder="🔍 Rechercher une entité...">

    <div class="filter-group">
      <label>Filtrer par Cœur</label>
      <button class="filter-btn noir active" data-coeur="noir">⚫ Noir</button>
      <button class="filter-btn gris active" data-coeur="gris">⚪ Gris</button>
      <button class="filter-btn blanc active" data-coeur="blanc">⚪ Blanc</button>
    </div>

    <div class="filter-group">
      <label>Score minimum</label>
      <input type="range" id="score-filter" min="0" max="1" step="0.05" value="0" style="width:100%">
      <div id="score-value" style="font-size:12px;color:#ffd700">0.00</div>
    </div>

    <div id="propheties">
      <h2>📜 Prophéties ({len(propheties)})</h2>
      <div id="propheties-list"></div>
    </div>
  </div>

  <div id="main">
    <svg id="graph"></svg>
    <div id="tooltip"></div>
    <div id="legend">
      <div class="legend-item"><div class="legend-color" style="background:#ff3333"></div>Cœur Noir</div>
      <div class="legend-item"><div class="legend-color" style="background:#aaaaaa"></div>Cœur Gris</div>
      <div class="legend-item"><div class="legend-color" style="background:#ffffff"></div>Cœur Blanc</div>
      <div class="legend-item"><div class="legend-color" style="background:#00ffff"></div>Lien de cycle</div>
    </div>
  </div>
</div>

<div id="modal">
  <div id="modal-content">
    <h2 id="modal-title"></h2>
    <div id="modal-body"></div>
    <button id="modal-close">Fermer</button>
  </div>
</div>

<script>
const NODES = {nodes_json};
const LINKS = {links_json};
const PROPHETIES = {propheties_json};
const STATS = {stats_json};

// État des filtres
const state = {{
  coeurs: new Set(['noir', 'gris', 'blanc']),
  scoreMin: 0,
  search: ''
}};

// Couleurs par cœur
const COULEURS = {{
  'noir': '#ff3333',
  'gris': '#aaaaaa',
  'blanc': '#ffffff'
}};

// Initialisation D3
const svg = d3.select('#graph');
const width = document.getElementById('main').clientWidth;
const height = document.getElementById('main').clientHeight;
svg.attr('width', width).attr('height', height);

const g = svg.append('g');

// Zoom
const zoom = d3.zoom()
  .scaleExtent([0.1, 4])
  .on('zoom', (event) => g.attr('transform', event.transform));
svg.call(zoom);

// Simulation
const simulation = d3.forceSimulation()
  .force('link', d3.forceLink().id(d => d.index).distance(120))
  .force('charge', d3.forceManyBody().strength(-400))
  .force('center', d3.forceCenter(width / 2, height / 2))
  .force('collision', d3.forceCollide().radius(d => 20 + d.risque * 5));

let linkElements, nodeElements, labelElements;

function render() {{
  // Filtrage
  const filteredNodes = NODES.filter(n =>
    state.coeurs.has(n.coeur) &&
    n.score_cluster >= state.scoreMin &&
    (state.search === '' || n.nom.toLowerCase().includes(state.search.toLowerCase()))
  );
  const nodeIndices = new Set(filteredNodes.map(n => n.index));
  const filteredLinks = LINKS.filter(l => nodeIndices.has(l.source) && nodeIndices.has(l.target));

  // Liens
  linkElements = g.selectAll('.link').data(filteredLinks, d => d.source + '-' + d.target);
  linkElements.exit().remove();
  const linkEnter = linkElements.enter().append('line')
    .attr('class', 'link')
    .attr('stroke', '#00ffff')
    .attr('stroke-opacity', 0.6)
    .attr('stroke-width', d => 1 + d.score * 3);
  linkElements = linkEnter.merge(linkElements);

  // Nœuds
  nodeElements = g.selectAll('.node').data(filteredNodes, d => d.index);
  nodeElements.exit().remove();
  const nodeEnter = nodeElements.enter().append('circle')
    .attr('class', 'node')
    .attr('r', d => 15 + d.risque * 4)
    .attr('fill', d => COULEURS[d.coeur] || '#aaaaaa')
    .attr('stroke', '#0f0f1b')
    .attr('stroke-width', 2)
    .style('cursor', 'pointer')
    .call(d3.drag()
      .on('start', dragStart)
      .on('drag', dragging)
      .on('end', dragEnd))
    .on('mouseover', showTooltip)
    .on('mouseout', hideTooltip)
    .on('click', showDetails);
  nodeElements = nodeEnter.merge(nodeElements);

  // Labels
  labelElements = g.selectAll('.label').data(filteredNodes, d => d.index);
  labelElements.exit().remove();
  const labelEnter = labelElements.enter().append('text')
    .attr('class', 'label')
    .attr('fill', '#e0e0e0')
    .attr('font-size', '10px')
    .attr('text-anchor', 'middle')
    .attr('dy', d => 25 + d.risque * 4)
    .text(d => d.nom.length > 30 ? d.nom.substring(0, 30) + '...' : d.nom)
    .style('pointer-events', 'none');
  labelElements = labelEnter.merge(labelElements);

  simulation.nodes(filteredNodes);
  simulation.force('link').links(filteredLinks);
  simulation.alpha(0.5).restart();

  simulation.on('tick', () => {{
    linkElements
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y);
    nodeElements
      .attr('cx', d => d.x)
      .attr('cy', d => d.y);
    labelElements
      .attr('x', d => d.x)
      .attr('y', d => d.y);
  }});

  document.getElementById('stat-nodes').textContent = filteredNodes.length;
}}

function dragStart(event, d) {{
  if (!event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x; d.fy = d.y;
}}
function dragging(event, d) {{ d.fx = event.x; d.fy = event.y; }}
function dragEnd(event, d) {{
  if (!event.active) simulation.alphaTarget(0);
  d.fx = null; d.fy = null;
}}

function showTooltip(event, d) {{
  const tooltip = document.getElementById('tooltip');
  tooltip.innerHTML = `
    <div class="nom">${{d.nom}}</div>
    <div class="coeur ${{d.coeur}}">Cœur : ${{d.coeur.toUpperCase()}}</div>
    <div>Date : ${{d.date_debut}}</div>
    <div>Delta : ${{d.delta_pendant.toFixed(3)}}</div>
    <div>Risque : ${{d.risque}}</div>
    <div>Score cluster : ${{d.score_cluster.toFixed(3)}}</div>
  `;
  tooltip.style.display = 'block';
  tooltip.style.left = (event.pageX + 10) + 'px';
  tooltip.style.top = (event.pageY + 10) + 'px';
}}

function hideTooltip() {{
  document.getElementById('tooltip').style.display = 'none';
}}

function showDetails(event, d) {{
  event.stopPropagation();
  const modal = document.getElementById('modal');
  document.getElementById('modal-title').textContent = d.nom;
  document.getElementById('modal-body').innerHTML = `
    <div class="field"><div class="label">ID</div><div class="value">${{d.id}}</div></div>
    <div class="field"><div class="label">Cœur</div><div class="value" style="color:${{COULEURS[d.coeur]}}">${{d.coeur.toUpperCase()}}</div></div>
    <div class="field"><div class="label">Classe</div><div class="value">${{d.classe}}</div></div>
    <div class="field"><div class="label">Date</div><div class="value">${{d.date_debut}}</div></div>
    <div class="field"><div class="label">Delta pendant</div><div class="value">${{d.delta_pendant.toFixed(3)}}</div></div>
    <div class="field"><div class="label">Risque</div><div class="value">${{d.risque}}</div></div>
    <div class="field"><div class="label">Score de cluster</div><div class="value" style="color:#ffd700">${{d.score_cluster.toFixed(3)}}</div></div>
    <div class="field"><div class="label">Description</div><div class="value">${{d.description || '—'}}</div></div>
    <div class="field"><div class="label">Runes</div><div class="value runes">${{d.runes || '—'}}</div></div>
    <div class="field"><div class="label">Paléo-mèmes</div><div class="value">${{(d.paleo_memes || []).join(', ') || '—'}}</div></div>
  `;
  modal.classList.add('active');
}}

document.getElementById('modal-close').onclick = () => document.getElementById('modal').classList.remove('active');
document.getElementById('modal').onclick = (e) => {{ if (e.target.id === 'modal') e.currentTarget.classList.remove('active'); }};

// Filtres
document.querySelectorAll('.filter-btn').forEach(btn => {{
  btn.onclick = () => {{
    btn.classList.toggle('active');
    const coeur = btn.dataset.coeur;
    if (btn.classList.contains('active')) state.coeurs.add(coeur);
    else state.coeurs.delete(coeur);
    render();
  }};
}});

document.getElementById('score-filter').oninput = (e) => {{
  state.scoreMin = parseFloat(e.target.value);
  document.getElementById('score-value').textContent = state.scoreMin.toFixed(2);
  render();
}};

document.getElementById('search').oninput = (e) => {{
  state.search = e.target.value;
  render();
}};

// Prophéties dans la sidebar
const propList = document.getElementById('propheties-list');
PROPHETIES.forEach((p, i) => {{
  const div = document.createElement('div');
  div.className = 'prophetie';
  const scoreMatch = p.match(/Score: ([\\d.]+)/);
  const score = scoreMatch ? scoreMatch[1] : '?';
  div.innerHTML = `<span class="score">[${{score}}]</span> ${{p.substring(0, 120)}}...`;
  div.onclick = () => {{
    // Zoom sur le premier nœud du cluster
    const nodesInProp = NODES.filter(n => p.includes(n.nom));
    if (nodesInProp.length > 0) {{
      const target = nodesInProp[0];
      svg.transition().duration(750).call(
        zoom.transform,
        d3.zoomIdentity.translate(width/2, height/2).scale(1.5).translate(-target.x, -target.y)
      );
    }}
  }};
  propList.appendChild(div);
}});

// Premier rendu
NODES.forEach((n, i) => n.index = i);
render();

// Resize
window.addEventListener('resize', () => {{
  const w = document.getElementById('main').clientWidth;
  const h = document.getElementById('main').clientHeight;
  svg.attr('width', w).attr('height', h);
  simulation.force('center', d3.forceCenter(w / 2, h / 2));
  simulation.alpha(0.3).restart();
}});
</script>
</body>
</html>
"""

    Path(output_path).write_text(html_content, encoding="utf-8")
    print(f"🌐 Explorateur HTML généré : {output_path}")


def main():
    print("🌀 Éveil du Filtre de l'Héligre... Analyse des spirales pures en cours.")

    entites, liens = charger_donnees()
    if not entites:
        print("❌ La base leviathan.db est vide ou introuvable.")
        return

    G = reconstruire_graphe(entites, liens)
    clusters, propheties = appliquer_filtre_heligre(G, entites)

    print(f"\n✨ FILTRAGE TERMINÉ : {len(clusters)} spirales pures isolées.")

    if propheties:
        print("\n" + "=" * 80)
        print("📜 PROPHÉTIES DES CLUSTERS VALIDÉS (Codex MTT-2075)")
        print("=" * 80)
        for p in propheties:
            print(p + "\n" + "-" * 80)
        exporter_propheties(propheties, OUTPUT_PROPHETIES)

    if clusters:
        exporter_graphml(clusters, entites, OUTPUT_GRAPHML)
        generer_html_autonome(clusters, entites, propheties, OUTPUT_HTML)
    else:
        print("⚠️ Aucun cluster n'a atteint le seuil. La Trame est stable.")


if __name__ == "__main__":
    main()