#!/usr/bin/env python3
"""
Aplikasi Perpustakaan sederhana (Tkinter + SQLite)
Simpan file sebagai library_app.py dan jalankan: python library_app.py
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

DB_FILE = "library.db"

# ----- Database helpers -----
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT,
        year INTEGER,
        isbn TEXT,
        status TEXT DEFAULT 'available', -- 'available' or 'borrowed'
        borrower TEXT,
        borrowed_date TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_book(title, author, year, isbn):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO books (title, author, year, isbn) VALUES (?, ?, ?, ?)",
              (title, author, year or None, isbn))
    conn.commit()
    conn.close()

def update_book(book_id, title, author, year, isbn):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE books SET title=?, author=?, year=?, isbn=? WHERE id=?",
              (title, author, year or None, isbn, book_id))
    conn.commit()
    conn.close()

def delete_book(book_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()

def list_books(filter_sql=None, params=()):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    base = "SELECT id, title, author, year, isbn, status, borrower, borrowed_date FROM books"
    if filter_sql:
        base += " WHERE " + filter_sql
    base += " ORDER BY title COLLATE NOCASE"
    c.execute(base, params)
    rows = c.fetchall()
    conn.close()
    return rows

def borrow_book(book_id, borrower_name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    now = datetime.now().isoformat(timespec='seconds')
    c.execute("UPDATE books SET status='borrowed', borrower=?, borrowed_date=? WHERE id=?",
              (borrower_name, now, book_id))
    conn.commit()
    conn.close()

def return_book(book_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE books SET status='available', borrower=NULL, borrowed_date=NULL WHERE id=?",
              (book_id,))
    conn.commit()
    conn.close()

# ----- GUI -----
class LibraryApp:
    def __init__(self, root):
        self.root = root
        root.title("Aplikasi Perpustakaan - Tkinter + SQLite")
        root.geometry("850x500")

        # Top frame: Form input
        frm = tk.Frame(root, pady=8)
        frm.pack(fill=tk.X)

        tk.Label(frm, text="Judul").grid(row=0, column=0, sticky=tk.W)
        tk.Label(frm, text="Penulis").grid(row=0, column=2, sticky=tk.W)
        tk.Label(frm, text="Tahun").grid(row=1, column=0, sticky=tk.W)
        tk.Label(frm, text="ISBN").grid(row=1, column=2, sticky=tk.W)

        self.e_title = tk.Entry(frm, width=30)
        self.e_author = tk.Entry(frm, width=30)
        self.e_year = tk.Entry(frm, width=15)
        self.e_isbn = tk.Entry(frm, width=20)

        self.e_title.grid(row=0, column=1, padx=4, pady=2)
        self.e_author.grid(row=0, column=3, padx=4, pady=2)
        self.e_year.grid(row=1, column=1, padx=4, pady=2, sticky=tk.W)
        self.e_isbn.grid(row=1, column=3, padx=4, pady=2, sticky=tk.W)

        # Buttons
        btn_frame = tk.Frame(frm)
        btn_frame.grid(row=0, column=4, rowspan=2, padx=10)

        tk.Button(btn_frame, text="Tambah Buku", width=14, command=self.on_add).pack(pady=2)
        tk.Button(btn_frame, text="Edit Buku", width=14, command=self.on_edit).pack(pady=2)
        tk.Button(btn_frame, text="Hapus Buku", width=14, command=self.on_delete).pack(pady=2)
        tk.Button(btn_frame, text="Segarkan Daftar", width=14, command=self.refresh).pack(pady=2)

        # Search
        search_frame = tk.Frame(root, pady=6)
        search_frame.pack(fill=tk.X)
        tk.Label(search_frame, text="Cari (judul / penulis / isbn):").pack(side=tk.LEFT, padx=4)
        self.e_search = tk.Entry(search_frame, width=40)
        self.e_search.pack(side=tk.LEFT, padx=4)
        tk.Button(search_frame, text="Cari", command=self.on_search).pack(side=tk.LEFT, padx=4)
        tk.Button(search_frame, text="Tampilkan Semua", command=self.refresh).pack(side=tk.LEFT, padx=4)

        # Treeview (table)
        cols = ("id", "title", "author", "year", "isbn", "status", "borrower", "borrowed_date")
        self.tree = ttk.Treeview(root, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("id", text="ID"); self.tree.column("id", width=40, anchor=tk.CENTER)
        self.tree.heading("title", text="Judul"); self.tree.column("title", width=250)
        self.tree.heading("author", text="Penulis"); self.tree.column("author", width=140)
        self.tree.heading("year", text="Tahun"); self.tree.column("year", width=60, anchor=tk.CENTER)
        self.tree.heading("isbn", text="ISBN"); self.tree.column("isbn", width=110)
        self.tree.heading("status", text="Status"); self.tree.column("status", width=80, anchor=tk.CENTER)
        self.tree.heading("borrower", text="Peminjam"); self.tree.column("borrower", width=120)
        self.tree.heading("borrowed_date", text="Tgl Pinjam"); self.tree.column("borrowed_date", width=130)

        vsb = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Bottom action buttons for borrow/return
        bottom = tk.Frame(root, pady=6)
        bottom.pack(fill=tk.X)
        tk.Button(bottom, text="Pinjam Buku", command=self.on_borrow).pack(side=tk.LEFT, padx=6)
        tk.Button(bottom, text="Kembalikan Buku", command=self.on_return).pack(side=tk.LEFT, padx=6)
        tk.Button(bottom, text="Detail Buku", command=self.on_detail).pack(side=tk.LEFT, padx=6)

        # Bind double-click to edit
        self.tree.bind("<Double-1>", lambda e: self.on_edit())

        # initial load
        self.refresh()

    def clear_form(self):
        self.e_title.delete(0, tk.END)
        self.e_author.delete(0, tk.END)
        self.e_year.delete(0, tk.END)
        self.e_isbn.delete(0, tk.END)

    def on_add(self):
        title = self.e_title.get().strip()
        if not title:
            messagebox.showwarning("Validasi", "Judul wajib diisi.")
            return
        author = self.e_author.get().strip()
        year_text = self.e_year.get().strip()
        year = int(year_text) if year_text.isdigit() else None
        isbn = self.e_isbn.get().strip()
        add_book(title, author, year, isbn)
        self.clear_form()
        self.refresh()

    def get_selected(self):
        sel = self.tree.selection()
        if not sel:
            return None
        values = self.tree.item(sel[0], "values")
        # values: id, title, author, year, isbn, status, borrower, borrowed_date
        return values

    def on_edit(self):
        sel = self.get_selected()
        if not sel:
            messagebox.showinfo("Info", "Pilih buku yang ingin diedit.")
            return
        book_id = sel[0]
        # open a simple dialog to edit fields
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit Buku")
        tk.Label(edit_win, text="Judul").grid(row=0, column=0, sticky=tk.W, padx=6, pady=4)
        tk.Label(edit_win, text="Penulis").grid(row=1, column=0, sticky=tk.W, padx=6, pady=4)
        tk.Label(edit_win, text="Tahun").grid(row=2, column=0, sticky=tk.W, padx=6, pady=4)
        tk.Label(edit_win, text="ISBN").grid(row=3, column=0, sticky=tk.W, padx=6, pady=4)

        e_t = tk.Entry(edit_win, width=40); e_t.grid(row=0, column=1, padx=6, pady=4)
        e_a = tk.Entry(edit_win, width=40); e_a.grid(row=1, column=1, padx=6, pady=4)
        e_y = tk.Entry(edit_win, width=15); e_y.grid(row=2, column=1, padx=6, pady=4, sticky=tk.W)
        e_i = tk.Entry(edit_win, width=25); e_i.grid(row=3, column=1, padx=6, pady=4, sticky=tk.W)

        e_t.insert(0, sel[1])
        e_a.insert(0, sel[2])
        e_y.insert(0, sel[3] or "")
        e_i.insert(0, sel[4] or "")

        def save_changes():
            title = e_t.get().strip()
            if not title:
                messagebox.showwarning("Validasi", "Judul wajib diisi.")
                return
            author = e_a.get().strip()
            y = e_y.get().strip()
            year = int(y) if y.isdigit() else None
            isbn = e_i.get().strip()
            update_book(book_id, title, author, year, isbn)
            edit_win.destroy()
            self.refresh()

        tk.Button(edit_win, text="Simpan", command=save_changes).grid(row=4, column=0, columnspan=2, pady=8)

    def on_delete(self):
        sel = self.get_selected()
        if not sel:
            messagebox.showinfo("Info", "Pilih buku untuk dihapus.")
            return
        book_id, title = sel[0], sel[1]
        if messagebox.askyesno("Konfirmasi", f"Hapus buku: '{title}'?"):
            delete_book(book_id)
            self.refresh()

    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = list_books()
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def on_search(self):
        q = self.e_search.get().strip()
        if not q:
            self.refresh()
            return
        pattern = f"%{q}%"
        rows = list_books("title LIKE ? OR author LIKE ? OR isbn LIKE ?", (pattern, pattern, pattern))
        for r in self.tree.get_children():
            self.tree.delete(r)
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def on_borrow(self):
        sel = self.get_selected()
        if not sel:
            messagebox.showinfo("Info", "Pilih buku untuk dipinjam.")
            return
        book_id, title, _, _, _, status = sel[0], sel[1], sel[2], sel[3], sel[4], sel[5]
        if status == "borrowed":
            messagebox.showinfo("Info", "Buku ini sedang dipinjam.")
            return
        borrower = simpledialog.askstring("Peminjam", "Masukkan nama peminjam:")
        if borrower:
            borrow_book(book_id, borrower.strip())
            self.refresh()

    def on_return(self):
        sel = self.get_selected()
        if not sel:
            messagebox.showinfo("Info", "Pilih buku untuk dikembalikan.")
            return
        book_id, title, _, _, _, status = sel[0], sel[1], sel[2], sel[3], sel[4], sel[5]
        if status != "borrowed":
            messagebox.showinfo("Info", "Buku ini belum dipinjam.")
            return
        if messagebox.askyesno("Konfirmasi", f"Kembalikan buku '{title}'?"):
            return_book(book_id)
            self.refresh()

    def on_detail(self):
        sel = self.get_selected()
        if not sel:
            messagebox.showinfo("Info", "Pilih buku untuk melihat detail.")
            return
        book_id, title, author, year, isbn, status, borrower, borrowed_date = sel
        detail = f"ID: {book_id}\nJudul: {title}\nPenulis: {author}\nTahun: {year}\nISBN: {isbn}\nStatus: {status}"
        if status == "borrowed":
            detail += f"\nPeminjam: {borrower}\nTanggal Pinjam: {borrowed_date}"
        messagebox.showinfo("Detail Buku", detail)

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()
