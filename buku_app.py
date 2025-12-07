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
import streamlit as st
from datetime import datetime

# =========================================================
# OOP MODEL DATA
# =========================================================

class Buku:
    def __init__(self, id_buku, judul, penulis):
        self.id_buku = id_buku
        self.judul = judul
        self.penulis = penulis
        self.status = "Tersedia"   # Tersedia / Dipinjam

class Riwayat:
    def __init__(self, id_buku, user, aksi, waktu):
        self.id_buku = id_buku
        self.user = user
        self.aksi = aksi
        self.waktu = waktu

# =========================================================
# OOP UTAMA: Perpustakaan
# =========================================================

class Perpustakaan:
    def __init__(self):
        self.buku_list = []
        self.riwayat_list = []

    # ---------------- Tambah Buku ----------------
    def tambah_buku(self, id_buku, judul, penulis):
        buku = Buku(id_buku, judul, penulis)
        self.buku_list.append(buku)
        return True

    # ---------------- Hapus Buku ----------------
    def hapus_buku(self, id_buku):
        for b in self.buku_list:
            if b.id_buku == id_buku:
                self.buku_list.remove(b)
                return True
        return False

    # ---------------- Pinjam Buku ----------------
    def pinjam(self, id_buku, user):
        for b in self.buku_list:
            if b.id_buku == id_buku and b.status == "Tersedia":
                b.status = "Dipinjam"
                self.riwayat_list.append(
                    Riwayat(id_buku, user, "PINJAM", datetime.now())
                )
                return True
        return False

    # ---------------- Kembalikan Buku ----------------
    def kembalikan(self, id_buku, user):
        for b in self.buku_list:
            if b.id_buku == id_buku and b.status == "Dipinjam":
                b.status = "Tersedia"
                self.riwayat_list.append(
                    Riwayat(id_buku, user, "KEMBALI", datetime.now())
                )
                return True
        return False

    # ---------------- Ambil Daftar ----------------
    def daftar_buku(self):
        return self.buku_list

    def daftar_tersedia(self):
        return [b for b in self.buku_list if b.status == "Tersedia"]

    def daftar_dipinjam(self):
        return [b for b in self.buku_list if b.status == "Dipinjam"]

    def daftar_riwayat(self):
        return self.riwayat_list


# =========================================================
# SESSION STATE
# =========================================================
if "login" not in st.session_state:
    st.session_state.login = False

if "perpus" not in st.session_state:
    st.session_state.perpus = Perpustakaan()

USERNAME = "admin"
PASSWORD = "123"


# =========================================================
# HALAMAN LOGIN
# =========================================================
def login_page():
    st.title("🔐 Login Sistem Perpustakaan")

    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == USERNAME and pw == PASSWORD:
            st.session_state.login = True
            st.success("Login Berhasil!")
        else:
            st.error("Username atau password salah!")


# =========================================================
# MENU TAMBAH BUKU
# =========================================================
def menu_tambah():
    st.header("📚 Tambah Buku")

    id_buku = st.text_input("ID Buku")
    judul = st.text_input("Judul Buku")
    penulis = st.text_input("Penulis Buku")

    if st.button("Tambah Buku"):
        if id_buku and judul and penulis:
            st.session_state.perpus.tambah_buku(id_buku, judul, penulis)
            st.success("Buku berhasil ditambahkan!")
        else:
            st.warning("Semua kolom harus diisi!")


# =========================================================
# MENU HAPUS BUKU
# =========================================================
def menu_hapus():
    st.header("🗑️ Hapus Buku")

    buku_list = st.session_state.perpus.daftar_buku()

    if not buku_list:
        st.info("Belum ada buku.")
        return

    pilihan = st.selectbox(
        "Pilih Buku", 
        [f"{b.id_buku} - {b.judul}" for b in buku_list]
    )

    id_buku = pilihan.split(" - ")[0]

    if st.button("Hapus"):
        st.session_state.perpus.hapus_buku(id_buku)
        st.success("Buku berhasil dihapus!")


# =========================================================
# MENU PEMINJAMAN
# =========================================================
def menu_pinjam():
    st.header("📖 Peminjaman Buku")

    tersedia = st.session_state.perpus.daftar_tersedia()

    if not tersedia:
        st.info("Tidak ada buku tersedia.")
        return
