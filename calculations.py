from datetime import date, datetime
from typing import Any, Dict, List

def sum_sopimukset(sopimukset: List[Dict[str, Any]]) -> float:
    """Laskee voimassaolevien sopimusten kokonaisarvon."""
    total = 0.0
    for a in sopimukset:
        try:
            loppu = datetime.fromisoformat(a.get('sopimus', '')).date()
            if loppu >= date.today():
                total += a.get('kokonaisarvo', 0)
        except Exception:
            continue
    return total


def sum_kulut(kulut: List[Dict[str, Any]]) -> float:
    """Laskee kululistan vuosikulut yhteen."""
    return sum(item.get('kokonaisarvo', 0) for item in kulut)


def laske_palkka_metrics(total_sopimukset: float, kulut: float, vero_pct: int, tavoite_netto: float) -> Dict[str, float]:
    """Laskee kuukausittaiset myynti-, brutto-, netto- ja kuiluluvut."""
    kuukausi_myynnit = total_sopimukset / 12
    brutto = kuukausi_myynnit - (kulut / 12)
    verot = max(brutto, 0) * (vero_pct / 100)
    netto = max(brutto, 0) - verot
    # Myyntikuilu verrattuna vuosittaiseen tavoite_nettoon
    myyntikuilu = total_sopimukset - (kulut + tavoite_netto * 12 / (1 - vero_pct / 100))
    return {
        'kuukausi_myynnit': kuukausi_myynnit,
        'brutto': brutto,
        'netto': netto,
        'verot': verot,
        'myyntikuilu': myyntikuilu,
    }
