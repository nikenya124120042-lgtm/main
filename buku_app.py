import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ================================
# CUSTOM CSS
# ================================
st.markdown("""
<style>
.big-title {
    font-size: 42px;
    font-weight: 900;
    color: #1A5276;
    text-align: center;
}

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

* {
    font-family: 'Poppins', sans-serif !important;
}

.stApp {
    background: linear-gradient(135deg, #E3F2FD, #BBDEFB, #E8F4FF);
}

.stButton>button {
    background-color: #90CAF9;
    color: white;
    border-radius: 12px;
    padding: 10px 20px;
    border: none;
    font-weight: 600;
    transition: 0.2s;
    font-size: 15px;
}
.stButton>button:hover {
    background-color: #64B5F6;
    transform: scale(1.04);
}
</style>
""", unsafe_allow_html=True)

# ================================
# TAMPILAN UTAMA
# ================================
st.markdown("<div class='big-title'>Aplikasi Perpustakaan</div>", unsafe_allow_html=True)


# ==========================================
# DATABASE CLASS
# ==========================================
class Database:
    def __init__(self, db_name="library.db"):
        self.db_name = db_name
        self.create_table()

    def connect(self):
        return sqlite3.connect(self.db_name)

    def create_table(self):
        conn = self.connect()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT,
                penulis TEXT,
                tahun INTEGER,
                isbn TEXT,
                status TEXT,
                peminjam TEXT,
                tanggal_pinjam TEXT
            )
        """)
        conn.commit()
        conn.close()

    def execute(self, query, params=(), fetch=False):
        conn = self.connect()
        c = conn.cursor()
        c.execute(query, params)
        data = c.fetchall() if fetch else None
        conn.commit()
        conn.close()
        return data


# ==========================================
# BOOK CLASS
# ==========================================
class Book:
    def __init__(self, judul, penulis, tahun, isbn):
        self.judul = judul
        self.penulis = penulis
        self.tahun = tahun
        self.isbn = isbn


# ==========================================
# LIBRARY SYSTEM CLASS
# ==========================================
class LibrarySystem:
    def __init__(self, database):
        self.db = database

    def add_book(self, book: Book):
        self.db.execute("""
            INSERT INTO books (judul, penulis, tahun, isbn, status)
            VALUES (?, ?, ?, ?, "tersedia")
        """, (book.judul, book.penulis, book.tahun, book.isbn))

    def get_all_books(self):
        return self.db.execute("SELECT * FROM books", fetch=True)

    def borrow_book(self, book_id, peminjam):
        today = datetime.today().strftime("%Y-%m-%d")
        self.db.execute("""
            UPDATE books 
            SET status='dipinjam', peminjam=?, tanggal_pinjam=?
            WHERE id=?
        """, (peminjam, today, book_id))

    def return_book(self, book_id):
        self.db.execute("""
            UPDATE books 
            SET status='tersedia', peminjam='', tanggal_pinjam=''
            WHERE id=?
        """, (book_id,))


# ==========================================
# SISTEM LOGIN
# ==========================================
accounts = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"}
}

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.subheader("🔐 Login Aplikasi")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in accounts and accounts[username]["password"] == password:
            st.success(f"Login berhasil sebagai {accounts[username]['role']}")
            st.session_state.login = True
            st.session_state.role = accounts[username]["role"]
        else:
            st.error("Username atau password salah!")
    st.stop()


# ==========================================
# SETELAH LOGIN
# ==========================================
db = Database()
library = LibrarySystem(db)

st.sidebar.title("Menu")


# ADMIN MENU
if st.session_state.role == "admin":
    menu = st.sidebar.selectbox("Pilih Menu", ["Tambah Buku", "Daftar Buku", "Peminjaman", "Pengembalian"])

# USER MENU
else:
    menu = st.sidebar.selectbox("Pilih Menu", ["Daftar Buku", "Peminjaman", "Pengembalian"])


# ==============================
# FITUR APLIKASI
# ==============================

# TAMBAH BUKU (ADMIN ONLY)
if menu == "Tambah Buku" and st.session_state.role == "admin":
    st.header("➕ Tambah Buku Baru")

    judul = st.text_input("Judul Buku")
    penulis = st.text_input("Penulis")
    tahun = st.number_input("Tahun Terbit", min_value=0, max_value=9999)
    isbn = st.text_input("ISBN")

    if st.button("Simpan Buku"):
        buku_baru = Book(judul, penulis, tahun, isbn)
        library.add_book(buku_baru)
        st.success("Buku berhasil ditambahkan!")


# DAFTAR BUKU
if menu == "Daftar Buku":
    st.header("📖 Daftar Semua Buku")

    data = library.get_all_books()

    df = pd.DataFrame(data, columns=[
        "ID", "Judul", "Penulis", "Tahun", "ISBN",
        "Status", "Peminjam", "Tanggal Pinjam"
    ])

    st.dataframe(df, use_container_width=True)


# PEMINJAMAN
if menu == "Peminjaman":
    st.header("📘 Form Peminjaman Buku")

    data = library.get_all_books()
    df = pd.DataFrame(data, columns=[
        "ID", "Judul", "Penulis", "Tahun", "ISBN",
        "Status", "Peminjam", "Tanggal Pinjam"
    ])

    buku_tersedia = df[df["Status"] == "tersedia"]

    if len(buku_tersedia) > 0:
        id_buku = st.selectbox("Pilih Buku", buku_tersedia["ID"].tolist())
        peminjam = st.text_input("Nama Peminjam")

        if st.button("Pinjam"):
            library.borrow_book(id_buku, peminjam)
            st.success("Buku berhasil dipinjam!")
    else:
        st.info("Tidak ada buku tersedia.")


# PENGEMBALIAN
if menu == "Pengembalian":
    st.header("📗 Form Pengembalian Buku")

    data = library.get_all_books()
    df = pd.DataFrame(data, columns=[
        "ID", "Judul", "Penulis", "Tahun", "ISBN",
        "Status", "Peminjam", "Tanggal Pinjam"
    ])

    buku_dipinjam = df[df["Status"] == "dipinjam"]

    if len(buku_dipinjam) > 0:
        id_buku = st.selectbox("Pilih Buku Dipinjam", buku_dipinjam["ID"].tolist())

        if st.button("Kembalikan Buku"):
            library.return_book(id_buku)
            st.success("Buku berhasil dikembalikan!")
    else:
        st.info("Tidak ada buku dipinjam.")
