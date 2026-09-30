import sqlite3
import json
import os
from datetime import datetime
from typing import List
from core.ontology import EntiteOntique

class LeviathanDB:
    def __init__(self, db_path: str = "leviathan.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entites (
                    id TEXT PRIMARY KEY, nom TEXT, description TEXT, date_debut TEXT, date_fin TEXT,
                    classe TEXT, coeur TEXT, delta_avant REAL, delta_pendant REAL, delta_apres REAL, risque INTEGER,
                    runes TEXT, paleo_memes TEXT, couches TEXT
                )
            """)
            # Migration robuste pour les bases existantes
            for sql in [
                "ALTER TABLE entites ADD COLUMN date_fin TEXT",
                "ALTER TABLE entites ADD COLUMN delta_avant REAL",
                "ALTER TABLE entites ADD COLUMN delta_apres REAL",
                "ALTER TABLE entites ADD COLUMN paleo_memes TEXT"
            ]:
                try:
                    conn.execute(sql)
                except sqlite3.OperationalError:
                    pass  # La colonne existe déjà

            conn.execute("""
                CREATE TABLE IF NOT EXISTS liens_temporels (
                    source TEXT, cible TEXT, force REAL, type TEXT,
                    PRIMARY KEY (source, cible, type)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alertes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entite_id TEXT,
                    type TEXT,
                    message TEXT,
                    timestamp TEXT
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
                delta_estime = item.get('delta_estime', {})
                conn.execute("""
                    INSERT OR IGNORE INTO entites
                    (id, nom, description, date_debut, date_fin, classe, coeur, delta_avant, delta_pendant, delta_apres, risque, runes, paleo_memes, couches)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.get('id', 'unknown'), item.get('nom', 'Inconnu'),
                    item.get('description', '')[:200], item.get('date_debut', '1970-01-01'),
                    item.get('date_fin', None),
                    item.get('taxonomie', {}).get('classe_principale', 'NC'),
                    item.get('coeur_dominant', 'gris'), 
                    delta_estime.get('avant', 0.5), delta_estime.get('pendant', 0.5), delta_estime.get('apres', 0.5),
                    item.get('risque', 1), "", "", ""
                ))
            conn.commit()

    def obtenir_toutes_entites(self) -> List[EntiteOntique]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, nom, description, date_debut, date_fin, classe, coeur, delta_avant, delta_pendant, delta_apres, risque, runes, paleo_memes, couches FROM entites")
            entites = []
            for row in cursor.fetchall():
                entites.append(EntiteOntique(
                    id=row[0], nom=row[1], description=row[2], date_debut=row[3], date_fin=row[4],
                    classe_principale=row[5], coeur_dominant=row[6],
                    delta_avant=row[7] if row[7] is not None else 0.5, 
                    delta_pendant=row[8] if row[8] is not None else 0.5, 
                    delta_apres=row[9] if row[9] is not None else 0.5, 
                    risque=row[10],
                    fragments_runiques=row[11].split(',') if row[11] else [],
                    paleo_memes=row[12].split(',') if row[12] else [],
                    couches_osi=[int(x) for x in row[13].split(',')] if row[13] else []
                ))
            return entites

    def sauvegarder_attributs_calcules(self, entite: EntiteOntique):
        with sqlite3.connect(self.db_path) as conn:
            runes_str = ",".join(entite.fragments_runiques)
            memes_str = ",".join(entite.paleo_memes)
            conn.execute("UPDATE entites SET runes = ?, paleo_memes = ? WHERE id = ?", (runes_str, memes_str, entite.id))
            conn.commit()

    def sauvegarder_lien(self, source: str, cible: str, force: float, type_lien: str = "causal"):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO liens_temporels (source, cible, force, type) VALUES (?, ?, ?, ?)", (source, cible, force, type_lien))
            conn.commit()

    def obtenir_liens(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT source, cible, force, type FROM liens_temporels")
            return cursor.fetchall()

    def sauvegarder_entite(self, entite: EntiteOntique):
        """Insère ou met à jour une entité (UPSERT)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO entites
                (id, nom, description, date_debut, date_fin, classe, coeur,
                 delta_avant, delta_pendant, delta_apres, risque, runes, paleo_memes, couches)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    nom=excluded.nom, description=excluded.description,
                    date_debut=excluded.date_debut, date_fin=excluded.date_fin,
                    classe=excluded.classe, coeur=excluded.coeur,
                    delta_avant=excluded.delta_avant, delta_pendant=excluded.delta_pendant,
                    delta_apres=excluded.delta_apres, risque=excluded.risque,
                    runes=excluded.runes, paleo_memes=excluded.paleo_memes, couches=excluded.couches
            """, (
                entite.id, entite.nom, entite.description, entite.date_debut, entite.date_fin,
                entite.classe_principale, entite.coeur_dominant,
                entite.delta_avant, entite.delta_pendant, entite.delta_apres, entite.risque,
                ",".join(entite.fragments_runiques), ",".join(entite.paleo_memes),
                ",".join(map(str, entite.couches_osi))
            ))
            conn.commit()

    def sauvegarder_alerte(self, entite_id: str, type_alerte: str, message: str):
        """Insère une alerte (la table est créée à l'initialisation de la base)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO alertes (entite_id, type, message, timestamp)
                VALUES (?, ?, ?, ?)
            """, (entite_id, type_alerte, message, datetime.now().isoformat()))
            conn.commit()

    def obtenir_alertes(self, limite: int = 20):
        """Retourne les dernières alertes : (id, entite_id, type, message, timestamp)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, entite_id, type, message, timestamp FROM alertes ORDER BY id DESC LIMIT ?",
                (limite,))
            return cursor.fetchall()