# =========================================================
# MENU PEMINJAMAN (DENGAN INPUT NAMA PEMINJAM)
# =========================================================
def menu_pinjam():
    st.header("📖 Peminjaman Buku")

    tersedia = st.session_state.perpus.daftar_tersedia()

    if not tersedia:
        st.info("Tidak ada buku tersedia.")
        return

    pilihan = st.selectbox(
        "Pilih Buku",
        [f"{b.id_buku} - {b.judul}" for b in tersedia]
    )

    id_buku = pilihan.split(" - ")[0]

    # Tambahan baru → input nama peminjam
    nama_peminjam = st.text_input("Nama Peminjam")

    if st.button("Pinjam"):
        if nama_peminjam.strip() == "":
            st.warning("Nama peminjam harus diisi!")
            return

        st.session_state.perpus.pinjam(id_buku, nama_peminjam)
        st.success(f"Buku berhasil dipinjam oleh {nama_peminjam}!")

    pilihan = st.selectbox(
        "Pilih Buku",
        [f"{b.id_buku} - {b.judul}" for b in tersedia]
    )

    id_buku = pilihan.split(" - ")[0]

    if st.button("Pinjam"):
        st.session_state.perpus.pinjam(id_buku, USERNAME)
        st.success("Buku berhasil dipinjam!")


# =========================================================
# MENU PENGEMBALIAN
# =========================================================
def menu_kembalikan():
    st.header("↩️ Pengembalian Buku")

    dipinjam = st.session_state.perpus.daftar_dipinjam()

    if not dipinjam:
        st.info("Tidak ada buku yang sedang dipinjam.")
        return

    pilihan = st.selectbox(
        "Pilih Buku",
        [f"{b.id_buku} - {b.judul}" for b in dipinjam]
    )

    id_buku = pilihan.split(" - ")[0]

    if st.button("Kembalikan"):
        st.session_state.perpus.kembalikan(id_buku, USERNAME)
        st.success("Buku berhasil dikembalikan!")

# =========================================================
# MENU PENGEMBALIAN (DENGAN NAMA PENGEMBALIAN)
# =========================================================
def menu_kembalikan():
    st.header("↩️ Pengembalian Buku")

    dipinjam = st.session_state.perpus.daftar_dipinjam()

    if not dipinjam:
        st.info("Tidak ada buku yang sedang dipinjam.")
        return

    pilihan = st.selectbox(
        "Pilih Buku",
        [f"{b.id_buku} - {b.judul}" for b in dipinjam]
    )

    id_buku = pilihan.split(" - ")[0]

    nama_pengembali = st.text_input("Nama Pengembali")

    if st.button("Kembalikan"):
        if nama_pengembali.strip() == "":
            st.warning("Nama pengembali harus diisi!")
            return

        st.session_state.perpus.kembalikan(id_buku, nama_pengembali)
        st.success(f"Buku berhasil dikembalikan oleh {nama_pengembali}!")

# =========================================================
# MENU RIWAYAT
# =========================================================
def menu_riwayat():
    st.header("📜 Riwayat Peminjaman")

    riwayat = st.session_state.perpus.daftar_riwayat()

    if not riwayat:
        st.info("Belum ada riwayat.")
        return

    for r in riwayat:
        st.write(
            f"📘 ID Buku: **{r.id_buku}** | "
            f"Aksi: **{r.aksi}** | "
            f"User: **{r.user}** | "
            f"Waktu: {r.waktu.strftime('%Y-%m-%d %H:%M:%S')}"
        )


# =========================================================
# MAIN APP
# =========================================================
def main():
    st.sidebar.title("📘 Menu Perpustakaan")

    menu = st.sidebar.radio(
        "Navigasi",
        ["Tambah Buku", "Hapus Buku", "Peminjaman", "Pengembalian", "Riwayat"]
    )

    if menu == "Tambah Buku":
        menu_tambah()
    elif menu == "Hapus Buku":
        menu_hapus()
    elif menu == "Peminjaman":
        menu_pinjam()
    elif menu == "Pengembalian":
        menu_kembalikan()
    elif menu == "Riwayat":
        menu_riwayat()


# =========================================================
# RUN PROGRAM
# =========================================================
if not st.session_state.login:
    login_page()
else:
    main()
