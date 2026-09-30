# core/webhook_notifier.py
import os
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import List, Optional


class DiscordNotifier:
    """Envoie les alertes Omega vers un webhook Discord.

    Silencieux si aucune URL n'est configurée : le script ne plante jamais en local.
    Priorité : argument > variable d'environnement CHRONOS_TRAME_WEBHOOK_URL > None.
    """

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("CHRONOS_TRAME_WEBHOOK_URL") or None

    @staticmethod
    def _tronquer(texte: str, limite: int) -> str:
        """Discord limite la taille des champs d'un embed (1024 caractères)."""
        return texte if len(texte) <= limite else texte[: limite - 1] + "…"

    def send_omega_alert(self, entite_nom: str, runes: str, cycle: List[str],
                         paleo_memes: List[str], delta: float):
        """Envoie une alerte formatée en Embed Discord lors d'un Mugissement Quantique."""
        if not self.webhook_url:
            return  # Mode silencieux si non configuré

        cycle_str = " ➜ ".join(cycle + [cycle[0]])  # Referme la boucle visuellement
        memes_str = ", ".join(paleo_memes) if paleo_memes else "Aucun détecté"

        payload = {
            "embeds": [{
                "title": "⚠️ MUGISSEMENT QUANTIQUE DÉTECTÉ ⚠️",
                "color": 12582912,  # Rouge sombre (0xC00000)
                "description": "Le Léviathan a détecté une convergence ontique critique. **Le passé a été réécrit.**",
                "fields": [
                    {"name": "📍 Entité Déclencheuse",
                     "value": self._tronquer(f"**{entite_nom}**", 1024), "inline": False},
                    {"name": "🔮 FracturoScript Résonant",
                     "value": self._tronquer(f"```text\n{runes}\n```", 1024), "inline": True},
                    {"name": "🕸️ Boucle Rétrocausale",
                     "value": self._tronquer(f"`{cycle_str}`", 1024), "inline": True},
                    {"name": "🧠 Paléo-mèmes Activés",
                     "value": self._tronquer(memes_str, 1024), "inline": False},
                    {"name": "📉 Effondrement du Delta",
                     "value": f"**{delta:.2f}** (Zone de Cœur Noir)", "inline": False},
                ],
                "footer": {"text": "Codex MTT-2075 | Chronos-Trame v2.0"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }]
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.webhook_url,
            data=data,
            # Un User-Agent explicite est requis : Discord (Cloudflare) rejette
            # l'agent par défaut "Python-urllib" avec une erreur 403.
            headers={"Content-Type": "application/json",
                     "User-Agent": "Chronos-Trame/2.0 (+MTT-2075)"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status in (200, 204):
                    print("  ↳ [Discord] Alerte Omega transmise avec succès.")
        except urllib.error.HTTPError as e:
            print(f"  ↳ [Discord] Erreur HTTP {e.code}: {e.reason}")
        except Exception as e:
            print(f"  ↳ [Discord] Échec de la transmission : {e}")
