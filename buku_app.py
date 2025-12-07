import streamlit as st
import sqlite3

# =============================
# BAGIAN 1 — CSS UNTUK TAMPILAN
# =============================
st.markdown("""
<style>
/* CSS DI SINI */
.big-title {
    font-size: 42px;
    font-weight: 900;
    color: #1A5276;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# =============================
# BAGIAN 2 — HEADER
# =============================
st.markdown("<div class='big-title'>Aplikasi Perpustakaan</div>", unsafe_allow_html=True)

# ======== TEMA BIRU PASTEL + FONT POPPINS ========
st.markdown("""
<style>

    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    * {
        font-family: 'Poppins', sans-serif !important;
    }

    /* Background utama biru pastel */
    .stApp {
        background: linear-gradient(135deg, #E3F2FD, #BBDEFB, #E8F4FF);
    }

    /* Card / container */
    .stMarkdown, .stTextInput, .stSelectbox, .stNumberInput, .stDataFrame {
        background-color: #ffffffcc; 
        padding: 12px;
        border-radius: 12px;
        backdrop-filter: blur(6px);
    }

    /* Judul */
    h1, h2, h3 {
        color: #1A73E8 !important;
        font-weight: 700;
    }

    /* Input box */
    .stTextInput>div>div>input {
        background-color: #F0F7FF;
        border-radius: 8px;
        border: 1px solid #CFE2FF;
        font-size: 15px;
    }

    /* Selectbox */
    .stSelectbox>div>div {
        background-color: #F0F7FF;
        border-radius: 8px;
        border: 1px solid #CFE2FF;
    }

    /* Tombol */
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

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #D7EAFE;
    }

</style>
""", unsafe_allow_html=True)
# ===========================
# SISTEM LOGIN + PERPUSTAKAAN
# ===========================

# Database akun (bisa disimpan ke file jika ingin lebih lengkap)
accounts = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"}
}

# Database buku
buku_list = []


# ---------------------------
# Fungsi Login
# ---------------------------
def login():
    print("===== LOGIN =====")
    username = input("Username : ")
    password = input("Password : ")

    if username in accounts and accounts[username]["password"] == password:
        print(f"Login berhasil sebagai {username} ({accounts[username]['role']})\n")
        return accounts[username]["role"]
    else:
        print("Login gagal! Username atau password salah.\n")
        return None


# ---------------------------
# Menu Admin
# ---------------------------
def menu_admin():
    while True:
        print("===== MENU ADMIN =====")
        print("1. Tambah Buku")
        print("2. Lihat Daftar Buku")
        print("3. Logout")

        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            tambah_buku()
        elif pilihan == "2":
            lihat_buku()
        elif pilihan == "3":
            print("Logout...\n")
            break
        else:
            print("Pilihan tidak valid!\n")


# ---------------------------
# Menu User
# ---------------------------
def menu_user():
    while True:
        print("===== MENU USER =====")
        print("1. Lihat Daftar Buku")
        print("2. Logout")

        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            lihat_buku()
        elif pilihan == "2":
            print("Logout...\n")
            break
        else:
            print("Pilihan tidak valid!\n")


# ---------------------------
# Fungsi Tambah Buku
# ---------------------------
def tambah_buku():
    print("\n=== Tambah Buku ===")
    judul = input("Judul Buku : ")
    penulis = input("Penulis    : ")
    tahun = input("Tahun Terbit : ")

    buku = {
        "judul": judul,
        "penulis": penulis,
        "tahun": tahun
    }

    buku_list.append(buku)
    print("Buku berhasil ditambahkan!\n")


# ---------------------------
# Fungsi Lihat Buku
# ---------------------------
def lihat_buku():
    print("\n=== Daftar Buku ===")

    if not buku_list:
        print("Belum ada buku.\n")
        return

    for i, buku in enumerate(buku_list, 1):
        print(f"{i}. {buku['judul']} - {buku['penulis']} ({buku['tahun']})")

    print("")


# ---------------------------
# PROGRAM UTAMA
# ---------------------------
def main():
    print("===================================")
    print("   SISTEM PERPUSTAKAAN SEDERHANA   ")
    print("===================================\n")

    while True:
        role = login()

        if role == "admin":
            menu_admin()
        elif role == "user":
            menu_user()
        else:
            print("Silakan coba login lagi.\n")


# Jalankan Program
main()
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ===========================================================
# CLASS DATABASE
# ===========================================================
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
        data = None
        if fetch:
            data = c.fetchall()
        conn.commit()
        conn.close()
        return data


# ===========================================================
# CLASS BOOK
# ===========================================================
class Book:
    def __init__(self, judul, penulis, tahun, isbn):
        self.judul = judul
        self.penulis = penulis
        self.tahun = tahun
        self.isbn = isbn


# ===========================================================
# CLASS LIBRARY SYSTEM
# ===========================================================
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


# ===========================================================
# STREAMLIT UI
# ===========================================================

st.title("📚 Aplikasi Perpustakaan (Versi OOP)")

# Create database + system
db = Database()
library = LibrarySystem(db)

menu = st.sidebar.selectbox("Menu", ["Tambah Buku", "Daftar Buku", "Peminjaman", "Pengembalian"])

# --------------------- TAMBAH BUKU -------------------------
if menu == "Tambah Buku":
    st.header("➕ Tambah Buku Baru")

    judul = st.text_input("Judul Buku")
    penulis = st.text_input("Penulis")
    tahun = st.number_input("Tahun Terbit", min_value=0, max_value=9999)
    isbn = st.text_input("ISBN")

    if st.button("Simpan Buku"):
        buku_baru = Book(judul, penulis, tahun, isbn)
        library.add_book(buku_baru)
        st.success("Buku berhasil ditambahkan!")

# --------------------- DAFTAR BUKU -------------------------
elif menu == "Daftar Buku":
    st.header("📖 Daftar Semua Buku")

    data = library.get_all_books()

    df = pd.DataFrame(data, columns=[
        "ID", "Judul", "Penulis", "Tahun", "ISBN", 
        "Status", "Peminjam", "Tanggal Pinjam"
    ])

    st.dataframe(df, use_container_width=True)

# --------------------- PEMINJAMAN -------------------------
elif menu == "Peminjaman":
    st.header("📘 Form Peminjaman Buku")

    data = library.get_all_books()
    buku_df = pd.DataFrame(data, columns=[
        "ID", "Judul", "Penulis", "Tahun", "ISBN", 
        "Status", "Peminjam", "Tanggal Pinjam"
    ])

    buku_tersedia = buku_df[buku_df["Status"] == "tersedia"]

    if len(buku_tersedia) > 0:
        id_buku = st.selectbox("Pilih Buku", buku_tersedia["ID"].tolist())
        peminjam = st.text_input("Nama Peminjam")

        if st.button("Pinjam"):
            library.borrow_book(id_buku, peminjam)
            st.success("Buku berhasil dipinjam!")
    else:
        st.info("Tidak ada buku yang tersedia.")

# --------------------- PENGEMBALIAN -------------------------
elif menu == "Pengembalian":
    st.header("📗 Form Pengembalian Buku")

    data = library.get_all_books()
    buku_df = pd.DataFrame(data, columns=[
        "ID", "Judul", "Penulis", "Tahun", "ISBN", 
        "Status", "Peminjam", "Tanggal Pinjam"
    ])

    buku_dipinjam = buku_df[buku_df["Status"] == "dipinjam"]

    if len(buku_dipinjam) > 0:
        id_buku = st.selectbox("Pilih Buku Dipinjam", buku_dipinjam["ID"].tolist())

        if st.button("Kembalikan Buku"):
            library.return_book(id_buku)
            st.success("Buku berhasil dikembalikan!")
    else:
        st.info("Tidak ada buku yang sedang dipinjam.")
