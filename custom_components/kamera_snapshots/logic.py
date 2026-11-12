"""Kamera Snapshot-Archiv: Fachlogik (Port von kamera_snapshots.yaml)."""
from __future__ import annotations

import logging
import os
import time

import voluptuous as vol
from homeassistant.core import Event, ServiceCall
from homeassistant.helpers.storage import Store

from .const import SLOTS, SNAP_DIR, eintraege
from .framework import LogicBase, now_local

_LOGGER = logging.getLogger(__name__)


class Logic(LogicBase):
    def __init__(self, rt) -> None:
        super().__init__(rt)
        rt.mem.update(times=[""] * SLOTS, next=0, stamp=0, last=0.0)
        self.store = Store(rt.hass, 1, f"{rt.domain}_{rt.entry.entry_id}")
        rt.actions.update(
            snapshot=self.snapshot,
            neuer=self.neuer,
            aelter=self.aelter,
            leeren=self.leeren,
            reset=self._reset,
        )

        async def _svc(call: ServiceCall) -> None:
            await self.snapshot()

        rt.register_service("snapshot", _svc, vol.Schema({}))

    async def async_start(self) -> None:
        rt = self.rt
        data = await self.store.async_load() or {}
        times = list(data.get("times") or [])
        rt.mem["times"] = (times + [""] * SLOTS)[:SLOTS]
        rt.mem["next"] = int(data.get("next", 0)) % SLOTS
        rt.mem["stamp"] = int(data.get("stamp", 0))
        await rt.hass.async_add_executor_job(lambda: os.makedirs(SNAP_DIR, exist_ok=True))
        rt.track_state([rt.cfg("bewegung")], self._bewegung)
        rt.refresh()

    async def _speichern(self) -> None:
        m = self.rt.mem
        await self.store.async_save({"times": m["times"], "next": m["next"], "stamp": m["stamp"]})

    async def _reset(self) -> None:
        self.rt.reset_defaults()

    async def _bewegung(self, event: Event) -> None:
        rt = self.rt
        new = event.data.get("new_state")
        if new is None or new.state != "on" or not rt.on("kamera_aktiv"):
            return
        # Entprellung: nicht öfter als alle X Sekunden
        if time.time() - rt.mem["last"] <= rt.flt("kamera_entprellung", 30):
            return
        await self.snapshot()

    async def snapshot(self) -> None:
        """Nächsten Slot beschreiben (auch manuell, ohne Entprellung)."""
        rt = self.rt
        kamera = rt.cfg("kamera")
        if not kamera:
            _LOGGER.warning("Keine Kamera konfiguriert")
            return
        slot = int(rt.mem["next"]) % SLOTS
        ok = await rt.call("camera", "snapshot", {"entity_id": kamera, "filename": f"{SNAP_DIR}/cam_{slot:02d}.jpg"})
        if not ok:
            return
        rt.mem["times"][slot] = now_local().strftime("%d.%m %H:%M")
        rt.mem["next"] = (slot + 1) % SLOTS
        rt.mem["stamp"] = int(time.time())
        rt.mem["last"] = time.time()
        rt.values["kamera_bild"] = 1.0
        await self._speichern()
        rt.refresh()

    async def neuer(self) -> None:
        rt = self.rt
        rt.set("kamera_bild", max(1.0, rt.flt("kamera_bild", 1) - 1))

    async def aelter(self) -> None:
        rt = self.rt
        n = max(1, len(eintraege(rt)))
        rt.set("kamera_bild", min(float(n), rt.flt("kamera_bild", 1) + 1))

    async def leeren(self) -> None:
        rt = self.rt
        rt.mem["times"] = [""] * SLOTS
        rt.mem["next"] = 0
        rt.values["kamera_bild"] = 1.0
        await self._speichern()
        rt.refresh()
