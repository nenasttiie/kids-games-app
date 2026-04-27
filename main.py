import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_FAMILY = "Georgia"


class KidsMainMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kids Games App")
        self.geometry("720x720")
        self.minsize(680, 500)
        self.configure(bg="#FFEFF7")

        self._build_ui()

    def _build_ui(self):

        title = tk.Label(
            self,
            text="Добро пожаловать!",
            font=(FONT_FAMILY, 33, "bold"),
            bg="#FFEFF7",
            fg="#E4579A",
        )
        title.pack(pady=(6, 6))

        subtitle = tk.Label(
            self,
            text="Выбери игру",
            font=(FONT_FAMILY, 15, "bold"),
            bg="#FFEFF7",
            fg="#9B63D5",
        )
        subtitle.pack(pady=(0, 18))

        card = tk.Frame(
            self,
            bg="#FFFDFE",
            bd=2,
            relief=tk.RIDGE,
            highlightbackground="#F8BBD8",
            highlightthickness=2,
        )
        card.pack(padx=42, pady=10, fill=tk.BOTH, expand=True)

        card_title = tk.Label(
            card,
            text="Главное меню",
            font=(FONT_FAMILY, 17, "bold"),
            bg="#FFFDFE",
            fg="#C95D93",
        )
        card_title.pack(pady=(18, 10))

        buttons_wrap = tk.Frame(card, bg="#FFFDFE")
        buttons_wrap.pack(expand=True, fill=tk.BOTH, padx=30, pady=(0, 8))

        self._create_game_card(
            parent=buttons_wrap,
            title="2048",
            subtitle="Собирай числа и ставь рекорды",
            color="#FFE08A",
            hover="#FFD15A",
            command=self.open_2048,
        ).pack(fill=tk.X, pady=8)

        self._create_game_card(
            parent=buttons_wrap,
            title="Фотобудка",
            subtitle="Веселые фильтры и яркие фото",
            color="#A8E8F5",
            hover="#7CDAED",
            command=self.open_photobooth,
        ).pack(fill=tk.X, pady=8)

        self._create_game_card(
            parent=buttons_wrap,
            title="Рисование",
            subtitle="Рисуй, раскрашивай и фантазируй",
            color="#BDF4D4",
            hover="#96EAB9",
            command=self.open_drawing,
        ).pack(fill=tk.X, pady=8)

        hint = tk.Label(
            self,
            text="Окно меню остается открытым - можно запускать игры снова",
            font=(FONT_FAMILY, 10, "italic"),
            bg="#FFEFF7",
            fg="#896C7A",
        )
        hint.pack(pady=(10, 12))

    def _create_game_card(self, parent, title, subtitle, color, hover, command):
        wrapper = tk.Frame(parent, bg="#FFFDFE")

        title_btn = tk.Button(
            wrapper,
            text=title,
            font=(FONT_FAMILY, 18, "bold"),
            bg=color,
            fg="#3E3E3E",
            activebackground=hover,
            activeforeground="#2A2A2A",
            relief=tk.RAISED,
            bd=3,
            cursor="hand2",
            height=1,
            command=command,
        )
        title_btn.pack(fill=tk.X)

        subtitle_lbl = tk.Label(
            wrapper,
            text=subtitle,
            font=(FONT_FAMILY, 10, "italic"),
            bg="#FFFDFE",
            fg="#8D7582",
        )
        subtitle_lbl.pack(anchor="w", padx=8, pady=(4, 0))

        return wrapper

    def _run_module(self, script_path, working_dir):
        try:
            self.update_idletasks()
            env = os.environ.copy()
            env["APP_WINDOW_X"] = str(self.winfo_x())
            env["APP_WINDOW_Y"] = str(self.winfo_y())
            env["APP_WINDOW_W"] = str(self.winfo_width())
            env["APP_WINDOW_H"] = str(self.winfo_height())

            subprocess.Popen(
                [sys.executable, script_path],
                cwd=working_dir,
                env=env,
            )
        except Exception as exc:
            messagebox.showerror("Ошибка запуска", f"Не удалось открыть модуль:\n{exc}")

    def open_2048(self):
        self._run_module("main_window.py", os.path.join(BASE_DIR, "modules", "2048"))

    def open_photobooth(self):
        self._run_module("photobooth.py", os.path.join(BASE_DIR, "modules", "masks"))

    def open_drawing(self):
        self._run_module("drawing\\drawing.py", os.path.join(BASE_DIR, "modules"))


if __name__ == "__main__":
    app = KidsMainMenu()
    app.mainloop()
