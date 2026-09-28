# core/ontology.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class EntiteOntique:
    id: str
    nom: str
    description: str
    date_debut: str
    date_fin: Optional[str]
    
    # --- Héritage BDO ---
    classe_principale: str  # RM, IR, ESC, VMO, Omega, etc.
    coeur_dominant: str     # "noir", "gris", "blanc", "NC"
    delta_avant: float
    delta_pendant: float
    delta_apres: float
    risque: int             # 1 à 5
    
    # --- Héritage Trame & Temporal ---
    couches_osi: List[int] = field(default_factory=list)
    fragments_runiques: List[str] = field(default_factory=list)
    paleo_memes: List[str] = field(default_factory=list)
    
    # --- État Quantique ---
    superposition_active: bool = False
    intention_observateur: float = 0.5  # 0.0 (Noir) à 1.0 (Blanc)

    @property
    def delta_moyen(self) -> float:
        return (self.delta_avant + self.delta_pendant + self.delta_apres) / 3.0

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}
