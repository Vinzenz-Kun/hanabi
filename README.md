# Hanabi

Mehrspieler-Umsetzung des Kartenspiels Hanabi mit Python-Server und Pygame-Client. Dazu gehören Lobby, Spielstände und eine deutsch/englische Oberfläche.

## Start

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Zwei Terminals, jeweils im Ordner `src`:

```
python -m hanabi.core.server
python -m hanabi.core.client_launcher
```

Den Client für jeden weiteren Spieler noch einmal starten.

## Steuerung

- Sprache wechseln: `L`
- Navigationsmenü: `Esc`
- Spiel speichern: `S`
- Ein Speicherstand lässt sich nur laden, wenn dieselben Spieler in denselben Lobby-Slots sitzen

## Diagramme

Die PlantUML-Dateien (`*.puml`) beschreiben Kern, Oberfläche und den Ablauf. Die SVGs sind die gerenderten Fassungen. `Anleitung zum Start von Hanabi.pdf` beschreibt den Start noch einmal im Detail.
