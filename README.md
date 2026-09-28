# Hanabi

Multiplayer version of the card game Hanabi, with a Python server and a Pygame client. It includes a lobby, saved games, and an English interface. Press `L` to switch the interface to German.

## Start

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

From the `src` directory, in two terminals:

```
python -m hanabi.core.server
python -m hanabi.core.client_launcher
```

Start the client again for each additional player.

## Controls

- Switch language: `L`
- Navigation menu: `Esc`
- Save the game: `S`
- A save can be loaded only when the same players sit in the same lobby slots

## Diagrams

The PlantUML files (`*.puml`) describe the core, the interface, and the message flow. The SVGs are the rendered versions. `Anleitung zum Start von Hanabi.pdf` is a German start guide.
