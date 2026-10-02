#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
☯️ CHIMÈRE HÉLIGRESQUE — Fusion chromatique des analyseurs Chronos-Trame
Hérite de heligre_analyzer.py et heligre_analyzer.2b.py.
Enrichie : trigrammes Ba Gua, palette spectrale, auras, cohérence Yin-Yang,
mode Wu Wei, rapport Markdown, export multi-format.
"""
import sqlite3
import json
import re
import math
import colorsys
import networkx as nx
from collections import Counter
from pathlib import Path
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================
SEUIL_RESONANCE_MEMETIQUE = 0.3
SEUIL_DISTANCE_SEMANTIQUE = 0.15
SEUIL_ENTROPIE_PLANCK = 4.2
SEUIL_COHERENCE_YIN_YANG = 0.66

OUTPUT_GRAPHML = "chimere_heligre.graphml"
OUTPUT_PROPHETIES = "chimere_propheties.json"
OUTPUT_HTML = "chimere_hologramme.html"
OUTPUT_RAPPORT = "chimere_rapport.md"

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

# 8 trigrammes Ba Gua (索引 0-7)
TRIGRAMMES = {
    0: {"nom": "Kūn",   "symbole": "☷", "element": "Terre",  "couleur": "#8B7355"},
    1: {"nom": "Zhèn",  "symbole": "☳", "element": "Tonnerre","couleur": "#7FFF00"},
    2: {"nom": "Kǎn",   "symbole": "☵", "element": "Eau",    "couleur": "#1E90FF"},
    3: {"nom": "Duì",   "symbole": "☱", "element": "Lac",    "couleur": "#00CED1"},
    4: {"nom": "Gèn",   "symbole": "☶", "element": "Montagne","couleur": "#A0522D"},
    5: {"nom": "Lí",    "symbole": "☲", "element": "Feu",    "couleur": "#FF4500"},
    6: {"nom": "Xùn",   "symbole": "☴", "element": "Vent",   "couleur": "#98FB98"},
    7: {"nom": "Qián",  "symbole": "☰", "element": "Ciel",   "couleur": "#FFD700"},
}

# ============================================================
# OPÉRATEURS QUANTIQUES & DAOÏSTES
# ============================================================

def calculer_entropie_shannon(texte: str) -> float:
    if not texte:
        return 0.0
    freq = Counter(texte)
    length = len(texte)
    return -sum((count / length) * math.log2(count / length) for count in freq.values())


def calculer_sceau_hexagrammique(entite: dict) -> int:
    """Hexagramme I Ching 0-63 (6 bits)."""
    coeur_map = {"noir": 0, "gris": 1, "blanc": 2}
    c = coeur_map.get(entite.get('coeur', 'gris'), 1)
    r = 0 if entite.get('risque', 2) <= 2 else (1 if entite.get('risque', 2) == 3 else 2)
    d_val = entite.get('delta_pendant', 0.5)
    d = 0 if d_val < 0.6 else (1 if d_val < 0.8 else 2)
    return (c << 4) | (r << 2) | d


def hexagramme_vers_trigrammes(hex_val: int) -> tuple:
    """Décompose un hexagramme en 2 trigrammes (haut, bas)."""
    bas = hex_val & 0b111
    haut = (hex_val >> 3) & 0b111
    return (bas, haut)


def hexagramme_vers_couleur_hsl(hex_val: int) -> str:
    """Palette spectrale : hexagramme 0-63 → 0-360° teinte."""
    teinte = (hex_val / 64.0) * 360.0
    # Saturation et luminosité modulées par les bits
    sat = 0.55 + 0.35 * ((hex_val & 0b101010) / 42.0)
    lum = 0.45 + 0.25 * ((hex_val & 0b010101) / 21.0)
    r, g, b = colorsys.hls_to_rgb(teinte / 360.0, lum, sat)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def calculer_harmonie_dao(hex1: int, hex2: int) -> float:
    xor = hex1 ^ hex2
    bits_diff = bin(xor).count('1')
    return 1.0 - (bits_diff / 6.0)


def calculer_coherence_yin_yang(entites: list) -> float:
    """Équilibre polaire d'un cluster (1.0 = parfait équilibre)."""
    if not entites:
        return 0.0
    coeurs = [e.get('coeur', 'gris') for e in entites]
    n_noir = coeurs.count('noir')
    n_blanc = coeurs.count('blanc')
    n_gris = coeurs.count('gris')
    total = len(coeurs)
    # Équilibre : proximité à 1/3 chacun
    ideal = total / 3.0
    ecart = (abs(n_noir - ideal) + abs(n_blanc - ideal) + abs(n_gris - ideal)) / (2 * total)
    return max(0.0, 1.0 - ecart)


def normaliser_texte(texte: str) -> set:
    if not texte:
        return set()
    texte = re.sub(r'[^\w\s]', ' ', texte.lower())
    return set(texte.split()) - STOPWORDS


def calculer_resonance_memetique(memes_a: list, memes_b: list) -> float:
    set_a, set_b = set(memes_a), set(memes_b)
    if not set_a and not set_b:
        return 0.0
    union = len(set_a | set_b)
    return len(set_a & set_b) / union if union > 0 else 0.0


