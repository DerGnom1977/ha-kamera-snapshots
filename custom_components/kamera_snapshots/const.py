"""Sonoff-Kamera Snapshot-Archiv: Spezifikation."""
from __future__ import annotations

from .framework import Field, Spec

DOMAIN = "kamera_snapshots"
TITLE = "Kamera Snapshot-Archiv"
PREFIX = "kamera"
VERSION = "1.0.0"
DESCRIPTION = "Speichert bei Bewegung ein Bild in einem Ringpuffer mit 20 Plätzen und zeigt sie nach Zeit sortiert an."
SLOTS = 20
SNAP_DIR = "/config/www/snapshots"
SNAP_URL = "/local/snapshots"

FIELDS = [
    Field("bewegung", "binary_sensor.kamera_bewegung", "entity", "Bewegungsmelder", ("binary_sensor",)),
    Field("kamera", "camera.kamera_mainstream", "entity", "Kamera", ("camera",)),
]


def eintraege(rt) -> list[tuple[int, int, str]]:
    """Liste (Rang ab 1, Slot, Zeitstempel), neueste zuerst."""
    times = rt.mem.get("times") or [""] * SLOTS
    nxt = int(rt.mem.get("next", 0))
    out = []
    for k in range(SLOTS):
        slot = (nxt - 1 - k) % SLOTS
        if times[slot]:
            out.append((len(out) + 1, slot, times[slot]))
    return out


def _label(i: int, e: tuple[int, int, str]) -> str:
    return f"{e[0]} · {e[2]}" + (" (aktuell)" if i == 0 else "")


def auswahl(rt) -> str:
    ein = eintraege(rt)
    if not ein:
        return "Keine Bilder"
    rang = int(rt.flt("kamera_bild", 1)) - 1
    i = rang if 0 <= rang < len(ein) else 0
    return _label(i, ein[i])


def auswahl_attrs(rt) -> dict:
    ein = eintraege(rt)
    if not ein:
        return {"optionen": [], "url": None, "datei": None}
    rang = int(rt.flt("kamera_bild", 1)) - 1
    i = rang if 0 <= rang < len(ein) else 0
    slot = ein[i][1]
    stamp = int(rt.mem.get("stamp", 0))
    return {
        "optionen": [_label(k, e) for k, e in enumerate(ein)],
        "url": f"{SNAP_URL}/cam_{slot:02d}.jpg?v={stamp}",
        "datei": f"cam_{slot:02d}.jpg",
        "slot": slot,
    }


def anzahl(rt) -> int:
    return len(eintraege(rt))


SPECS = [
    Spec("switch", "kamera_aktiv", "Snapshot bei Bewegung", "mdi:camera-burst", True),
    Spec("number", "kamera_entprellung", "Mindestabstand zwischen Bildern", "mdi:timer-sand", 30, 0, 600, 5, "s", "slider"),
    Spec("number", "kamera_bild", "Angezeigtes Bild (1 = neuestes)", "mdi:image-multiple", 1, 1, SLOTS, 1, None, "box"),
    Spec("sensor", "kamera_snapshot_auswahl", "Kamera Snapshot Auswahl", "mdi:image", fn=auswahl, attrs=auswahl_attrs),
    Spec("sensor", "kamera_snapshot_anzahl", "Kamera Snapshots gespeichert", "mdi:counter", state_class="measurement", fn=anzahl),
    Spec("button", "kamera_snapshot_jetzt", "Snapshot jetzt", "mdi:camera", press="snapshot"),
    Spec("button", "kamera_bild_neuer", "Neueres Bild", "mdi:chevron-left", press="neuer"),
    Spec("button", "kamera_bild_aelter", "Älteres Bild", "mdi:chevron-right", press="aelter"),
    Spec("button", "kamera_archiv_leeren", "Archiv leeren", "mdi:delete-sweep", press="leeren"),
    Spec("button", "kamera_standardwerte", "Standardwerte setzen", "mdi:restore", press="reset"),
]

EXTRA_CARDS = [
    {
        "type": "markdown",
        "title": "Aktuelles Bild",
        "content": "{{ states('sensor.kamera_snapshot_auswahl') }}\n\n"
        "{% set u = state_attr('sensor.kamera_snapshot_auswahl','url') %}"
        "{% if u %}![Snapshot]({{ u }}){% endif %}",
    }
]

SECTIONS = [
    ("Archiv", ["kamera_snapshot_auswahl", "kamera_snapshot_anzahl", "kamera_bild", "kamera_bild_neuer", "kamera_bild_aelter", "kamera_snapshot_jetzt", "kamera_archiv_leeren"]),
    ("Einstellungen", ["kamera_aktiv", "kamera_entprellung", "kamera_standardwerte"]),
]
