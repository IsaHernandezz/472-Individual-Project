import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk


file_path = "C:/Users/ihern/OneDrive/Desktop/Fantasy Football.xlsx"
xls = pd.ExcelFile(file_path)
sheets = xls.sheet_names
data = xls.parse("Overall")


root = tk.Tk()
root.title("Fantasy Football Draft Assistant")
root.geometry("1000x600")
root.configure(bg="#e8f4f8")


try:
    icon_img = Image.open("football_icon.png").resize((30, 30))
    icon = ImageTk.PhotoImage(icon_img)
except Exception:
    icon = None


title_frame = tk.Frame(root, bg="#e8f4f8")
title_frame.pack(pady=10)

if icon:
    icon_label = tk.Label(title_frame, image=icon, bg="#e8f4f8")
    icon_label.pack(side="left", padx=(10, 5))

title_label = tk.Label(title_frame, text="Fantasy Football Draft Assistant", font=("Arial", 16, "bold"), bg="#e8f4f8")
title_label.pack(side="left")


dropdown_frame = tk.Frame(root, bg="#e8f4f8")
dropdown_frame.pack(pady=5)

if icon:
    dropdown_icon = tk.Label(dropdown_frame, image=icon, bg="#e8f4f8")
    dropdown_icon.pack(side="left", padx=(5, 10))

sheet_var = tk.StringVar(value="Overall")
sheet_dropdown = ttk.Combobox(dropdown_frame, textvariable=sheet_var, values=sheets)
sheet_dropdown.pack(side="left")


status_label = tk.Label(root, text="Sheet loaded: Overall", font=("Arial", 10), bg="#e8f4f8")
status_label.pack(pady=(5, 0))


tree_frame = tk.Frame(root)
tree_frame.pack(expand=True, fill='both', padx=10, pady=10)

tree_scroll = tk.Scrollbar(tree_frame)
tree_scroll.pack(side='right', fill='y')

tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set)
tree.pack(expand=True, fill='both')
tree_scroll.config(command=tree.yview)

# === Buttons Frame ===
nav_frame = tk.Frame(root, bg="#e8f4f8")
nav_frame.pack(pady=10)


current_index = 0
best_available_stack = []
taken_players = set()




def update_table(df):
    tree.delete(*tree.get_children())
    tree["columns"] = list(df.columns)
    tree["show"] = "headings"

    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')

    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    status_label.config(text=f"Displaying {len(df)} players from '{sheet_var.get()}'")


def on_sheet_change(event=None):
    global current_index, best_available_stack, taken_players
    try:
        sheet = sheet_var.get()
        df = xls.parse(sheet)
        update_table(df)
        current_index = 0
        best_available_stack.clear()
        taken_players.clear()
        status_label.config(text=f"Sheet loaded: {sheet}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load sheet: {e}")


def sort_by_rank():
    try:
        df = xls.parse(sheet_var.get())
        df_sorted = df.sort_values("RK")
        update_table(df_sorted)
        status_label.config(text=f"Sorted by RK: {sheet_var.get()}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not sort by RK: {e}")


def highlight_next_best():
    global current_index
    try:
        sorted_df = xls.parse(sheet_var.get()).sort_values("RK").reset_index(drop=True)
    except Exception as e:
        messagebox.showerror("Error", f"Could not load or sort sheet: {e}")
        return


    while current_index < len(sorted_df) and sorted_df.loc[current_index, "PLAYER NAME"] in taken_players:
        current_index += 1

    if current_index >= len(sorted_df):
        messagebox.showinfo("End", "No more available players.")
        return

    player_name = sorted_df.loc[current_index, "PLAYER NAME"]
    best_available_stack.append(current_index)


    for item in tree.get_children():
        values = tree.item(item, "values")
        if values and player_name in values:
            tree.selection_set(item)
            tree.see(item)
            break

    taken_players.add(player_name)
    current_index += 1


def undo_last():
    global current_index
    if not best_available_stack:
        messagebox.showinfo("Undo", "No previous selection to undo.")
        return

    current_index = best_available_stack.pop()
    try:
        sorted_df = xls.parse(sheet_var.get()).sort_values("RK").reset_index(drop=True)
    except Exception as e:
        messagebox.showerror("Error", f"Could not load or sort sheet: {e}")
        return

    player_name = sorted_df.loc[current_index, "PLAYER NAME"]
    taken_players.discard(player_name)

    for item in tree.get_children():
        values = tree.item(item, "values")
        if values and player_name in values:
            tree.selection_set(item)
            tree.see(item)
            break



sort_button = tk.Button(nav_frame, text="Sort by Rank", command=sort_by_rank, bg="#1abc9c", fg="white", padx=10, pady=5)
sort_button.pack(side="left", padx=5)

next_button = tk.Button(nav_frame, text="Next Best", command=highlight_next_best, bg="#3498db", fg="white", padx=10, pady=5)
next_button.pack(side="left", padx=5)

undo_button = tk.Button(nav_frame, text="Undo", command=undo_last, bg="#e74c3c", fg="white", padx=10, pady=5)
undo_button.pack(side="left", padx=5)


sheet_dropdown.bind("<<ComboboxSelected>>", on_sheet_change)


update_table(data)


root.mainloop()