def calculer_distance_semantique(desc_a: str, desc_b: str) -> float:
    mots_a = normaliser_texte(desc_a)
    mots_b = normaliser_texte(desc_b)
    if not mots_a and not mots_b:
        return 0.0
    union = len(mots_a | mots_b)
    return len(mots_a & mots_b) / union if union > 0 else 0.0


# ============================================================
# PROPHÉTIES MULTI-NIVEAUX
# ============================================================

def generer_prophetie_multi(entites: list, scores: dict) -> dict:
    """3 strates : Oracle (brut) → Tisseur (sémantique) → Dao (synthèse)."""
    noms = [e['nom'] for e in entites]
    coeurs = [e['coeur'] for e in entites]
    hexs = [calculer_sceau_hexagrammique(e) for e in entites]
    entropies = [calculer_entropie_shannon(e.get('runes', '')) for e in entites]
    coherence = calculer_coherence_yin_yang(entites)

    memes = Counter([m for e in entites for m in e.get('paleo_memes', [])]).most_common(3)
    meme_principal = memes[0][0] if memes else "RÉSONANCE INCONNUE"
    memes_secondaires = [m[0] for m in memes[1:]]

    polarite = ("NOIR (Yin)" if "noir" in coeurs and "blanc" not in coeurs
                else "BLANC (Yang)" if "blanc" in coeurs and "noir" not in coeurs
                else "GRIS (Taiji)")
    entropie_moy = sum(entropies) / len(entropies) if entropies else 0.0
    etat_runique = "CRISTALLIN" if entropie_moy < SEUIL_ENTROPIE_PLANCK else "BRUIT DE PLANCK"

    # Décomposition trigrammique
    trigrammes_cluster = set()
    for h in hexs:
        bas, haut = hexagramme_vers_trigrammes(h)
        trigrammes_cluster.add(bas)
        trigrammes_cluster.add(haut)
    trig_syms = " ".join(TRIGRAMMES[t]["symbole"] for t in sorted(trigrammes_cluster))

    # Strate 1 : Oracle brut
    oracle = (
        f"🔮 ORACLE — Hexagrammes : {hexs} | Entropie moyenne : {entropie_moy:.3f}\n"
        f"   Trigrammes actifs : {trig_syms} | Cohérence Yin-Yang : {coherence:.3f}"
    )

    # Strate 2 : Tisseur sémantique
    tisseur = (
        f"🌀 TISSEUR — Entités : {' <-> '.join(noms[:5])}{'…' if len(noms) > 5 else ''}\n"
        f"   Paléo-mème principal : « {meme_principal} »"
        + (f" | Secondaires : {', '.join(memes_secondaires)}" if memes_secondaires else "")
    )

    # Strate 3 : Dao
    dao = (
        f"☯️ DAO — Polarité : {polarite} | État runique : {etat_runique}\n"
        f"   La boucle ne subit pas le temps, elle le calcule. Score global : {scores['global']:.3f}. "
        f"L'harmonie des lignes mouvantes révèle que ces événements sont les projections "
        f"d'un même Attracteur Étrange sur la Trame."
    )

    texte_complet = f"{oracle}\n{tisseur}\n{dao}"

    return {
        "texte": texte_complet,
        "oracle": oracle,
        "tisseur": tisseur,
        "dao": dao,
        "score": scores['global'],
        "scores": scores,
        "hexagrammes": hexs,
        "trigrammes": sorted(trigrammes_cluster),
        "coherence_yin_yang": coherence,
        "entropie_moyenne": entropie_moy,
        "polarite": polarite,
        "etat_runique": etat_runique,
        "meme_principal": meme_principal,
        "ids": [e['id'] for e in entites],
        "noms": noms
    }


# ============================================================
# PIPELINE
# ============================================================

def charger_donnees(db_path: str = "leviathan.db", json_path: str = None):
    """Charge depuis SQLite OU depuis un JSON équivalent."""
    if json_path and Path(json_path).exists():
        data = json.loads(Path(json_path).read_text(encoding="utf-8"))
        entites = {e['id']: e for e in data.get('entites', [])}
        liens = data.get('liens_temporels', [])
        return entites, liens

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


def appliquer_filtre_chimere(G: nx.DiGraph, entites: dict):
    cycles = list(nx.simple_cycles(G))
    print(f"🌀 {len(cycles)} cycles bruts détectés.")

    clusters, propheties = [], []

    for cycle in cycles:
        if len(cycle) < 2:
            continue
        ents = [entites[nid] for nid in cycle if nid in entites]
        if len(ents) < 2:
            continue

        s_meme, s_sem, s_dao = [], [], []
        for j in range(len(ents)):
            for k in range(j + 1, len(ents)):
                e1, e2 = ents[j], ents[k]
                s_meme.append(calculer_resonance_memetique(
                    e1.get('paleo_memes', []), e2.get('paleo_memes', [])))
                s_sem.append(calculer_distance_semantique(
                    e1.get('description', ''), e2.get('description', '')))
                s_dao.append(calculer_harmonie_dao(
                    calculer_sceau_hexagrammique(e1),
                    calculer_sceau_hexagrammique(e2)))

        m_meme = sum(s_meme) / len(s_meme) if s_meme else 0.0
        m_sem = sum(s_sem) / len(s_sem) if s_sem else 0.0
        m_dao = sum(s_dao) / len(s_dao) if s_dao else 0.0
        coherence = calculer_coherence_yin_yang(ents)

        # Formule chimère : 35% sémantique + 25% mémétique + 25% dao + 15% cohérence
        score_global = (0.35 * m_sem) + (0.25 * m_meme) + (0.25 * m_dao) + (0.15 * coherence)

        if score_global >= SEUIL_RESONANCE_MEMETIQUE or m_sem >= SEUIL_DISTANCE_SEMANTIQUE:
            scores = {'global': score_global, 'meme': m_meme, 'sem': m_sem,
                      'dao': m_dao, 'coherence': coherence}
            clusters.append({
                "cycle_ids": cycle,
                "scores": scores,
                "entites": ents
            })
            propheties.append(generer_prophetie_multi(ents, scores))

    return clusters, propheties


