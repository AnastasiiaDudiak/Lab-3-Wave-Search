import tkinter as tk
from tkinter import ttk
from collections import deque
import time
import random


# ============================================================
# ПОЧАТКОВІ ДАНІ
# ============================================================

DEFAULT_MAZE = [
    [0,  0,  0, -1,  0,  0,  0,  0,  0,  0],
    [-1, -1, 0, -1,  0, -1, -1, -1, -1, 0],
    [0,  0,  0,  0,  0,  0,  0,  0, -1, 0],
    [0, -1, -1, -1, -1, -1, -1,  0, -1, 0],
    [0,  0,  0,  0,  0,  0, -1,  0,  0,  0],
    [-1, -1, -1, -1, -1, 0, -1, -1, -1, 0],
    [0,  0,  0,  0, -1, 0,  0,  0,  0,  0],
    [0, -1, -1,  0, -1, -1, -1, -1, -1, 0],
    [0,  0, -1,  0,  0,  0,  0,  0, -1, 0],
    [-1, 0,  0,  0, -1, -1, -1,  0,  0,  0]
]

maze = [row[:] for row in DEFAULT_MAZE]

start = (0, 0)
goal = (9, 9)


# ============================================================
# ОПЕРАТОРИ ПЕРЕХОДУ
# ============================================================

ORTHOGONAL = [
    (-1, 0),   # вверх
    (1, 0),    # вниз
    (0, 1),    # вправо
    (0, -1)    # вліво
]

DIAGONAL = [
    (-1, -1),
    (-1, 1),
    (1, -1),
    (1, 1)
]

COMBINED = ORTHOGONAL + DIAGONAL


# ============================================================
# ХВИЛЬОВИЙ ПОШУК
# ============================================================

def wave_search(maze, start, goal, directions):
    rows = len(maze)
    cols = len(maze[0])

    wave = [
        [-1 for _ in range(cols)]
        for _ in range(rows)
    ]

    wave[start[0]][start[1]] = 0

    queue = deque([start])

    visited_order = []
    expanded_vertices = 0

    search_start = time.perf_counter()

    while queue:
        current = queue.popleft()

        expanded_vertices += 1
        visited_order.append(current)

        if current == goal:
            break

        row, col = current

        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc

            if (
                0 <= new_row < rows
                and 0 <= new_col < cols
            ):
                if (
                    maze[new_row][new_col] == 0
                    and wave[new_row][new_col] == -1
                ):
                    wave[new_row][new_col] = (
                        wave[row][col] + 1
                    )

                    queue.append(
                        (new_row, new_col)
                    )

    search_end = time.perf_counter()

    search_time = search_end - search_start

    if wave[goal[0]][goal[1]] != -1:
        wave_cycles = wave[goal[0]][goal[1]]

    else:
        values = [
            value
            for row in wave
            for value in row
            if value >= 0
        ]

        wave_cycles = max(values) if values else 0

    return (
        wave,
        visited_order,
        expanded_vertices,
        wave_cycles,
        search_time
    )


# ============================================================
# ВІДНОВЛЕННЯ НАЙКОРОТШОГО ШЛЯХУ
# ============================================================

def restore_path(wave, start, goal, directions):
    if wave[goal[0]][goal[1]] == -1:
        return []

    path = [goal]
    current = goal

    while current != start:
        row, col = current
        current_wave = wave[row][col]

        found = False

        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc

            if (
                0 <= new_row < len(wave)
                and 0 <= new_col < len(wave[0])
            ):
                if (
                    wave[new_row][new_col]
                    == current_wave - 1
                ):
                    current = (
                        new_row,
                        new_col
                    )

                    path.append(current)

                    found = True
                    break

        if not found:
            return []

    path.reverse()

    return path


# ============================================================
# ГРАФІЧНИЙ ІНТЕРФЕЙС
# ============================================================

CANVAS_SIZE = 600

root = tk.Tk()

root.title(
    "Однонаправлений хвильовий пошук"
)

root.geometry("1100x760")

root.resizable(False, False)


main_frame = ttk.Frame(
    root,
    padding=15
)

main_frame.pack(
    fill="both",
    expand=True
)


# ============================================================
# CANVAS
# ============================================================

canvas = tk.Canvas(
    main_frame,
    width=CANVAS_SIZE,
    height=CANVAS_SIZE,
    bg="white"
)

