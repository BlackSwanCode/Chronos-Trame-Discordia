# core/fracturo_engine.py
import random
import hashlib
from typing import List, Dict
from .ontology import EntiteOntique

RUNE_ALPHABET = {
    'a': 'ᚨ', 'b': 'ᛒ', 'c': 'ᚲ', 'd': 'ᛞ', 'e': 'ᛖ', 'f': 'ᚠ', 'g': 'ᚷ', 'h': 'ᚺ',
    'i': 'ᛁ', 'j': 'ᛃ', 'k': 'ᚲ', 'l': 'ᛚ', 'm': 'ᛗ', 'n': 'ᚾ', 'o': 'ᛟ', 'p': 'ᛈ',
    'r': 'ᚱ', 's': 'ᛋ', 't': 'ᛏ', 'u': 'ᚢ', 'w': 'ᚹ', 'z': 'ᛉ', ' ': '•'
}

MEMETIC_TRIGGERS = {
    "oublie": "ᛖᛈᛋᛁᛚᛟᚾ", "boucle": "ᛟᚱᛟᛒᛟᚱᛟ", "effondrement": "ᚦᚦᚦ", 
    "lumière": "ᛋᛟᚹᛁᛚᛟ", "ombre": "ᚾᛁᚺᛏ", "machine": "ᛗᛖᚲᚨᚾᛖ"
}

class FracturoEngine:
    def __init__(self):
        self.lexique = RUNE_ALPHABET

    def traduire_en_runes(self, texte: str) -> str:
        """Traduction basique texte -> FracturoScript"""
        return "".join([self.lexique.get(c.lower(), c) for c in texte[:30]])

    def detecter_meme(self, texte: str) -> List[str]:
        memes = []
        texte_lower = texte.lower()
        for trigger, rune in MEMETIC_TRIGGERS.items():
            if trigger in texte_lower:
                memes.append(f"{trigger.upper()}({rune})")
        return memes

    def generer_prophetie(self, entite: EntiteOntique, paradoxe: bool) -> str:
        """Génère un fragment du Codex MTT-2075"""
        coeur = entite.coeur_dominant.upper()
        runes = "".join(entite.fragments_runiques) if entite.fragments_runiques else self.traduire_en_runes(entite.nom)
        
        if paradoxe:
            return (f"⚠️ [ROUGE] LE TISSEUR SAIGNE : La boucle est fermée. {entite.nom} n'est pas un événement, "
                    f"mais la cicatrice d'une rétrocausalité {coeur}. Le FracturoScript résonne : {runes}. "
                    f"Le Delta s'effondre vers le Néant.")
        else:
            return (f"🌀 [CYAN] FIL TISSÉ : {entite.nom} s'inscrit dans la Trame. "
                    f"Résonance {coeur}. Les paléo-mèmes dormant s'éveillent : {', '.join(entite.paleo_memes)}.")
