import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ==================== DATABASE SETUP ====================
def init_db():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS books 
                 (id INTEGER PRIMARY KEY, title TEXT, author TEXT, 
                  category TEXT, quantity INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS issued 
                 (id INTEGER PRIMARY KEY, book_id INTEGER, student_name TEXT, 
                  issue_date TEXT, return_date TEXT)''')
    conn.commit()
    conn.close()

# ==================== MAIN WINDOW ====================
root = tk.Tk()
root.title("📚 Library Management System - Kishan")
root.geometry("1200x750")
root.configure(bg="#f4f6f9")

init_db()

# Style Configuration
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", rowheight=25, font=("Arial", 10))
style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

# ==================== GLOBAL VARIABLES ====================
current_book_id = None

# ==================== HELPER FUNCTIONS ====================
def clear_entries():
    entry_title.delete(0, tk.END)
    entry_author.delete(0, tk.END)
    entry_category.delete(0, tk.END)
    entry_qty.delete(0, tk.END)
    entry_student.delete(0, tk.END)
    global current_book_id
    current_book_id = None
    btn_add.config(text="➕ Add Book", command=add_book)

def refresh_table():
    for item in tree.get_children():
        tree.delete(item)
    
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("SELECT * FROM books ORDER BY title")
    for row in c.fetchall():
        tree.insert("", tk.END, values=row)
    conn.close()

# ==================== CRUD OPERATIONS ====================
def add_book():
    title = entry_title.get().strip()
    author = entry_author.get().strip()
    category = entry_category.get().strip()
    qty = entry_qty.get().strip()

    if not title or not author or not qty:
        messagebox.showwarning("Missing Fields", "Book Title, Author, and Quantity are mandatory!")
        return

    try:
        qty = int(qty)
        if qty < 1:
            raise ValueError
    except:
        messagebox.showerror("Invalid Input", "Quantity must be a positive number!")
        return

    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("INSERT INTO books (title, author, category, quantity) VALUES (?, ?, ?, ?)",
              (title, author, category, qty))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Book Added Successfully! ✅")
    clear_entries()
    refresh_table()

def update_book():
    global current_book_id
    if not current_book_id:
        messagebox.showwarning("Error", "Please select a book to update!")
        return

    title = entry_title.get().strip()
    author = entry_author.get().strip()
    category = entry_category.get().strip()
    qty = entry_qty.get().strip()

    if not title or not author or not qty:
        messagebox.showwarning("Missing Fields", "Title, Author, and Quantity are mandatory!")
        return

    try:
        qty = int(qty)
    except:
        messagebox.showerror("Invalid Input", "Quantity must be a number!")
        return

    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("""UPDATE books SET title=?, author=?, category=?, quantity=? 
                 WHERE id=?""", (title, author, category, qty, current_book_id))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Book Updated Successfully! ✅")
    clear_entries()
    refresh_table()

def delete_book():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Error", "Please select a book to delete!")
        return

    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this book?"):
        book_id = tree.item(selected[0])['values'][0]
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute("DELETE FROM books WHERE id=?", (book_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Book Deleted Successfully!")
        refresh_table()

def search_books():
    query = entry_search.get().strip().lower()
    for item in tree.get_children():
        tree.delete(item)

    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("""SELECT * FROM books WHERE 
                 LOWER(title) LIKE ? OR LOWER(author) LIKE ? OR LOWER(category) LIKE ?""",
              (f"%{query}%", f"%{query}%", f"%{query}%"))
    for row in c.fetchall():
        tree.insert("", tk.END, values=row)
    conn.close()

# ==================== ISSUE & RETURN ====================
def issue_book():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Error", "Please select a book first!")
        return

    student = entry_student.get().strip()
    if not student:
        messagebox.showwarning("Error", "Please enter Student Name!")
        return

    book_id = tree.item(selected[0])['values'][0]
    current_qty = tree.item(selected[0])['values'][4]

    if current_qty <= 0:
        messagebox.showerror("Out of Stock", "This book is currently out of stock!")
        return

    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("UPDATE books SET quantity = quantity - 1 WHERE id=?", (book_id,))
    c.execute("INSERT INTO issued (book_id, student_name, issue_date) VALUES (?, ?, ?)",
              (book_id, student, datetime.now().strftime("%d-%m-%Y")))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", f"Book issued to {student} ✅")
    clear_entries()
    refresh_table()

def return_book():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Error", "Please select a book!")
        return

    book_id = tree.item(selected[0])['values'][0]
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("UPDATE books SET quantity = quantity + 1 WHERE id=?", (book_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Book Returned Successfully!")
    refresh_table()

# ==================== LOAD SELECTED BOOK FOR EDIT ====================
def on_tree_double_click(event):
    global current_book_id
    selected = tree.selection()
    if selected:
        values = tree.item(selected[0])['values']
        current_book_id = values[0]
        
        clear_entries()
        entry_title.insert(0, values[1])
        entry_author.insert(0, values[2])
        entry_category.insert(0, values[3] if values[3] else "")
        entry_qty.insert(0, values[4])
        
        btn_add.config(text="💾 Update Book", command=update_book)

# ==================== UI DESIGN ====================
# Header
header = tk.Label(root, text="📚 Library Management System", 
                  font=("Arial", 24, "bold"), bg="#f4f6f9", fg="#1e3a8a")
header.pack(pady=15)

# Search Frame
search_frame = tk.Frame(root, bg="#f4f6f9")
search_frame.pack(pady=8, fill="x", padx=20)

tk.Label(search_frame, text="🔍 Search:", font=("Arial", 11), bg="#f4f6f9").pack(side="left")
entry_search = tk.Entry(search_frame, width=40, font=("Arial", 11))
entry_search.pack(side="left", padx=8)
tk.Button(search_frame, text="Search", command=search_books, bg="#3b82f6", fg="white", 
          font=("Arial", 10, "bold")).pack(side="left")
tk.Button(search_frame, text="Clear", command=lambda: (entry_search.delete(0, tk.END), refresh_table()),
          bg="#64748b", fg="white", font=("Arial", 10)).pack(side="left", padx=5)

# Input Fields Frame
input_frame = tk.LabelFrame(root, text=" Book Details ", font=("Arial", 12, "bold"), 
                           bg="#f4f6f9", padx=15, pady=15)
input_frame.pack(pady=10, padx=20, fill="x")

# Row 1
tk.Label(input_frame, text="Book Title*:", font=("Arial", 10)).grid(row=0, column=0, sticky="e", pady=6, padx=8)
entry_title = tk.Entry(input_frame, width=35, font=("Arial", 10))
entry_title.grid(row=0, column=1, pady=6, padx=8)

tk.Label(input_frame, text="Author*:", font=("Arial", 10)).grid(row=0, column=2, sticky="e", pady=6, padx=8)
entry_author = tk.Entry(input_frame, width=35, font=("Arial", 10))
entry_author.grid(row=0, column=3, pady=6, padx=8)

# Row 2
tk.Label(input_frame, text="Category:", font=("Arial", 10)).grid(row=1, column=0, sticky="e", pady=6, padx=8)
entry_category = tk.Entry(input_frame, width=35, font=("Arial", 10))
entry_category.grid(row=1, column=1, pady=6, padx=8)

tk.Label(input_frame, text="Quantity*:", font=("Arial", 10)).grid(row=1, column=2, sticky="e", pady=6, padx=8)
entry_qty = tk.Entry(input_frame, width=35, font=("Arial", 10))
entry_qty.grid(row=1, column=3, pady=6, padx=8)

# Buttons
btn_frame = tk.Frame(input_frame, bg="#f4f6f9")
btn_frame.grid(row=2, column=0, columnspan=4, pady=12)

btn_add = tk.Button(btn_frame, text="➕ Add Book", command=add_book, bg="#22c55e", fg="white", 
                    font=("Arial", 10, "bold"), width=18, height=2)
btn_add.pack(side="left", padx=8)

tk.Button(btn_frame, text="🗑 Delete Book", command=delete_book, bg="#ef4444", fg="white", 
          font=("Arial", 10, "bold"), width=18, height=2).pack(side="left", padx=8)

tk.Button(btn_frame, text="📖 Issue Book", command=issue_book, bg="#3b82f6", fg="white", 
          font=("Arial", 10, "bold"), width=18, height=2).pack(side="left", padx=8)

tk.Button(btn_frame, text="↩ Return Book", command=return_book, bg="#eab308", fg="black", 
          font=("Arial", 10, "bold"), width=18, height=2).pack(side="left", padx=8)

# Student Name
tk.Label(input_frame, text="Student Name:", font=("Arial", 10), bg="#f4f6f9").grid(row=3, column=0, sticky="e", pady=8, padx=8)
entry_student = tk.Entry(input_frame, width=35, font=("Arial", 10))
entry_student.grid(row=3, column=1, pady=8, padx=8, sticky="w")

# Books Table
tree_frame = tk.LabelFrame(root, text=" Books Inventory ", font=("Arial", 12, "bold"), bg="#f4f6f9")
tree_frame.pack(pady=10, padx=20, fill="both", expand=True)

columns = ("ID", "Title", "Author", "Category", "Quantity")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=180 if col != "Title" else 280)

tree.pack(pady=10, padx=10, fill="both", expand=True)

# Bind double click
tree.bind("<Double-1>", on_tree_double_click)

# Refresh Button
tk.Button(root, text="🔄 Refresh List", command=refresh_table, bg="#64748b", fg="white", 
          font=("Arial", 10, "bold"), width=20).pack(pady=8)

# Load initial data
refresh_table()

root.mainloop()