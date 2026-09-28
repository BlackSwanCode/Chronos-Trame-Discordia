# storage/leviathan_db.py
import sqlite3
import json
import os
from typing import List, Optional
from core.ontology import EntiteOntique

class LeviathanDB:
    def __init__(self, db_path: str = "leviathan.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entites (
                    id TEXT PRIMARY KEY, nom TEXT, description TEXT, date_debut TEXT,
                    classe TEXT, coeur TEXT, delta_pendant REAL, risque INTEGER,
                    runes TEXT, couches TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS liens_temporels (
                    source TEXT, cible TEXT, force REAL, type TEXT
                )
            """)
            conn.commit()

    def charger_corpus_bdo(self, json_path: str):
        if not os.path.exists(json_path):
            return
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with sqlite3.connect(self.db_path) as conn:
            for item in data:
                conn.execute("""
                    INSERT OR IGNORE INTO entites 
                    (id, nom, description, date_debut, classe, coeur, delta_pendant, risque, runes, couches)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.get('id', 'unknown'), item.get('nom', 'Inconnu'), 
                    item.get('description', '')[:100], item.get('date_debut', '1970-01-01'),
                    item.get('taxonomie', {}).get('classe_principale', 'NC'),
                    item.get('coeur_dominant', 'gris'), item.get('delta_estime', {}).get('pendant', 0.5),
                    item.get('risque', 1), "", ""
                ))
            conn.commit()

    def obtenir_toutes_entites(self) -> List[EntiteOntique]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM entites")
            entites = []
            for row in cursor.fetchall():
                entites.append(EntiteOntique(
                    id=row[0], nom=row[1], description=row[2], date_debut=row[3],
                    date_fin=None, classe_principale=row[4], coeur_dominant=row[5],
                    delta_avant=row[6], delta_pendant=row[6], delta_apres=row[6],
                    risque=row[7], fragments_runiques=row[8].split(',') if row[8] else [],
                    couches_osi=[int(x) for x in row[9].split(',')] if row[9] else []
                ))
            return entites
