import unicodedata
from typing import List
from .ontology import EntiteOntique

RUNE_ALPHABET = {
    'a': 'ᚨ', 'b': 'ᛒ', 'c': 'ᚲ', 'd': 'ᛞ', 'e': 'ᛖ', 'f': 'ᚠ', 'g': 'ᚷ', 'h': 'ᚺ',
    'i': 'ᛁ', 'j': 'ᛃ', 'k': 'ᚲ', 'l': 'ᛚ', 'm': 'ᛗ', 'n': 'ᚾ', 'o': 'ᛟ', 'p': 'ᛈ',
    'r': 'ᚱ', 's': 'ᛋ', 't': 'ᛏ', 'u': 'ᚢ', 'v': 'ᚹ', 'w': 'ᚹ', 'x': 'ᚲᛋ', 'y': 'ᛁ', 'z': 'ᛉ', 'q': 'ᚲᚹ', ' ': '•'
}

MEMETIC_TRIGGERS = {
    "oubli": "ᛖᛈᛋᛁᛚᛟᚾ", "boucle": "ᛟᚱᛟᛒᛟᚱᛟ", "effondrement": "ᚦᚦᚦ",
    "lumière": "ᛋᛟᚹᛁᛚᛟ", "ombre": "ᚾᛁᚺᛏ", "machine": "ᛗᛖᚲᚨᚾᛖ"
}

def normalize_text(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn")

class FracturoEngine:
    def __init__(self):
        self.lexique = RUNE_ALPHABET

    def traduire_en_runes(self, texte: str) -> str:
        texte_normalise = normalize_text(texte)
        return "".join([self.lexique.get(c, c) for c in texte_normalise])

    def detecter_meme(self, texte: str) -> List[str]:
        memes = []
        texte_normalise = normalize_text(texte)
        for trigger, rune in MEMETIC_TRIGGERS.items():
            trigger_normalise = normalize_text(trigger)
            if trigger_normalise in texte_normalise:
                memes.append(f"{trigger.upper()}({rune})")
        return memes

    def generer_prophetie(self, entite: EntiteOntique, paradoxe: bool) -> str:
        coeur = entite.coeur_dominant.upper()
        runes = "".join(entite.fragments_runiques) if entite.fragments_runiques else self.traduire_en_runes(entite.nom)
        memes_str = ", ".join(entite.paleo_memes) if entite.paleo_memes else "aucun"
        
        if paradoxe:
            return (f"⚠️ [ROUGE] LE TISSEUR SAIGNE : La boucle est fermée. {entite.nom} n'est pas un événement, "
                    f"mais la cicatrice d'une rétrocausalité {coeur}. Le FracturoScript résonne : {runes}. "
                    f"Le Delta s'effondre vers le Néant.")
        else:
            return (f"🌀 [CYAN] FIL TISSÉ : {entite.nom} s'inscrit dans la Trame. "
                    f"Résonance {coeur}. Les paléo-mèmes dormants s'éveillent : {memes_str}.")