canvas.grid(
    row=0,
    column=0,
    rowspan=30,
    padx=(0, 25),
    sticky="n"
)


def get_cell_size():
    return CANVAS_SIZE / len(maze)


def draw_cell(
    row,
    col,
    state="initial",
    wave_value=None
):
    cell_size = get_cell_size()

    x1 = col * cell_size
    y1 = row * cell_size

    x2 = x1 + cell_size
    y2 = y1 + cell_size

    if maze[row][col] == -1:
        color = "black"
    else:
        color = "white"

    if state == "visited":
        color = "lightblue"

    elif state == "path":
        color = "gold"

    if (row, col) == start:
        color = "lightgreen"

    if (row, col) == goal:
        color = "tomato"

    canvas.create_rectangle(
        x1,
        y1,
        x2,
        y2,
        fill=color,
        outline="gray"
    )

    text = ""

    if (row, col) == start:
        text = "S"

    elif (row, col) == goal:
        text = "G"

    elif (
        wave_value is not None
        and state in ("visited", "path")
    ):
        text = str(wave_value)

    font_size = max(
        8,
        int(cell_size / 4)
    )

    canvas.create_text(
        x1 + cell_size / 2,
        y1 + cell_size / 2,
        text=text,
        font=("Arial", font_size, "bold")
    )


def draw_maze():
    canvas.delete("all")

    for row in range(len(maze)):
        for col in range(len(maze[0])):
            draw_cell(row, col)


# ============================================================
# РЕДАГУВАННЯ ЛАБІРИНТУ
# ============================================================

edit_mode = tk.StringVar(
    value="Стіна"
)


def edit_cell(event):
    global start, goal

    cell_size = get_cell_size()

    col = int(event.x / cell_size)
    row = int(event.y / cell_size)

    if (
        row < 0
        or row >= len(maze)
        or col < 0
        or col >= len(maze[0])
    ):
        return

    mode = edit_mode.get()

    if mode == "Стіна":

        if (
            (row, col) != start
            and (row, col) != goal
        ):
            maze[row][col] = -1

    elif mode == "Прохід":

        maze[row][col] = 0

    elif mode == "Старт":

        if (row, col) != goal:
            maze[row][col] = 0
            start = (row, col)

    elif mode == "Ціль":

        if (row, col) != start:
            maze[row][col] = 0
            goal = (row, col)

    draw_maze()

    result_label.config(
        text="Лабіринт змінено."
    )


canvas.bind(
    "<Button-1>",
    edit_cell
)


# ============================================================
# ЗАГОЛОВОК
# ============================================================

ttk.Label(
    main_frame,
    text="Параметри пошуку",
    font=("Arial", 16, "bold")
).grid(
    row=0,
    column=1,
    sticky="w",
    pady=(0, 8)
)


# ============================================================
# РОЗМІР ЛАБІРИНТУ
# ============================================================

ttk.Label(
    main_frame,
    text="Розмір лабіринту:"
).grid(
    row=1,
    column=1,
    sticky="w"
)


size_var = tk.StringVar(
    value="10 × 10"
)


size_box = ttk.Combobox(
    main_frame,
    textvariable=size_var,
    state="readonly",
    width=30
)

size_box["values"] = (
    "10 × 10",
    "15 × 15",
    "20 × 20"
)

size_box.grid(
    row=2,
    column=1,
    sticky="ew",
    pady=(3, 5)
)


def create_new_maze():
    global maze, start, goal

    selected = size_var.get()

    if selected == "10 × 10":
        size = 10

    elif selected == "15 × 15":
        size = 15

    else:
        size = 20

    maze = [
        [0 for _ in range(size)]
        for _ in range(size)
    ]

    start = (0, 0)
    goal = (size - 1, size - 1)

    draw_maze()

    result_label.config(
        text=(
            f"Створено новий лабіринт "
            f"{size} × {size}."
        )
    )


new_maze_button = ttk.Button(
    main_frame,
    text="Створити новий",
    command=create_new_maze
)

new_maze_button.grid(
    row=3,
    column=1,
    sticky="ew",
    pady=(0, 8)
)


# ============================================================
# ЧАСТКА НЕПРОХІДНИХ КЛІТИНОК
# ============================================================

