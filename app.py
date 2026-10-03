"""Small desktop interface for the playlist analyser."""

import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from dotenv import load_dotenv

load_dotenv()

from main import ask_gemini, ask_qwen3


PROMPT = "Summarize the playlist's mood, style, and standout tracks."


def main():
    root = tk.Tk()
    root.title("Playlist Analyser")
    root.geometry("620x480")
    root.minsize(480, 360)

    container = ttk.Frame(root, padding=24)
    container.pack(fill="both", expand=True)

    ttk.Label(container, text="🎵 Playlist Analyser", font=("Segoe UI", 20, "bold")).pack(anchor="w")
    ttk.Label(
        container,
        text="Get a quick read on the mood and style of your Spotify playlist.",
    ).pack(anchor="w", pady=(6, 20))

    ttk.Label(container, text="Spotify playlist URL").pack(anchor="w")
    url_var = tk.StringVar()
    url_entry = ttk.Entry(container, textvariable=url_var)
    url_entry.pack(fill="x", pady=(6, 12))
    url_entry.focus_set()

    ttk.Label(container, text="Analysis model").pack(anchor="w")
    model_var = tk.StringVar(value="Gemini")
    model_picker = ttk.Combobox(
        container,
        textvariable=model_var,
        values=("Gemini", "Qwen3 (local Ollama)"),
        state="readonly",
    )
    model_picker.pack(fill="x", pady=(6, 12))

    ttk.Label(container, text="Your playlist analysis", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(4, 0))
    result = tk.Text(container, wrap="word", height=12, state="disabled", font=("Segoe UI", 10))
    result.pack(fill="both", expand=True, pady=(16, 0))

    def show_result(text):
        result.configure(state="normal")
        result.delete("1.0", "end")
        result.insert("1.0", text)
        result.configure(state="disabled")

    def set_busy(busy):
        button.configure(state="disabled" if busy else "normal")
        status_var.set(f"Analysing with {model_var.get()}…" if busy else "")

    def run_analysis():
        playlist_url = url_var.get().strip()
        if not playlist_url:
            messagebox.showinfo("Playlist URL needed", "Paste a Spotify playlist URL to get started.", parent=root)
            return

        selected_model = model_var.get()
        api_key = None
        if selected_model == "Gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                messagebox.showerror(
                    "Gemini API key missing",
                    "Set GEMINI_API_KEY in your .env file or environment, then restart the app.",
                    parent=root,
                )
                return

        set_busy(True)
        show_result("")

        def worker():
            try:
                if selected_model == "Gemini":
                    analysis = ask_gemini(playlist_url, PROMPT, api_key)
                else:
                    analysis = ask_qwen3(playlist_url, PROMPT)
            except Exception as exc:
                root.after(0, lambda error=str(exc): finish(error=error))
            else:
                root.after(0, lambda value=analysis: finish(value=value))

        def finish(value=None, error=None):
            set_busy(False)
            if error:
                show_result("")
                messagebox.showerror("Analysis failed", error, parent=root)
            else:
                show_result(value or "No analysis was returned.")

        threading.Thread(target=worker, daemon=True).start()

    button = ttk.Button(container, text="Analyse playlist", command=run_analysis)
    button.pack(fill="x", pady=(12, 0))

    status_var = tk.StringVar()
    ttk.Label(container, textvariable=status_var).pack(anchor="w", pady=(8, 0))

    root.bind("<Return>", lambda _event: run_analysis())
    root.mainloop()


if __name__ == "__main__":
    main()
