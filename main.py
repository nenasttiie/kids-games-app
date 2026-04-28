import os
import subprocess
import sys
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_FAMILY = "Segoe UI"
FALLBACK_FONT = ("Segoe UI", "Arial", "Georgia")
APP_BG = "#FFF8FC"
HEADER_PINK = "#F06CA7"
TEXT_DARK = "#5B4B68"


class KidsMainMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Детские игры")
        self.geometry("980x780")
        self.minsize(900, 720)
        self.configure(bg=APP_BG)

        # Шрифты
        self.title_font = tkfont.Font(family=FONT_FAMILY, size=28, weight="bold")
        self.card_title_font = tkfont.Font(family=FONT_FAMILY, size=16, weight="bold")
        self.stat_font = tkfont.Font(family=FONT_FAMILY, size=12)

        self._build_ui()

    def _build_ui(self):
        hero = tk.Frame(self, bg=APP_BG)
        hero.pack(fill=tk.X, padx=34, pady=(18, 12))

        tk.Label(
            hero,
            text="Привет! Выбери игру",
            font=(FONT_FAMILY, 26, "bold"),
            bg=APP_BG,
            fg=HEADER_PINK
        ).pack()

        games_frame = tk.Frame(self, bg=APP_BG)
        games_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=5)

        top_games = tk.Frame(games_frame, bg=APP_BG)
        top_games.pack(fill=tk.BOTH, expand=True, pady=8)

        self._create_game_card(
            parent=top_games,
            title="2048",
            color_bg="#FFF1D9",
            accent="#FFB56B",
            command=self.open_2048
        ).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        self._create_game_card(
            parent=top_games,
            title="Фотобудка",
            color_bg="#EAF9F0",
            accent="#67C587",
            command=self.open_photobooth
        ).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        bottom_games = tk.Frame(games_frame, bg=APP_BG)
        bottom_games.pack(fill=tk.BOTH, expand=True, pady=8)

        self._create_game_card(
            parent=bottom_games,
            title="Рисование",
            color_bg="#FFE9F2",
            accent="#FF96B7",
            command=self.open_drawing
        ).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        self._create_game_card(
            parent=bottom_games,
            title="Скоро",
            color_bg="#F2ECFF",
            accent="#A892F5",
            command=lambda: messagebox.showinfo("Скоро", "Скоро здесь появится новая игра!")
        ).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

    def _create_game_card(self, parent, title, color_bg, accent, command):
        card = tk.Frame(
            parent,
            bg=APP_BG,
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=10
        )

        flower_card = self._create_flower_card(card, title, color_bg, accent, command)
        flower_card.pack()

        return card

    def _create_flower_card(self, parent, title, color_bg, accent, command):
        flower = tk.Canvas(
            parent,
            width=315,
            height=285,
            bg=parent.cget("bg"),
            highlightthickness=0,
            bd=0,
            cursor="hand2"
        )

        petal_positions = [
            (92, 18, 226, 128),
            (162, 62, 296, 172),
            (136, 148, 270, 258),
            (44, 148, 178, 258),
            (18, 62, 152, 172),
        ]

        petal_ids = []
        for x1, y1, x2, y2 in petal_positions:
            petal_ids.append(
                flower.create_oval(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=self._mix_hex(accent, "#FFFFFF", 0.12),
                    outline=""
                )
            )

        center_id = flower.create_oval(90, 88, 224, 222, fill="#FFF4B8", outline="")
        title_id = flower.create_text(
            157,
            155,
            text=title,
            width=145,
            font=(FONT_FAMILY, 16, "bold"),
            fill=TEXT_DARK
        )

        def set_hover(is_hovered):
            petal_color = self._mix_hex(accent, "#FFFFFF", 0.24) if is_hovered else self._mix_hex(accent, "#FFFFFF", 0.12)
            center_color = "#FFF8D6" if is_hovered else "#FFF4B8"
            for petal_id in petal_ids:
                flower.itemconfigure(petal_id, fill=petal_color)
            flower.itemconfigure(center_id, fill=center_color)

        def on_click(_event=None):
            command()

        for item_id in [*petal_ids, center_id, title_id]:
            flower.tag_bind(item_id, "<Button-1>", on_click)
            flower.tag_bind(item_id, "<Enter>", lambda _event: set_hover(True))
            flower.tag_bind(item_id, "<Leave>", lambda _event: set_hover(False))

        flower.bind("<Enter>", lambda _event: set_hover(True))
        flower.bind("<Leave>", lambda _event: set_hover(False))
        return flower

    def _mix_hex(self, color1, color2, ratio):
        def to_rgb(color):
            color = color.lstrip("#")
            return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))

        rgb1 = to_rgb(color1)
        rgb2 = to_rgb(color2)
        mixed = tuple(int(a * (1 - ratio) + b * ratio) for a, b in zip(rgb1, rgb2))
        return "#" + "".join(f"{value:02X}" for value in mixed)

    def _run_module(self, script_path, working_dir):
        try:
            self.update_idletasks()
            env = os.environ.copy()
            env["APP_WINDOW_X"] = str(self.winfo_x())
            env[("APP"
                 "_WINDOW_Y")] = str(self.winfo_y())
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
        self._run_module(os.path.join("drawing", "drawing.py"), os.path.join(BASE_DIR, "modules"))


if __name__ == "__main__":
    app = KidsMainMenu()
    app.mainloop()