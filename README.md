# Hanabi

**English** · [Deutsch](README.de.md) · [日本語](README.ja.md)

Multiplayer version of the card game Hanabi, with a Python server and a Pygame client. It includes a lobby, saved games, and an English interface. Press `L` to cycle the interface through English, German, and Japanese.

## Start

Double-click `dist/Hanabi.exe`. The window stays open. Start the server once, then start a client for each player. Each one opens in its own window. Closing the launcher does not close them.

Build that exe from this folder:

```
pip install pyinstaller
pyinstaller Hanabi.spec
```

From source, in the `src` directory:

```
python -m hanabi.launcher
```

Or start the pieces yourself, still from `src`:

```
python -m hanabi.core.server
python -m hanabi.core.client_launcher
```

## Controls

- Cycle language (English, German, Japanese): `L`
- Navigation menu: `Esc`
- Save the game: `S`
- A save can be loaded only when the same players sit in the same lobby slots

## Diagrams

The PlantUML files (`*.puml`) describe the core, the interface, and the message flow. The SVGs are the rendered versions. `Anleitung zum Start von Hanabi.pdf` is a German start guide.