ttk.Label(
    main_frame,
    text="Частка непрохідних клітинок:"
).grid(
    row=4,
    column=1,
    sticky="w"
)


wall_percent_var = tk.StringVar(
    value="30%"
)


wall_percent_box = ttk.Combobox(
    main_frame,
    textvariable=wall_percent_var,
    state="readonly",
    width=30
)

wall_percent_box["values"] = (
    "0%",
    "10%",
    "20%",
    "30%",
    "40%"
)

wall_percent_box.grid(
    row=5,
    column=1,
    sticky="ew",
    pady=(3, 5)
)


# ============================================================
# ГЕНЕРАЦІЯ ВИПАДКОВИХ СТІН
# ============================================================

def random_maze():
    global maze

    size = len(maze)

    wall_probability = (
        int(
            wall_percent_var.get().replace("%", "")
        ) / 100
    )

    for row in range(size):
        for col in range(size):

            # Старт і ціль не можуть бути стінами
            if (
                (row, col) == start
                or (row, col) == goal
            ):
                maze[row][col] = 0
                continue

            if random.random() < wall_probability:
                maze[row][col] = -1

            else:
                maze[row][col] = 0

    draw_maze()

    # Рахуємо фактичну кількість стін
    total_cells = size * size

    wall_count = sum(
        1
        for row in maze
        for cell in row
        if cell == -1
    )

    actual_percent = (
        wall_count / total_cells
    ) * 100

    result_label.config(
        text=(
            "Створено випадковий лабіринт.\n"
            f"Задана частка стін: "
            f"{wall_percent_var.get()}\n"
            f"Фактична частка стін: "
            f"{actual_percent:.1f}%"
        )
    )


random_button = ttk.Button(
    main_frame,
    text="Згенерувати стіни",
    command=random_maze
)

random_button.grid(
    row=6,
    column=1,
    sticky="ew",
    pady=(0, 8)
)


# ============================================================
# РЕДАГУВАННЯ КЛІТИНКИ
# ============================================================

ttk.Label(
    main_frame,
    text="Редагування клітинки:"
).grid(
    row=7,
    column=1,
    sticky="w"
)


edit_box = ttk.Combobox(
    main_frame,
    textvariable=edit_mode,
    state="readonly",
    width=30
)

edit_box["values"] = (
    "Стіна",
    "Прохід",
    "Старт",
    "Ціль"
)

edit_box.grid(
    row=8,
    column=1,
    sticky="ew",
    pady=(3, 8)
)


# ============================================================
# ОПЕРАТОР ПЕРЕХОДУ
# ============================================================

ttk.Label(
    main_frame,
    text="Оператор переходу:"
).grid(
    row=9,
    column=1,
    sticky="w"
)


operator_var = tk.StringVar(
    value="Вверх-вниз-вправо-вліво"
)


operator_box = ttk.Combobox(
    main_frame,
    textvariable=operator_var,
    state="readonly",
    width=30
)

operator_box["values"] = (
    "Вверх-вниз-вправо-вліво",
    "Перехід по діагоналях",
    "Комбінований оператор"
)

operator_box.grid(
    row=10,
    column=1,
    sticky="ew",
    pady=(3, 8)
)


# ============================================================
# ЗАТРИМКА АНІМАЦІЇ
# ============================================================

ttk.Label(
    main_frame,
    text="Затримка анімації:"
).grid(
    row=11,
    column=1,
    sticky="w"
)


delay_var = tk.IntVar(
    value=100
)


delay_scale = tk.Scale(
    main_frame,
    from_=20,
    to=500,
    orient="horizontal",
    variable=delay_var,
    length=280,
    resolution=20
)

delay_scale.grid(
    row=12,
    column=1,
    sticky="w"
)


ttk.Label(
    main_frame,
    text="20 мс — швидко     500 мс — повільно"
).grid(
    row=13,
    column=1,
    sticky="w",
    pady=(0, 8)
)


# ============================================================
# АНІМАЦІЯ
# ============================================================

animation_data = {}


def animate_search(index=0):
    visited = animation_data["visited"]
    wave = animation_data["wave"]

    if index < len(visited):

        row, col = visited[index]

        draw_cell(
            row,
            col,
            "visited",
            wave[row][col]
        )

        root.after(
            delay_var.get(),
            lambda: animate_search(index + 1)
        )

    else:
        animate_path(0)


