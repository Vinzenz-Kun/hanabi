# Hanabi

[English](README.md) · **Deutsch** · [日本語](README.ja.md)

Mehrspieler-Version des Kartenspiels Hanabi: Python-Server und Pygame-Client, mit Lobby und Spielständen. Die Oberfläche startet auf Englisch. `L` wechselt Englisch → Deutsch → Japanisch.

## Start

`dist/Hanabi.exe` doppelklicken. Das Fenster bleibt offen. Einmal den Server starten, dann pro Spieler einen Client. Jeder Client öffnet ein eigenes Fenster. Den Launcher schließen beendet Server und Clients nicht.

Exe in diesem Ordner bauen:

```
pip install pyinstaller
pyinstaller Hanabi.spec
```

Aus dem Quellcode, im Ordner `src`:

```
python -m hanabi.launcher
```

Oder die Teile einzeln, ebenfalls aus `src`:

```
python -m hanabi.core.server
python -m hanabi.core.client_launcher
```

## Steuerung

- Sprache (Englisch, Deutsch, Japanisch): `L`
- Navigationsmenü: `Esc`
- Spiel speichern: `S`
- Ein Spielstand lässt sich nur laden, wenn dieselben Spieler auf denselben Lobby-Plätzen sitzen

## Diagramme

Die PlantUML-Dateien (`*.puml`) beschreiben Kern, Oberfläche und Nachrichtenfluss. Die SVGs sind die gerenderten Versionen. `Anleitung zum Start von Hanabi.pdf` ist eine deutsche Starthilfe.
