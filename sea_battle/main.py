import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import random
import json
import os


class BattleshipGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Морской бой")
        self.root.geometry("900x700")

        # Настройки игры
        self.board_size = 10
        self.ships = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]  # Размеры кораблей
        self.player_board = []
        self.computer_board = []
        self.player_target_board = []
        self.computer_target_board = []
        self.current_turn = "player"  # или "computer"
        self.game_over = False
        self.ships_placed = False
        self.placement_mode = False
        self.current_ship_index = 0
        self.current_ship_orientation = "horizontal"

        # Цвета для интерфейса
        self.colors = {
            "water": "#4a86e8",
            "ship": "#5b5b5b",
            "hit": "#e74c3c",
            "miss": "#3498db",
            "grid": "#2c3e50",
            "bg": "#ecf0f1",
            "text": "#2c3e50"
        }

        # Создание главного меню
        self.create_main_menu()

        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Загрузка сохраненных настроек
        self.load_settings()

    def create_main_menu(self):
        """Создание главного меню"""
        self.clear_window()

        # Фрейм для меню
        menu_frame = tk.Frame(self.root, bg=self.colors["bg"])
        menu_frame.pack(expand=True, fill="both", padx=50, pady=50)

        # Заголовок
        title_label = tk.Label(
            menu_frame,
            text="МОРСКОЙ БОЙ",
            font=("Arial", 36, "bold"),
            fg=self.colors["text"],
            bg=self.colors["bg"]
        )
        title_label.pack(pady=(0, 40))

        # Кнопки меню
        buttons = [
            ("Новая игра", self.start_new_game),
            ("Авторасстановка кораблей", self.auto_place_ships),
            ("Настройки", self.open_settings),
            ("Правила игры", self.show_rules),
            ("Выход", self.on_closing)
        ]

        for text, command in buttons:
            btn = tk.Button(
                menu_frame,
                text=text,
                font=("Arial", 16),
                bg=self.colors["water"],
                fg="white",
                activebackground="#3a76d8",
                activeforeground="white",
                width=25,
                height=2,
                cursor="hand2",
                command=command
            )
            btn.pack(pady=10)

    def clear_window(self):
        """Очистка окна от всех виджетов"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def start_new_game(self):
        """Начало новой игры"""
        self.clear_window()

        # Сброс состояния игры
        self.player_board = self.create_empty_board()
        self.computer_board = self.create_empty_board()
        self.player_target_board = self.create_empty_board()
        self.computer_target_board = self.create_empty_board()
        self.current_turn = "player"
        self.game_over = False
        self.ships_placed = False
        self.placement_mode = True
        self.current_ship_index = 0

        # Размещение кораблей компьютера
        self.place_computer_ships()

        # Создание интерфейса игры
        self.create_game_interface()

        # Начало размещения кораблей игрока
        self.start_ship_placement()

    def create_empty_board(self):
        """Создание пустой доски"""
        return [["~" for _ in range(self.board_size)] for _ in range(self.board_size)]

    def create_game_interface(self):
        """Создание игрового интерфейса"""
        # Фрейм для игровых досок
        boards_frame = tk.Frame(self.root, bg=self.colors["bg"])
        boards_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Доска игрока
        player_frame = tk.Frame(boards_frame, bg=self.colors["bg"])
        player_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        player_label = tk.Label(
            player_frame,
            text="Ваше поле",
            font=("Arial", 18, "bold"),
            fg=self.colors["text"],
            bg=self.colors["bg"]
        )
        player_label.pack(pady=(0, 10))

        self.player_canvas = tk.Canvas(
            player_frame,
            width=400,
            height=400,
            bg=self.colors["water"],
            highlightbackground=self.colors["grid"],
            highlightthickness=2
        )
        self.player_canvas.pack()
        self.draw_board(self.player_canvas, self.player_board, True)

        # Доска компьютера (целей)
        computer_frame = tk.Frame(boards_frame, bg=self.colors["bg"])
        computer_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        computer_label = tk.Label(
            computer_frame,
            text="Поле противника",
            font=("Arial", 18, "bold"),
            fg=self.colors["text"],
            bg=self.colors["bg"]
        )
        computer_label.pack(pady=(0, 10))

        self.computer_canvas = tk.Canvas(
            computer_frame,
            width=400,
            height=400,
            bg=self.colors["water"],
            highlightbackground=self.colors["grid"],
            highlightthickness=2
        )
        self.computer_canvas.pack()
        self.draw_board(self.computer_canvas, self.computer_target_board, False)

        # Панель статуса
        status_frame = tk.Frame(self.root, bg=self.colors["bg"])
        status_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.status_label = tk.Label(
            status_frame,
            text="Разместите ваш корабль (4 клетки)",
            font=("Arial", 14),
            fg=self.colors["text"],
            bg=self.colors["bg"]
        )
        self.status_label.pack(side="left", padx=(0, 20))

        # Кнопка поворота корабля
        rotate_btn = tk.Button(
            status_frame,
            text="Повернуть корабль",
            font=("Arial", 12),
            bg=self.colors["water"],
            fg="white",
            activebackground="#3a76d8",
            activeforeground="white",
            cursor="hand2",
            command=self.rotate_ship
        )
        rotate_btn.pack(side="left", padx=(0, 10))

        # Кнопка возврата в меню
        menu_btn = tk.Button(
            status_frame,
            text="В меню",
            font=("Arial", 12),
            bg="#95a5a6",
            fg="white",
            activebackground="#7f8c8d",
            activeforeground="white",
            cursor="hand2",
            command=self.create_main_menu
        )
        menu_btn.pack(side="right")

    def draw_board(self, canvas, board, is_player_board):
        """Отрисовка игровой доски на холсте"""
        canvas.delete("all")

        cell_size = 400 // self.board_size

        # Рисуем сетку
        for i in range(self.board_size + 1):
            # Вертикальные линии
            canvas.create_line(
                i * cell_size, 0, i * cell_size, 400,
                fill=self.colors["grid"], width=2
            )
            # Горизонтальные линии
            canvas.create_line(
                0, i * cell_size, 400, i * cell_size,
                fill=self.colors["grid"], width=2
            )

        # Рисуем содержимое клеток
        for row in range(self.board_size):
            for col in range(self.board_size):
                x1 = col * cell_size + 2
                y1 = row * cell_size + 2
                x2 = (col + 1) * cell_size - 2
                y2 = (row + 1) * cell_size - 2

                cell = board[row][col]

                if cell == "S":  # Корабль
                    canvas.create_rectangle(x1, y1, x2, y2, fill=self.colors["ship"], outline=self.colors["ship"])
                elif cell == "X":  # Попадание
                    canvas.create_rectangle(x1, y1, x2, y2, fill=self.colors["hit"], outline=self.colors["hit"])
                    # Крестик для попадания
                    canvas.create_line(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="white", width=3)
                    canvas.create_line(x2 - 5, y1 + 5, x1 + 5, y2 - 5, fill="white", width=3)
                elif cell == "O":  # Промах
                    canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill=self.colors["miss"],
                                       outline=self.colors["miss"])
                elif cell == "~":  # Вода
                    pass  # Оставляем цвет воды

        # Если это доска компьютера и игра началась, привязываем клики
        if not is_player_board and not self.placement_mode:
            canvas.bind("<Button-1>", self.player_fire)
        else:
            canvas.unbind("<Button-1>")

        # Если это доска игрока и мы в режиме размещения кораблей
        if is_player_board and self.placement_mode:
            canvas.bind("<Motion>", self.on_mouse_move)
            canvas.bind("<Button-1>", self.place_player_ship)

    def on_mouse_move(self, event):
        """Обработка движения мыши при размещении кораблей"""
        if not self.placement_mode or self.current_ship_index >= len(self.ships):
            return

        canvas = self.player_canvas
        cell_size = 400 // self.board_size
        col = event.x // cell_size
        row = event.y // cell_size

        # Очищаем предыдущий предпросмотр
        canvas.delete("preview")

        # Проверяем, можно ли разместить корабль в этой позиции
        ship_size = self.ships[self.current_ship_index]
        valid = self.can_place_ship(self.player_board, row, col, ship_size, self.current_ship_orientation)

        if 0 <= row < self.board_size and 0 <= col < self.board_size and valid:
            # Рисуем предпросмотр корабля
            if self.current_ship_orientation == "horizontal":
                for i in range(ship_size):
                    if col + i < self.board_size:
                        x1 = (col + i) * cell_size + 2
                        y1 = row * cell_size + 2
                        x2 = (col + i + 1) * cell_size - 2
                        y2 = (row + 1) * cell_size - 2
                        canvas.create_rectangle(x1, y1, x2, y2, fill=self.colors["ship"], outline=self.colors["ship"],
                                                tags="preview")
            else:  # vertical
                for i in range(ship_size):
                    if row + i < self.board_size:
                        x1 = col * cell_size + 2
                        y1 = (row + i) * cell_size + 2
                        x2 = (col + 1) * cell_size - 2
                        y2 = (row + i + 1) * cell_size - 2
                        canvas.create_rectangle(x1, y1, x2, y2, fill=self.colors["ship"], outline=self.colors["ship"],
                                                tags="preview")

    def can_place_ship(self, board, row, col, size, orientation):
        """Проверка, можно ли разместить корабль в указанной позиции"""
        if orientation == "horizontal":
            if col + size > self.board_size:
                return False
            for i in range(size):
                # Проверяем саму клетку и соседние
                for r in range(max(0, row - 1), min(self.board_size, row + 2)):
                    for c in range(max(0, col + i - 1), min(self.board_size, col + i + 2)):
                        if board[r][c] == "S":
                            return False
        else:  # vertical
            if row + size > self.board_size:
                return False
            for i in range(size):
                # Проверяем саму клетку и соседние
                for r in range(max(0, row + i - 1), min(self.board_size, row + i + 2)):
                    for c in range(max(0, col - 1), min(self.board_size, col + 2)):
                        if board[r][c] == "S":
                            return False
        return True

    def place_player_ship(self, event):
        """Размещение корабля игрока по клику"""
        if self.current_ship_index >= len(self.ships):
            return

        canvas = self.player_canvas
        cell_size = 400 // self.board_size
        col = event.x // cell_size
        row = event.y // cell_size

        ship_size = self.ships[self.current_ship_index]

        # Проверяем, можно ли разместить корабль
        if not self.can_place_ship(self.player_board, row, col, ship_size, self.current_ship_orientation):
            messagebox.showwarning("Невозможно разместить", "Корабль нельзя разместить в этой позиции!")
            return

        # Размещаем корабль
        if self.current_ship_orientation == "horizontal":
            for i in range(ship_size):
                self.player_board[row][col + i] = "S"
        else:  # vertical
            for i in range(ship_size):
                self.player_board[row + i][col] = "S"

        # Переходим к следующему кораблю
        self.current_ship_index += 1

        # Обновляем доску
        self.draw_board(self.player_canvas, self.player_board, True)

        # Обновляем статус
        if self.current_ship_index < len(self.ships):
            next_ship_size = self.ships[self.current_ship_index]
            self.status_label.config(text=f"Разместите ваш корабль ({next_ship_size} клетки)")
        else:
            # Все корабли размещены
            self.placement_mode = False
            self.ships_placed = True
            self.status_label.config(text="Все корабли размещены! Ваш ход. Кликайте по правому полю.")

            # Разблокируем доску компьютера для выстрелов
            self.draw_board(self.computer_canvas, self.computer_target_board, False)

    def rotate_ship(self):
        """Поворот корабля при размещении"""
        if self.current_ship_orientation == "horizontal":
            self.current_ship_orientation = "vertical"
        else:
            self.current_ship_orientation = "horizontal"

    def start_ship_placement(self):
        """Начало размещения кораблей"""
        self.status_label.config(text=f"Разместите ваш корабль ({self.ships[0]} клетки)")

    def auto_place_ships(self):
        """Автоматическая расстановка кораблей для игрока"""
        self.start_new_game()

        # Очищаем доску игрока
        self.player_board = self.create_empty_board()

        # Размещаем корабли случайным образом
        for ship_size in self.ships:
            placed = False
            attempts = 0

            while not placed and attempts < 100:
                orientation = random.choice(["horizontal", "vertical"])
                row = random.randint(0, self.board_size - 1)
                col = random.randint(0, self.board_size - 1)

                if orientation == "horizontal":
                    if col + ship_size > self.board_size:
                        attempts += 1
                        continue
                else:  # vertical
                    if row + ship_size > self.board_size:
                        attempts += 1
                        continue

                if self.can_place_ship(self.player_board, row, col, ship_size, orientation):
                    # Размещаем корабль
                    if orientation == "horizontal":
                        for i in range(ship_size):
                            self.player_board[row][col + i] = "S"
                    else:  # vertical
                        for i in range(ship_size):
                            self.player_board[row + i][col] = "S"
                    placed = True
                else:
                    attempts += 1

            if not placed:
                messagebox.showerror("Ошибка", "Не удалось автоматически разместить корабли. Попробуйте вручную.")
                return

        # Обновляем доску
        self.draw_board(self.player_canvas, self.player_board, True)

        # Завершаем размещение
        self.placement_mode = False
        self.ships_placed = True
        self.current_ship_index = len(self.ships)
        self.status_label.config(text="Все корабли размещены! Ваш ход. Кликайте по правому полю.")

        # Разблокируем доску компьютера для выстрелов
        self.draw_board(self.computer_canvas, self.computer_target_board, False)

    def place_computer_ships(self):
        """Размещение кораблей компьютера"""
        self.computer_board = self.create_empty_board()

        for ship_size in self.ships:
            placed = False
            attempts = 0

            while not placed and attempts < 100:
                orientation = random.choice(["horizontal", "vertical"])
                row = random.randint(0, self.board_size - 1)
                col = random.randint(0, self.board_size - 1)

                if orientation == "horizontal":
                    if col + ship_size > self.board_size:
                        attempts += 1
                        continue
                else:  # vertical
                    if row + ship_size > self.board_size:
                        attempts += 1
                        continue

                if self.can_place_ship(self.computer_board, row, col, ship_size, orientation):
                    # Размещаем корабль
                    if orientation == "horizontal":
                        for i in range(ship_size):
                            self.computer_board[row][col + i] = "S"
                    else:  # vertical
                        for i in range(ship_size):
                            self.computer_board[row + i][col] = "S"
                    placed = True
                else:
                    attempts += 1

    def player_fire(self, event):
        """Выстрел игрока по полю компьютера"""
        if self.game_over or not self.ships_placed or self.current_turn != "player":
            return

        canvas = self.computer_canvas
        cell_size = 400 // self.board_size
        col = event.x // cell_size
        row = event.y // cell_size

        # Проверяем, что выстрел в пределах доски
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return

        # Проверяем, что в эту клетку еще не стреляли
        if self.computer_target_board[row][col] != "~":
            return

        # Проверяем попадание
        if self.computer_board[row][col] == "S":
            # Попадание!
            self.computer_target_board[row][col] = "X"
            self.computer_board[row][col] = "X"
            self.status_label.config(text="Попадание! Стреляйте еще.")

            # Проверяем, потоплен ли корабль
            if self.is_ship_sunk(self.computer_board, row, col):
                self.status_label.config(text="Корабль потоплен! Стреляйте еще.")

            # Проверяем, выиграл ли игрок
            if self.check_win(self.computer_board):
                self.game_over = True
                messagebox.showinfo("Победа!", "Поздравляем! Вы потопили все корабли противника!")
                self.create_main_menu()
                return
        else:
            # Промах
            self.computer_target_board[row][col] = "O"
            self.status_label.config(text="Промах! Ход противника.")
            self.current_turn = "computer"
            self.root.after(1000, self.computer_turn)  # Компьютер делает ход через 1 секунду

        # Обновляем доски
        self.draw_board(self.computer_canvas, self.computer_target_board, False)
        self.draw_board(self.player_canvas, self.player_board, True)

    def computer_turn(self):
        """Ход компьютера"""
        if self.game_over or self.current_turn != "computer":
            return

        # Простая стратегия: случайный выстрел
        # Можно улучшить для более интеллектуальной игры

        # Сначала ищем раненый корабль, чтобы добить
        target = self.find_target()

        if target:
            row, col = target
        else:
            # Случайный выстрел
            row = random.randint(0, self.board_size - 1)
            col = random.randint(0, self.board_size - 1)

            # Проверяем, что в эту клетку еще не стреляли
            attempts = 0
            while self.player_target_board[row][col] != "~" and attempts < 100:
                row = random.randint(0, self.board_size - 1)
                col = random.randint(0, self.board_size - 1)
                attempts += 1

        # Проверяем попадание
        if self.player_board[row][col] == "S":
            # Попадание!
            self.player_target_board[row][col] = "X"
            self.player_board[row][col] = "X"

            # Проверяем, выиграл ли компьютер
            if self.check_win(self.player_board):
                self.game_over = True
                self.draw_board(self.player_canvas, self.player_board, True)
                messagebox.showinfo("Поражение", "Компьютер потопил все ваши корабли!")
                self.create_main_menu()
                return
        else:
            # Промах
            self.player_target_board[row][col] = "O"
            self.current_turn = "player"
            self.status_label.config(text="Противник промахнулся! Ваш ход.")

        # Обновляем доски
        self.draw_board(self.player_canvas, self.player_board, True)

        # Если компьютер попал, он ходит еще раз
        if self.current_turn == "computer":
            self.root.after(1000, self.computer_turn)

    def find_target(self):
        """Поиск цели для компьютера (раненый корабль)"""
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.player_target_board[row][col] == "X":
                    # Проверяем соседние клетки
                    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                    for dr, dc in directions:
                        new_row, new_col = row + dr, col + dc
                        if (0 <= new_row < self.board_size and
                                0 <= new_col < self.board_size and
                                self.player_target_board[new_row][new_col] == "~"):
                            return new_row, new_col
        return None

    def is_ship_sunk(self, board, row, col):
        """Проверка, потоплен ли корабль"""
        # Находим все клетки корабля
        ship_cells = []
        visited = set()

        def dfs(r, c):
            if (r, c) in visited:
                return
            visited.add((r, c))

            # Если это часть корабля
            if board[r][c] == "X":
                ship_cells.append((r, c))
                # Проверяем соседние клетки
                directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                for dr, dc in directions:
                    new_r, new_c = r + dr, c + dc
                    if 0 <= new_r < self.board_size and 0 <= new_c < self.board_size:
                        dfs(new_r, new_c)

        dfs(row, col)

        # Проверяем, все ли клетки корабля подбиты
        for r, c in ship_cells:
            if board[r][c] != "X":
                return False
        return len(ship_cells) > 0

    def check_win(self, board):
        """Проверка, все ли корабли потоплены"""
        for row in range(self.board_size):
            for col in range(self.board_size):
                if board[row][col] == "S":
                    return False
        return True

    def open_settings(self):
        """Открытие окна настроек"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки")
        settings_window.geometry("400x300")
        settings_window.configure(bg=self.colors["bg"])
        settings_window.resizable(False, False)

        # Центрируем окно
        settings_window.transient(self.root)
        settings_window.grab_set()

        # Заголовок
        title_label = tk.Label(
            settings_window,
            text="Настройки игры",
            font=("Arial", 18, "bold"),
            fg=self.colors["text"],
            bg=self.colors["bg"]
        )
        title_label.pack(pady=(20, 30))

        # Настройка размера доски
        size_frame = tk.Frame(settings_window, bg=self.colors["bg"])
        size_frame.pack(pady=(0, 20))

        size_label = tk.Label(
            size_frame,
            text="Размер доски:",
            font=("Arial", 12),
            fg=self.colors["text"],
            bg=self.colors["bg"]
        )
        size_label.pack(side="left", padx=(0, 10))

        size_var = tk.StringVar(value=str(self.board_size))
        size_spinbox = tk.Spinbox(
            size_frame,
            from_=6,
            to=15,
            textvariable=size_var,
            font=("Arial", 12),
            width=10
        )
        size_spinbox.pack(side="left")

        # Кнопки
        buttons_frame = tk.Frame(settings_window, bg=self.colors["bg"])
        buttons_frame.pack(pady=(20, 0))

        def save_settings():
            try:
                new_size = int(size_var.get())
                if 6 <= new_size <= 15:
                    self.board_size = new_size
                    messagebox.showinfo("Сохранено", "Настройки сохранены!")
                    settings_window.destroy()
                else:
                    messagebox.showerror("Ошибка", "Размер доски должен быть от 6 до 15!")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное число!")

        save_btn = tk.Button(
            buttons_frame,
            text="Сохранить",
            font=("Arial", 12),
            bg=self.colors["water"],
            fg="white",
            activebackground="#3a76d8",
            activeforeground="white",
            cursor="hand2",
            command=save_settings
        )
        save_btn.pack(side="left", padx=(0, 10))

        cancel_btn = tk.Button(
            buttons_frame,
            text="Отмена",
            font=("Arial", 12),
            bg="#95a5a6",
            fg="white",
            activebackground="#7f8c8d",
            activeforeground="white",
            cursor="hand2",
            command=settings_window.destroy
        )
        cancel_btn.pack(side="left")

        # Центрируем окно
        settings_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - settings_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - settings_window.winfo_height()) // 2
        settings_window.geometry(f"+{x}+{y}")

    def show_rules(self):
        """Показать правила игры"""
        rules_text = """
        ПРАВИЛА ИГРЫ "МОРСКОЙ БОЙ"

        1. Каждый игрок имеет флот из 10 кораблей:
           - 1 корабль размером 4 клетки
           - 2 корабля размером 3 клетки
           - 3 корабля размером 2 клетки
           - 4 корабля размером 1 клетка

        2. Корабли не могут соприкасаться друг с другом 
           даже углами.

        3. Игроки по очереди делают выстрелы, называя 
           координаты клетки на поле противника.

        4. Если выстрел попадает в корабль, игрок делает 
           еще один ход.

        5. Если выстрел не попадает в корабль, ход 
           переходит к противнику.

        6. Игра продолжается, пока все корабли одного из 
           игроков не будут потоплены.

        7. Побеждает игрок, первым потопивший все корабли 
           противника.
        """

        messagebox.showinfo("Правила игры", rules_text)

    def load_settings(self):
        """Загрузка настроек из файла"""
        try:
            if os.path.exists("battleship_settings.json"):
                with open("battleship_settings.json", "r") as f:
                    settings = json.load(f)
                    self.board_size = settings.get("board_size", 10)
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")

    def save_settings(self):
        """Сохранение настроек в файл"""
        try:
            settings = {
                "board_size": self.board_size
            }
            with open("battleship_settings.json", "w") as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")

    def on_closing(self):
        """Обработка закрытия окна"""
        self.save_settings()
        self.root.destroy()


def main():
    """Основная функция запуска игры"""
    try:
        root = tk.Tk()
        app = BattleshipGame(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Критическая ошибка", f"Произошла ошибка: {e}\nПрограмма будет закрыта.")
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()