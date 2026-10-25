"""Stay-open window that starts the Hanabi server or another client."""

import os
import subprocess
import sys
import tkinter as tk

CREATE_NEW_CONSOLE = 0x00000010


def source_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def runtime_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return source_root()


def spawn(mode: str) -> subprocess.Popen:
    flags = CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    if getattr(sys, "frozen", False):
        command = [sys.executable, mode]
        cwd = os.path.dirname(sys.executable)
    else:
        module = {
            "--server": "hanabi.core.server",
            "--client": "hanabi.core.client_launcher",
        }[mode]
        command = [sys.executable, "-m", module]
        cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return subprocess.Popen(command, cwd=cwd, creationflags=flags)


def run_server() -> None:
    os.chdir(runtime_dir())
    from hanabi.core.server import Server

    Server().start_server()


def run_client() -> None:
    os.chdir(runtime_dir())
    from hanabi.core.client_launcher import Client

    Client().render_gui()


class Launcher:
    def __init__(self) -> None:
        self.server: subprocess.Popen | None = None
        self.clients: list[subprocess.Popen] = []
        self.root = tk.Tk()
        self.root.title("Hanabi")
        self.root.resizable(False, False)
        self.root.configure(bg="#100820")
        frame = tk.Frame(self.root, bg="#100820", padx=22, pady=18)
        frame.grid()
        tk.Label(
            frame,
            text=(
                "Start the server once, then one client for each player.\n"
                "This window stays open, so you can start more clients."
            ),
            justify="left",
            bg="#100820",
            fg="#f4ecfc",
            font=("Yu Gothic UI", 11),
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        self.server_button = tk.Button(
            frame,
            text="Start server",
            command=self.start_server,
            bg="#8a56d6",
            fg="#f8f2ff",
            activebackground="#a67ae0",
            activeforeground="#f8f2ff",
            relief="flat",
            padx=18,
            pady=8,
            font=("Yu Gothic UI", 11),
        )
        self.server_button.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(16, 0))
        tk.Button(
            frame,
            text="Start client",
            command=self.start_client,
            bg="#442a6c",
            fg="#f4ecfc",
            activebackground="#5a3890",
            activeforeground="#f8f2ff",
            relief="flat",
            padx=18,
            pady=8,
            font=("Yu Gothic UI", 11),
        ).grid(row=1, column=1, sticky="ew", pady=(16, 0))
        self.status = tk.StringVar()
        tk.Label(
            frame,
            textvariable=self.status,
            bg="#100820",
            fg="#baa8d6",
            font=("Yu Gothic UI", 10),
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(14, 0))
        self.refresh()

    def alive(self, process: subprocess.Popen | None) -> bool:
        return process is not None and process.poll() is None

    def start_server(self) -> None:
        if self.alive(self.server):
            return
        self.server = spawn("--server")
        self.refresh()

    def start_client(self) -> None:
        self.clients.append(spawn("--client"))
        self.refresh()

    def refresh(self) -> None:
        self.clients = [process for process in self.clients if self.alive(process)]
        if self.alive(self.server):
            self.server_button.configure(state="disabled", bg="#3a2858", fg="#baa8d6")
            server_text = "Server is running."
        else:
            self.server_button.configure(state="normal", bg="#8a56d6", fg="#f8f2ff")
            server_text = "Server is not running."
        self.status.set(f"{server_text} Open clients: {len(self.clients)}.")
        self.root.after(500, self.refresh)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        run_server()
        return
    if len(sys.argv) > 1 and sys.argv[1] == "--client":
        run_client()
        return
    Launcher().run()


if __name__ == "__main__":
    main()
