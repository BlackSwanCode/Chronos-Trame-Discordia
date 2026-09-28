# core/timewave.py
import numpy as np
from datetime import datetime, timedelta

class TimeWaveZero:
    def __init__(self, zero_date_str: str = "2012-12-21"):
        self.zero_date = datetime.strptime(zero_date_str, "%Y-%m-%d")
        # Table de King Wen simplifiée (64 valeurs de variation de nouveauté)
        self.novelty_diffs = [
            0, -3, -1, -6, 8, 1, -7, -4, -2, -1, -2, -2, -2, -2, -2, -2,
            16, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2,
            16, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2,
            16, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2
        ]
        self.scales = [1, 64, 4096]

    def calculer_nouveaute(self, target_date: datetime) -> float:
        days_from_zero = (self.zero_date - target_date).days
        novelty = 0.0
        
        for scale in self.scales:
            index = abs(days_from_zero // scale) % 64
            novelty += self.novelty_diffs[index]
            
        # Ajout d'une composante sinusoïdale pour lisser
        phase = (days_from_zero / 67.29) * 2 * np.pi
        novelty += np.sin(phase) * 2.0
        return novelty

    def est_pic_de_nouveaute(self, target_date: datetime, historique_nouveaute: list) -> bool:
        """Vérifie si la date est dans le top 10% des pics de nouveauté"""
        if not historique_nouveaute:
            return False
        current_nov = self.calculer_nouveaute(target_date)
        threshold = np.percentile(historique_nouveaute, 90)
        return current_nov >= threshold
