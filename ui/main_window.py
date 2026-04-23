import customtkinter as ctk


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("KidsUniverse - Главное меню")
        self.geometry("600x400")

        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text="Выберите игру!", font=("Arial", 28, "bold"))
        self.label.grid(row=0, column=0, padx=20, pady=40)

        self.draw_btn = ctk.CTkButton(self, text="Рисование", width=200, height=50,
                                      fg_color="#FF5733", hover_color="#C70039",
                                      command=self.open_drawing)
        self.draw_btn.grid(row=1, column=0, padx=20, pady=10)

        self.games_btn = ctk.CTkButton(self, text="Игры", width=200, height=50,
                                       fg_color="#33FF57", hover_color="#28B463",
                                       command=self.open_games)
        self.games_btn.grid(row=2, column=0, padx=20, pady=10)

        self.photo_btn = ctk.CTkButton(self, text="Фотобудка", width=200, height=50,
                                       fg_color="#3357FF", hover_color="#1F618D",
                                       command=self.open_photobooth)
        self.photo_btn.grid(row=3, column=0, padx=20, pady=10)

    def open_drawing(self):
        print("Переход к рисованию...")

    def open_games(self):
        print("Переход к играм...")

    def open_photobooth(self):
        print("Переход к фотобудке...")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