def animate_path(index=0):
    path = animation_data["path"]
    wave = animation_data["wave"]

    if index < len(path):

        row, col = path[index]

        draw_cell(
            row,
            col,
            "path",
            wave[row][col]
        )

        root.after(
            40,
            lambda: animate_path(index + 1)
        )

    else:
        show_results()


# ============================================================
# РЕЗУЛЬТАТ ПОШУКУ
# ============================================================

def show_results():
    path = animation_data["path"]

    expanded = animation_data["expanded"]
    cycles = animation_data["cycles"]
    search_time = animation_data["time"]

    size = len(maze)

    total_cells = size * size

    wall_count = sum(
        1
        for row in maze
        for cell in row
        if cell == -1
    )

    actual_percent = (
        wall_count / total_cells
    ) * 100

    if path:

        text = (
            "Шлях знайдено.\n\n"
            f"Довжина шляху: {len(path) - 1}\n"
            f"Вершин у шляху: {len(path)}\n"
            f"Циклів хвилі: {cycles}\n"
            f"Розкритих вершин: {expanded}\n"
            f"Частка стін: {actual_percent:.1f}%\n"
            f"Час пошуку: {search_time:.8f} с"
        )

    else:

        text = (
            "Шлях не знайдено.\n\n"
            f"Циклів хвилі: {cycles}\n"
            f"Розкритих вершин: {expanded}\n"
            f"Частка стін: {actual_percent:.1f}%\n"
            f"Час пошуку: {search_time:.8f} с"
        )

    result_label.config(
        text=text
    )

    search_button.config(
        state="normal"
    )


# ============================================================
# ЗАПУСК ПОШУКУ
# ============================================================

def start_search():
    draw_maze()

    result_label.config(
        text="Виконується пошук..."
    )

    selected = operator_var.get()

    if selected == "Вверх-вниз-вправо-вліво":
        directions = ORTHOGONAL

    elif selected == "Перехід по діагоналях":
        directions = DIAGONAL

    else:
        directions = COMBINED

    (
        wave,
        visited,
        expanded,
        cycles,
        search_time
    ) = wave_search(
        maze,
        start,
        goal,
        directions
    )

    path = restore_path(
        wave,
        start,
        goal,
        directions
    )

    animation_data["wave"] = wave
    animation_data["visited"] = visited
    animation_data["path"] = path
    animation_data["expanded"] = expanded
    animation_data["cycles"] = cycles
    animation_data["time"] = search_time

    search_button.config(
        state="disabled"
    )

    animate_search()


search_button = ttk.Button(
    main_frame,
    text="Запустити пошук",
    command=start_search
)

search_button.grid(
    row=14,
    column=1,
    sticky="ew",
    pady=5
)


# ============================================================
# СКИДАННЯ РЕЗУЛЬТАТУ
# ============================================================

def reset_search():
    draw_maze()

    result_label.config(
        text="Пошук ще не виконувався."
    )


reset_button = ttk.Button(
    main_frame,
    text="Скинути результат",
    command=reset_search
)

reset_button.grid(
    row=15,
    column=1,
    sticky="ew",
    pady=5
)


# ============================================================
# РЕЗУЛЬТАТИ
# ============================================================

ttk.Label(
    main_frame,
    text="Результати",
    font=("Arial", 14, "bold")
).grid(
    row=16,
    column=1,
    sticky="w",
    pady=(10, 5)
)


result_label = ttk.Label(
    main_frame,
    text="Пошук ще не виконувався.",
    justify="left",
    wraplength=320
)

result_label.grid(
    row=17,
    column=1,
    sticky="w"
)


# ============================================================
# ПОЧАТКОВИЙ ЛАБІРИНТ
# ============================================================

def restore_default():
    global maze, start, goal

    maze = [
        row[:]
        for row in DEFAULT_MAZE
    ]

    start = (0, 0)
    goal = (9, 9)

    size_var.set("10 × 10")

    draw_maze()

    result_label.config(
        text="Початковий лабіринт відновлено."
    )


default_button = ttk.Button(
    main_frame,
    text="Початковий лабіринт",
    command=restore_default
)

default_button.grid(
    row=18,
    column=1,
    sticky="ew",
    pady=(10, 5)
)


# ============================================================
# ЗАПУСК ПРОГРАМИ
# ============================================================

draw_maze()

root.mainloop()