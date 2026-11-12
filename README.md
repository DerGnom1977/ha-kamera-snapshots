# Kamera Snapshot-Archiv

Speichert bei Bewegung ein Bild in einem Ringpuffer mit 20 Plätzen und zeigt sie nach Zeit sortiert an.

Python-Integration für Home Assistant (HACS). Sie ersetzt das bisherige YAML-Paket
`sonoff_cam_s2/packages/kamera_snapshots.yaml`: Einstellungen sind jetzt eigene Entitäten (Schalter, Zahlen, Auswahlfelder,
Uhrzeiten), die Logik läuft in Python statt in Automationen und Skripten.

## Installation

1. HACS → Integrationen → ⋮ → **Benutzerdefinierte Repositories** →
   `https://github.com/DerGnom1977/ha-kamera-snapshots` als Kategorie **Integration** hinzufügen.
2. **Kamera Snapshot-Archiv** installieren und Home Assistant neu starten.
3. Einstellungen → Geräte & Dienste → **Integration hinzufügen** → *Kamera Snapshot-Archiv*.
4. Das Dashboard aus `dashboards/kamera_snapshots_dashboard.yaml` anlegen (Raw-Konfigurationseditor).

Manuell: Ordner `custom_components/kamera_snapshots` nach `/config/custom_components/` kopieren.

## Einrichtung

Beim Hinzufügen (und später über „Konfigurieren“) werden diese Angaben abgefragt:

- **Bewegungsmelder** (`bewegung`), Standard: `binary_sensor.kamera_bewegung`
- **Kamera** (`kamera`), Standard: `camera.kamera_mainstream`

## Was du anpassen musst

Alle Standardwerte oben sind **Platzhalter/Beispiele**. Passe sie beim Einrichten an dein System an:

- **Notify-Dienste** (`notify_person1`, `notify_person2`): Name deines Handy-Dienstes ohne `notify.`,
  z. B. `mobile_app_mein_handy` → bei dir `mobile_app_<gerätename>` (Entwicklerwerkzeuge → Aktionen → „notify“).
  „Person 1/Person 2“ sind frei; die Schalter *Push an Person 1/2* schalten die jeweilige Meldung.
- **Entitäten** (`sensor.…`, `camera.…`, `person.…`, `todo.…` usw.): auf die echten Entitäts-IDs aus
  Einstellungen → Geräte & Dienste → Entitäten ändern. Leere Felder sind Pflicht, wenn die Funktion genutzt wird.
- **Dashboard** (`dashboards/kamera_snapshots_dashboard.yaml`): enthält Entitäts-IDs der Integration; wenn du Namen
  oder Räume änderst, dort per Suchen/Ersetzen nachziehen.
- Später jederzeit unter Einstellungen → Geräte & Dienste → *Kamera Snapshot-Archiv* → **Konfigurieren** änderbar.

## Umstieg vom YAML-Paket

1. Das alte Paket `sonoff_cam_s2/packages/kamera_snapshots.yaml` (und sein Dashboard) aus `/config/packages/` entfernen
   und Home Assistant neu starten, damit Helfer, Automationen und Skripte nicht doppelt laufen.
2. Integration einrichten. Neue Entitäten haben dieselben Namen wie die alten Helfer, nur mit
   anderer Domain, z. B. `input_boolean.xyz` wird `switch.xyz`, `input_number.xyz` wird `number.xyz`,
   `input_select.xyz` wird `select.xyz`, `input_datetime.xyz` wird `time.xyz`.
3. Eigene Automationen und Dashboards, die alte Entitäten nutzen, entsprechend anpassen.
4. Die alten Standardwerte sind schon eingebaut, die Einstellungen bleiben nach Neustarts erhalten.

## Dienste

- `kamera_snapshots.snapshot` – Speichert sofort ein Bild im Ringpuffer.

## Entitäten

### Schalter

- `switch.kamera_aktiv` – Snapshot bei Bewegung

### Zahlenwerte

- `number.kamera_entprellung` – Mindestabstand zwischen Bildern
- `number.kamera_bild` – Angezeigtes Bild (1 = neuestes)

### Sensoren

- `sensor.kamera_snapshot_auswahl` – Kamera Snapshot Auswahl
- `sensor.kamera_snapshot_anzahl` – Kamera Snapshots gespeichert

### Knöpfe

- `button.kamera_snapshot_jetzt` – Snapshot jetzt
- `button.kamera_bild_neuer` – Neueres Bild
- `button.kamera_bild_aelter` – Älteres Bild
- `button.kamera_archiv_leeren` – Archiv leeren
- `button.kamera_standardwerte` – Standardwerte setzen

## Hinweis

Die Integration wurde aus dem bestehenden YAML-Paket portiert und ist noch nicht in einer laufenden
Home-Assistant-Instanz getestet. Bitte beim ersten Einsatz die Logbuch-/Protokoll-Meldungen
(`custom_components.kamera_snapshots`) im Blick behalten.