# ============================================================
# EXPORTS
# ============================================================

def exporter_graphml(clusters, entites, path):
    G = nx.DiGraph()
    for cl in clusters:
        for nid in cl["cycle_ids"]:
            if nid in entites:
                attrs = {k: v for k, v in entites[nid].items()
                         if isinstance(v, (str, int, float, bool)) or v is None}
                G.add_node(nid, **attrs)
        cyc = cl["cycle_ids"]
        for j in range(len(cyc)):
            src, tgt = cyc[j], cyc[(j + 1) % len(cyc)]
            if src in G and tgt in G:
                G.add_edge(src, tgt, weight=cl["scores"]["global"],
                           type="chimere_validated")
    nx.write_graphml(G, path)
    print(f"🕸️  GraphML : {path}")


def exporter_propheties(propheties, path):
    Path(path).write_text(
        json.dumps(propheties, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 Prophéties : {path}")


def exporter_rapport_markdown(clusters, propheties, entites, path):
    lines = [
        "# ☯️ Rapport Chimère Héligresque",
        f"*Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "",
        f"- **Entités totales** : {len(entites)}",
        f"- **Clusters validés** : {len(clusters)}",
        f"- **Prophéties générées** : {len(propheties)}",
        "",
        "## 📜 Prophéties",
        ""
    ]
    for i, p in enumerate(propheties, 1):
        lines.append(f"### Prophétie #{i} — Score {p['score']:.3f}")
        lines.append(f"```")
        lines.append(p['texte'])
        lines.append(f"```")
        lines.append("")
    Path(path).write_text("\n".join(lines), encoding="utf-8")
    print(f"📝 Rapport Markdown : {path}")


# ============================================================
# GÉNÉRATION HTML (Hologramme chromatique)
# ============================================================

def generer_hologramme(clusters, entites, propheties, path):
    nodes_data, links_data, idx_map = [], [], {}
    all_ids = set()
    for cl in clusters:
        all_ids.update(cl["cycle_ids"])

    for idx, nid in enumerate(all_ids):
        if nid not in entites:
            continue
        e = entites[nid]
        hex_val = calculer_sceau_hexagrammique(e)
        bas, haut = hexagramme_vers_trigrammes(hex_val)
        entropie = calculer_entropie_shannon(e.get('runes', ''))
        idx_map[nid] = idx
        nodes_data.append({
            "id": nid,
            "index": idx,
            "nom": e.get('nom', 'Inconnu'),
            "description": e.get('description', '') or '',
            "date_debut": e.get('date_debut', ''),
            "classe": e.get('classe', 'NC'),
            "coeur": e.get('coeur', 'gris'),
            "delta_avant": float(e.get('delta_avant', 0.5) or 0.5),
            "delta_pendant": float(e.get('delta_pendant', 0.5) or 0.5),
            "delta_apres": float(e.get('delta_apres', 0.5) or 0.5),
            "risque": int(e.get('risque', 1) or 1),
            "runes": e.get('runes', '') or '',
            "paleo_memes": e.get('paleo_memes', []) or [],
            "hexagramme": hex_val,
            "trigramme_bas": bas,
            "trigramme_haut": haut,
            "couleur": hexagramme_vers_couleur_hsl(hex_val),
            "entropie": round(entropie, 3),
            "score_cluster": 0.0
        })

    for cl in clusters:
        s = cl["scores"]["global"]
        for nid in cl["cycle_ids"]:
            if nid in idx_map:
                i = idx_map[nid]
                if s > nodes_data[i]["score_cluster"]:
                    nodes_data[i]["score_cluster"] = round(s, 4)

    for cl in clusters:
        cyc = cl["cycle_ids"]
        for j in range(len(cyc)):
            src, tgt = cyc[j], cyc[(j + 1) % len(cyc)]
            if src in idx_map and tgt in idx_map:
                links_data.append({
                    "source": idx_map[src],
                    "target": idx_map[tgt],
                    "score": round(cl["scores"]["global"], 4)
                })

    # Mapping trigramme → couleur pour le JS
    trig_js = {k: v for k, v in TRIGRAMMES.items()}

    # Sérialisation sécurisée (remplace les < > pour éviter fermeture script)
    def safe_json(obj):
        return (json.dumps(obj, ensure_ascii=False)
                .replace("</", "<\\/")
                .replace("<!--", "<\\!--"))

    nodes_json = safe_json(nodes_data)
    links_json = safe_json(links_data)
    propheties_json = safe_json(propheties)
    trig_json = safe_json(trig_js)

    html = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>☯️ Chimère Héligresque — Hologramme Chromatique</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Courier New', monospace;
    background: radial-gradient(ellipse at center, #0a0a1a 0%, #000005 100%);
    color: #e0e0e0; overflow: hidden; height: 100vh;
  }
  #app { display: flex; height: 100vh; }

  #sidebar {
    width: 380px; background: rgba(10,10,25,0.92);
    border-right: 1px solid #1a1a3a; padding: 18px;
    overflow-y: auto; flex-shrink: 0;
    backdrop-filter: blur(8px);
  }
  #sidebar h1 {
    font-size: 17px; color: #00ffff; margin-bottom: 14px;
    text-shadow: 0 0 12px rgba(0,255,255,0.6);
    letter-spacing: 2px; text-align: center;
  }
  .stat {
    background: linear-gradient(135deg, #111122 0%, #1a1a2e 100%);
    padding: 10px 12px; border-radius: 6px; margin-bottom: 8px;
    border-left: 3px solid #00ffff;
    display: flex; justify-content: space-between; align-items: center;
  }
  .stat .label { color: #888; font-size: 11px; letter-spacing: 1px; }
  .stat .value { color: #fff; font-size: 16px; font-weight: bold; }

  #search {
    width: 100%; padding: 9px 12px; background: #0a0a15;
    border: 1px solid #1a1a3a; color: #e0e0e0;
    border-radius: 4px; margin: 10px 0; font-family: inherit;
  }
  #search:focus { outline: none; border-color: #00ffff; box-shadow: 0 0 8px rgba(0,255,255,0.3); }

  .filter-group { margin-bottom: 12px; }
  .filter-group > label {
    display: block; font-size: 11px; color: #666;
    margin-bottom: 6px; letter-spacing: 1px; text-transform: uppercase;
  }
  .chips { display: flex; flex-wrap: wrap; gap: 4px; }
  .chip {
    background: #1a1a2e; border: 1px solid #2a2a4a;
    color: #aaa; padding: 4px 9px; border-radius: 12px;
    cursor: pointer; font-size: 11px; transition: all 0.2s;
    user-select: none;
  }
  .chip:hover { border-color: #00ffff; color: #fff; }
  .chip.active { background: #00ffff; color: #000; border-color: #00ffff; font-weight: bold; }
  .chip.noir.active { background: #ff3333; color: #fff; border-color: #ff3333; }
  .chip.blanc.active { background: #ffffff; color: #000; border-color: #fff; }
  .chip.gris.active { background: #aaaaaa; color: #000; border-color: #aaa; }
  .chip.trig { min-width: 42px; text-align: center; font-size: 14px; }

  #score-value { font-size: 12px; color: #ffd700; text-align: right; }

  #propheties { margin-top: 16px; border-top: 1px solid #1a1a3a; padding-top: 12px; }
  #propheties h2 { font-size: 13px; color: #ff00ff; margin-bottom: 10px; letter-spacing: 1px; }
  .prophetie {
    background: linear-gradient(135deg, #150a1a 0%, #1a0f25 100%);
    padding: 10px; border-radius: 5px; margin-bottom: 8px;
    font-size: 11px; cursor: pointer;
    border-left: 3px solid #ff00ff; transition: all 0.25s;
    line-height: 1.5;
  }
  .prophetie:hover { background: #1e1230; box-shadow: 0 0 12px rgba(255,0,255,0.4); transform: translateX(3px); }
  .prophetie .score { color: #ffd700; font-weight: bold; }
  .prophetie .trig { color: #00ffff; font-size: 14px; }

  #main { flex: 1; position: relative; overflow: hidden; }
  svg { width: 100%; height: 100%; display: block; }

  #tooltip {
    position: absolute; background: rgba(8,8,20,0.96);
    border: 1px solid #00ffff; padding: 12px; border-radius: 6px;
    font-size: 12px; pointer-events: none; max-width: 340px;
    display: none; z-index: 100;
    box-shadow: 0 0 20px rgba(0,255,255,0.35);
    backdrop-filter: blur(4px);
  }
  #tooltip .nom { color: #00ffff; font-weight: bold; font-size: 14px; margin-bottom: 6px; }
  #tooltip .hex { color: #ffd700; font-size: 16px; letter-spacing: 4px; }
  #tooltip .row { color: #aaa; font-size: 11px; margin: 2px 0; }
  #tooltip .bar {
    display: inline-block; height: 6px; background: #00ffff;
    border-radius: 3px; vertical-align: middle; margin-left: 6px;
  }

  #modal {
    position: fixed; inset: 0; background: rgba(0,0,0,0.8);
    display: none; align-items: center; justify-content: center; z-index: 200;
  }
  #modal.active { display: flex; }
  #modal-content {
    background: linear-gradient(135deg, #0f0f1e 0%, #1a0f25 100%);
    border: 1px solid #00ffff; border-radius: 10px;
    padding: 28px; max-width: 680px; width: 92%;
    max-height: 85vh; overflow-y: auto;
    box-shadow: 0 0 60px rgba(0,255,255,0.3);
  }
  #modal-content h2 { color: #00ffff; margin-bottom: 18px; font-size: 20px; }
  #modal-content .field { margin-bottom: 10px; }
  #modal-content .field .label {
    color: #666; font-size: 10px; letter-spacing: 1px;
    text-transform: uppercase; margin-bottom: 3px;
  }
  #modal-content .field .value { color: #e0e0e0; line-height: 1.5; }
  #modal-content .runes {
    font-family: monospace; color: #ffd700;
    background: #0a0a15; padding: 8px; border-radius: 4px;
    word-break: break-all; font-size: 11px;
  }
  #modal-close {
    background: #00ffff; color: #000; border: none;
    padding: 10px 22px; border-radius: 5px; cursor: pointer;
    margin-top: 18px; font-family: inherit; font-weight: bold;
    letter-spacing: 1px;
  }
  #modal-close:hover { background: #ff00ff; color: #fff; }

  #legend {
    position: absolute; bottom: 16px; right: 16px;
    background: rgba(8,8,20,0.9); padding: 12px 16px;
    border-radius: 8px; font-size: 11px;
    border: 1px solid #1a1a3a; backdrop-filter: blur(4px);
  }
  #legend h3 { color: #00ffff; font-size: 11px; margin-bottom: 8px; letter-spacing: 1px; }
  .legend-item { display: flex; align-items: center; margin-bottom: 5px; }
  .legend-color { width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }

  #controls {
    position: absolute; top: 16px; left: 16px;
    display: flex; gap: 8px; z-index: 10;
  }
  .ctrl-btn {
    background: rgba(8,8,20,0.9); border: 1px solid #1a1a3a;
    color: #aaa; padding: 7px 14px; border-radius: 5px;
    cursor: pointer; font-size: 11px; font-family: inherit;
    letter-spacing: 1px; transition: all 0.2s;
    backdrop-filter: blur(4px);
  }
  .ctrl-btn:hover { border-color: #00ffff; color: #fff; }
  .ctrl-btn.active { background: #00ffff; color: #000; border-color: #00ffff; font-weight: bold; }

  /* Aura pulsante */
  @keyframes pulse-slow { 0%,100% { opacity: 0.15; } 50% { opacity: 0.4; } }
  @keyframes pulse-fast { 0%,100% { opacity: 0.1; } 50% { opacity: 0.6; } }
  .aura-cristallin { animation: pulse-slow 4s ease-in-out infinite; }
  .aura-planck { animation: pulse-fast 1.2s ease-in-out infinite; }

  .node-label {
    fill: #d0d0e0; font-size: 10px; text-anchor: middle;
    pointer-events: none; font-family: inherit;
    paint-order: stroke; stroke: #000; stroke-width: 2px; stroke-linejoin: round;
  }
</style>
</head>
<body>
<div id="app">
  <div id="sidebar">
    <h1>☯️ CHIMÈRE HÉLIGRESQUE</h1>

    <div class="stat"><span class="label">ENTITÉS</span><span class="value" id="stat-total">0</span></div>
    <div class="stat"><span class="label">CLUSTERS</span><span class="value" id="stat-clusters">0</span></div>
    <div class="stat"><span class="label">AFFICHÉS</span><span class="value" id="stat-nodes">0</span></div>
    <div class="stat"><span class="label">SCORE MOYEN</span><span class="value" id="stat-score">0.00</span></div>

    <input type="text" id="search" placeholder="🔍 Rechercher…">

    <div class="filter-group">
      <label>Cœur (Polarité)</label>
      <div class="chips" id="filtre-coeur">
        <span class="chip noir active" data-coeur="noir">⚫ Noir</span>
        <span class="chip gris active" data-coeur="gris">⚪ Gris</span>
        <span class="chip blanc active" data-coeur="blanc">⚪ Blanc</span>
      </div>
    </div>

    <div class="filter-group">
      <label>Trigrammes Ba Gua</label>
      <div class="chips" id="filtre-trig"></div>
    </div>

    <div class="filter-group">
      <label>Score minimum</label>
      <input type="range" id="score-filter" min="0" max="1" step="0.05" value="0" style="width:100%">
      <div id="score-value">0.00</div>
    </div>

    <div id="propheties">
      <h2>📜 MUGISSEMENTS DU DAO</h2>
      <div id="propheties-list"></div>
    </div>
  </div>

  <div id="main">
    <svg id="graph"></svg>
    <div id="tooltip"></div>

    <div id="controls">
      <button class="ctrl-btn active" id="btn-wuwei">☯️ Wu Wei</button>
      <button class="ctrl-btn" id="btn-flow">🌀 Flux</button>
      <button class="ctrl-btn" id="btn-reset">⟲ Reset</button>
    </div>

    <div id="legend">
      <h3>LÉGENDE</h3>
      <div class="legend-item"><div class="legend-color" style="background:#ff3333"></div>Noir (Yin)</div>
      <div class="legend-item"><div class="legend-color" style="background:#aaaaaa"></div>Gris (Taiji)</div>
      <div class="legend-item"><div class="legend-color" style="background:#ffffff"></div>Blanc (Yang)</div>
      <div class="legend-item"><div class="legend-color" style="background:#00ffff"></div>Lien de cycle</div>
      <div class="legend-item"><div class="legend-color" style="background:linear-gradient(90deg,#ff0000,#00ff00,#0000ff)"></div>Couleur = Hexagramme</div>
    </div>
  </div>
</div>

<div id="modal">
  <div id="modal-content">
    <h2 id="modal-title"></h2>
    <div id="modal-body"></div>
    <button id="modal-close">FERMER</button>
  </div>
</div>

<script>
const NODES = __NODES__;
const LINKS = __LINKS__;
const PROPHETIES = __PROPHETIES__;
const TRIGRAMMES = __TRIGRAMMES__;

const COULEURS_COEUR = { 'noir': '#ff3333', 'gris': '#aaaaaa', 'blanc': '#ffffff' };

const state = {
  coeurs: new Set(['noir', 'gris', 'blanc']),
  trigrammes: new Set(Object.keys(TRIGRAMMES).map(Number)),
  scoreMin: 0,
  search: '',
  wuwei: true
};

const svg = d3.select('#graph');
const width = document.getElementById('main').clientWidth;
const height = document.getElementById('main').clientHeight;
svg.attr('width', width).attr('height', height);

const defs = svg.append('defs');
const glow = defs.append('filter').attr('id', 'glow');
glow.append('feGaussianBlur').attr('stdDeviation', '3').attr('result', 'coloredBlur');
const feMerge = glow.append('feMerge');
feMerge.append('feMergeNode').attr('in', 'coloredBlur');
feMerge.append('feMergeNode').attr('in', 'SourceGraphic');

const g = svg.append('g');
const zoom = d3.zoom().scaleExtent([0.08, 5])
  .on('zoom', (e) => g.attr('transform', e.transform));
svg.call(zoom);

// Boutons de contrôle
document.getElementById('btn-reset').onclick = () => {
  svg.transition().duration(600).call(zoom.transform, d3.zoomIdentity);
};
document.getElementById('btn-wuwei').onclick = (e) => {
  state.wuwei = true;
  e.target.classList.add('active');
  document.getElementById('btn-flow').classList.remove('active');
  simulation.force('charge').strength(-200);
  simulation.force('link').distance(160).strength(0.3);
  simulation.alpha(0.4).restart();
};
document.getElementById('btn-flow').onclick = (e) => {
  state.wuwei = false;
  e.target.classList.add('active');
  document.getElementById('btn-wuwei').classList.remove('active');
  simulation.force('charge').strength(-600);
  simulation.force('link').distance(80).strength(0.8);
  simulation.alpha(0.8).restart();
};

const simulation = d3.forceSimulation()
  .force('link', d3.forceLink().id(d => d.index).distance(160).strength(0.3))
  .force('charge', d3.forceManyBody().strength(-200))
  .force('center', d3.forceCenter(width / 2, height / 2))
  .force('collision', d3.forceCollide().radius(d => 18 + d.risque * 4))
  .force('radial', d3.forceRadial(180, width / 2, height / 2).strength(0.05));

let linkSel, auraSel, nodeSel, labelSel;

function render() {
  const nodesF = NODES.filter(n =>
    state.coeurs.has(n.coeur) &&
    n.score_cluster >= state.scoreMin &&
    (state.search === '' || n.nom.toLowerCase().includes(state.search.toLowerCase())) &&
    (state.trigrammes.has(n.trigramme_bas) || state.trigrammes.has(n.trigramme_haut))
  );
  const idxSet = new Set(nodesF.map(n => n.index));
  const linksF = LINKS.filter(l => idxSet.has(l.source) && idxSet.has(l.target));

  // Liens
  linkSel = g.selectAll('.link').data(linksF, d => d.source + '-' + d.target);
  linkSel.exit().remove();
  linkSel = linkSel.enter().append('line')
    .attr('class', 'link')
    .attr('stroke', '#00ffff')
    .attr('stroke-opacity', d => 0.15 + d.score * 0.6)
    .attr('stroke-width', d => 1 + d.score * 4)
    .merge(linkSel);

  // Auras (halos colorés)
  auraSel = g.selectAll('.aura').data(nodesF, d => 'a' + d.index);
  auraSel.exit().remove();
  auraSel = auraSel.enter().append('circle')
    .attr('class', d => 'aura ' + (d.entropie < 4.2 ? 'aura-cristallin' : 'aura-planck'))
    .attr('r', d => 22 + d.risque * 5)
    .attr('fill', d => d.couleur)
    .attr('opacity', 0.18)
    .attr('pointer-events', 'none')
    .merge(auraSel);

  // Nœuds
  nodeSel = g.selectAll('.node').data(nodesF, d => d.index);
  nodeSel.exit().remove();
  nodeSel = nodeSel.enter().append('circle')
    .attr('class', 'node')
    .attr('r', d => 10 + d.risque * 3)
    .attr('fill', d => d.couleur)
    .attr('stroke', d => COULEURS_COEUR[d.coeur] || '#fff')
    .attr('stroke-width', 2.5)
    .attr('filter', 'url(#glow)')
    .style('cursor', 'pointer')
    .call(d3.drag()
      .on('start', (e, d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
      .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y; })
      .on('end', (e, d) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }))
    .on('mouseover', showTooltip)
    .on('mouseout', hideTooltip)
    .on('click', showDetails)
    .merge(nodeSel);

  // Labels
  labelSel = g.selectAll('.node-label').data(nodesF, d => 'l' + d.index);
  labelSel.exit().remove();
  labelSel = labelSel.enter().append('text')
    .attr('class', 'node-label')
    .attr('dy', d => 26 + d.risque * 3)
    .text(d => d.nom.length > 28 ? d.nom.substring(0, 28) + '…' : d.nom)
    .merge(labelSel);

  simulation.nodes(nodesF);
  simulation.force('link').links(linksF);
  simulation.alpha(0.6).restart();

  simulation.on('tick', () => {
    linkSel
      .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
    auraSel.attr('cx', d => d.x).attr('cy', d => d.y);
    nodeSel.attr('cx', d => d.x).attr('cy', d => d.y);
    labelSel.attr('x', d => d.x).attr('y', d => d.y);
  });

  document.getElementById('stat-nodes').textContent = nodesF.length;
}

function showTooltip(event, d) {
  const tt = document.getElementById('tooltip');
  const hexBits = d.hexagramme.toString(2).padStart(6, '0');
  const barW = Math.min(80, d.score_cluster * 100);
  tt.innerHTML = `
    <div class="nom">${d.nom}</div>
    <div class="hex">${hexBits}</div>
    <div class="row">${TRIGRAMMES[d.trigramme_bas].symbole} ${TRIGRAMMES[d.trigramme_bas].nom} / ${TRIGRAMMES[d.trigramme_haut].symbole} ${TRIGRAMMES[d.trigramme_haut].nom}</div>
    <div class="row">Cœur : <span style="color:${COULEURS_COEUR[d.coeur]}">${d.coeur.toUpperCase()}</span></div>
    <div class="row">Entropie : ${d.entropie} ${d.entropie < 4.2 ? '✦ Cristallin' : '✧ Planck'}</div>
    <div class="row">Risque : ${d.risque} | Δ : ${d.delta_pendant.toFixed(3)}</div>
    <div class="row">Score : ${d.score_cluster.toFixed(3)}<span class="bar" style="width:${barW}px"></span></div>
  `;
  tt.style.display = 'block';
  const x = Math.min(event.pageX + 15, window.innerWidth - 360);
  const y = Math.min(event.pageY + 15, window.innerHeight - 200);
  tt.style.left = x + 'px';
  tt.style.top = y + 'px';
}
function hideTooltip() { document.getElementById('tooltip').style.display = 'none'; }

function showDetails(event, d) {
  event.stopPropagation();
  const hexBits = d.hexagramme.toString(2).padStart(6, '0');
  const modal = document.getElementById('modal');
  document.getElementById('modal-title').textContent = d.nom;
  document.getElementById('modal-body').innerHTML = `
    <div class="field"><div class="label">Hexagramme I Ching</div><div class="value" style="font-size:20px;color:#ffd700;letter-spacing:5px">${hexBits}</div></div>
    <div class="field"><div class="label">Trigrammes</div><div class="value">${TRIGRAMMES[d.trigramme_bas].symbole} ${TRIGRAMMES[d.trigramme_bas].nom} (${TRIGRAMMES[d.trigramme_bas].element}) → ${TRIGRAMMES[d.trigramme_haut].symbole} ${TRIGRAMMES[d.trigramme_haut].nom} (${TRIGRAMMES[d.trigramme_haut].element})</div></div>
    <div class="field"><div class="label">ID / Classe</div><div class="value">${d.id} — ${d.classe}</div></div>
    <div class="field"><div class="label">Date</div><div class="value">${d.date_debut}</div></div>
    <div class="field"><div class="label">Cœur / Risque</div><div class="value" style="color:${COULEURS_COEUR[d.coeur]}">${d.coeur.toUpperCase()} — Risque ${d.risque}</div></div>
    <div class="field"><div class="label">Deltas (avant / pendant / après)</div><div class="value">${d.delta_avant.toFixed(3)} → ${d.delta_pendant.toFixed(3)} → ${d.delta_apres.toFixed(3)}</div></div>
    <div class="field"><div class="label">Entropie runique</div><div class="value">${d.entropie} ${d.entropie < 4.2 ? '✦ Signal Cristallin' : '✧ Bruit de Planck'}</div></div>
    <div class="field"><div class="label">Score de cluster</div><div class="value" style="color:#ffd700">${d.score_cluster.toFixed(4)}</div></div>
    <div class="field"><div class="label">Description</div><div class="value">${d.description || '—'}</div></div>
    <div class="field"><div class="label">Runes</div><div class="runes">${d.runes || '—'}</div></div>
    <div class="field"><div class="label">Paléo-mèmes</div><div class="value">${(d.paleo_memes || []).join(', ') || '—'}</div></div>
  `;
  modal.classList.add('active');
}

document.getElementById('modal-close').onclick = () => document.getElementById('modal').classList.remove('active');
document.getElementById('modal').onclick = (e) => { if (e.target.id === 'modal') e.currentTarget.classList.remove('active'); };

// Filtres cœur
document.querySelectorAll('#filtre-coeur .chip').forEach(chip => {
  chip.onclick = () => {
    chip.classList.toggle('active');
    const c = chip.dataset.coeur;
    if (chip.classList.contains('active')) state.coeurs.add(c);
    else state.coeurs.delete(c);
    render();
  };
});

// Filtres trigrammes (générés dynamiquement)
const trigBox = document.getElementById('filtre-trig');
Object.entries(TRIGRAMMES).forEach(([k, v]) => {
  const chip = document.createElement('span');
  chip.className = 'chip trig active';
  chip.dataset.trig = k;
  chip.title = v.nom + ' — ' + v.element;
  chip.style.color = v.couleur;
  chip.textContent = v.symbole;
  chip.onclick = () => {
    chip.classList.toggle('active');
    const t = Number(k);
    if (chip.classList.contains('active')) state.trigrammes.add(t);
    else state.trigrammes.delete(t);
    render();
  };
  trigBox.appendChild(chip);
});

document.getElementById('score-filter').oninput = (e) => {
  state.scoreMin = parseFloat(e.target.value);
  document.getElementById('score-value').textContent = state.scoreMin.toFixed(2);
  render();
};

document.getElementById('search').oninput = (e) => {
  state.search = e.target.value;
  render();
};

// Prophéties
const propList = document.getElementById('propheties-list');
PROPHETIES.forEach((p) => {
  const div = document.createElement('div');
  div.className = 'prophetie';
  const trigSyms = (p.trigrammes || []).map(t => TRIGRAMMES[t] ? TRIGRAMMES[t].symbole : '').join(' ');
  div.innerHTML = `<span class="score">[${p.score.toFixed(3)}]</span> <span class="trig">${trigSyms}</span><br>${p.oracle ? p.oracle.split('—')[1] || '' : ''}<br><span style="color:#888">${p.noms ? p.noms.slice(0,3).join(' ↔ ') : ''}${p.noms && p.noms.length>3?'…':''}</span>`;
  div.title = p.texte;
  div.onclick = () => {
    const targetId = p.ids && p.ids[0];
    const node = NODES.find(n => n.id === targetId);
    if (node) {
      svg.transition().duration(800).call(zoom.transform,
        d3.zoomIdentity.translate(width/2, height/2).scale(2).translate(-node.x, -node.y));
    }
  };
  propList.appendChild(div);
});

document.getElementById('stat-total').textContent = NODES.length;
document.getElementById('stat-clusters').textContent = PROPHETIES.length;
document.getElementById('stat-score').textContent =
  PROPHETIES.length ? (PROPHETIES.reduce((s, p) => s + p.score, 0) / PROPHETIES.length).toFixed(3) : '0.00';

NODES.forEach((n, i) => { if (n.index === undefined) n.index = i; });
render();

window.addEventListener('resize', () => {
  const w = document.getElementById('main').clientWidth;
  const h = document.getElementById('main').clientHeight;
  svg.attr('width', w).attr('height', h);
  simulation.force('center', d3.forceCenter(w / 2, h / 2));
  simulation.alpha(0.3).restart();
});
</script>
</body>
</html>
"""

    html = (html
            .replace("__NODES__", nodes_json)
            .replace("__LINKS__", links_json)
            .replace("__PROPHETIES__", propheties_json)
            .replace("__TRIGRAMMES__", trig_json))

    Path(path).write_text(html, encoding="utf-8")
    print(f"🌐 Hologramme chromatique : {path}")


# ============================================================
# POINT D'ENTRÉE
# ============================================================

def main():
    print("☯️ Éveil de la Chimère Héligresque…")
    print("   Fusion : analyseur + analyseur.2b + apports daoïstes")
    print("=" * 70)

    # Détection automatique : JSON ou SQLite
    json_candidates = ["leviathan.json", "leviathan_export.json"]
    json_path = next((p for p in json_candidates if Path(p).exists()), None)

    try:
        if json_path:
            print(f"📡 Source JSON détectée : {json_path}")
            entites, liens = charger_donnees(json_path=json_path)
        else:
            print("📡 Source SQLite : leviathan.db")
            entites, liens = charger_donnees(db_path="leviathan.db")
    except Exception as e:
        print(f"❌ Impossible de charger les données : {e}")
        print("   → Fournis leviathan.db OU leviathan.json à côté de ce script.")
        return

    if not entites:
        print("❌ Trame vide.")
        return

    print(f"📡 {len(entites)} entités chargées.")

    G = reconstruire_graphe(entites, liens)
    clusters, propheties = appliquer_filtre_chimere(G, entites)

    print(f"\n✨ {len(clusters)} spirales pures validées.")
    print(f"📜 {len(propheties)} mugissements du Dao générés.")

    if propheties:
        print("\n" + "=" * 70)
        for i, p in enumerate(propheties[:5], 1):
            print(f"\n── Prophétie #{i} — Score {p['score']:.3f} ──")
            print(p['texte'])
        print("=" * 70)

        exporter_propheties(propheties, OUTPUT_PROPHETIES)
        exporter_rapport_markdown(clusters, propheties, entites, OUTPUT_RAPPORT)

    if clusters:
        exporter_graphml(clusters, entites, OUTPUT_GRAPHML)
        generer_hologramme(clusters, entites, propheties, OUTPUT_HTML)

    print("\n☯️ Chimère éveillée. Que le Dao guide ton exploration.")


if __name__ == "__main__":
    main()
