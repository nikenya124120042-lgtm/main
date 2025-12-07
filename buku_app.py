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
from datetime import datetime

DB_FILE = "library.db"

# ---------- DATABASE ----------
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
        status TEXT DEFAULT 'available',
        borrower TEXT,
        borrowed_date TEXT
    )
    """)
    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def list_books(search=""):
    conn = get_conn()
    c = conn.cursor()

    if search:
        pattern = f"%{search}%"
        c.execute("""
            SELECT id, title, author, year, isbn, status, borrower, borrowed_date 
            FROM books
            WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?
            ORDER BY title COLLATE NOCASE
        """, (pattern, pattern, pattern))
    else:
        c.execute("""
            SELECT id, title, author, year, isbn, status, borrower, borrowed_date 
            FROM books ORDER BY title COLLATE NOCASE
        """)
    rows = c.fetchall()
    conn.close()
    return rows

def add_book(title, author, year, isbn):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO books (title, author, year, isbn) VALUES (?, ?, ?, ?)",
        (title, author, year, isbn)
    )
    conn.commit()
    conn.close()

def update_book(book_id, title, author, year, isbn):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        UPDATE books SET title=?, author=?, year=?, isbn=? WHERE id=?
    """, (title, author, year, isbn, book_id))
    conn.commit()
    conn.close()

def delete_book(book_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()

def borrow_book(book_id, borrower):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat(timespec='seconds')
    c.execute("""
        UPDATE books SET status='borrowed', borrower=?, borrowed_date=? 
        WHERE id=?
    """, (borrower, now, book_id))
    conn.commit()
    conn.close()

def return_book(book_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        UPDATE books SET status='available', borrower=NULL, borrowed_date=NULL 
        WHERE id=?
    """, (book_id,))
    conn.commit()
    conn.close()
init_db()

# ----------- FORM TAMBAH / EDIT ----------
st.subheader("Tambah / Edit Buku")

with st.form("book_form"):
    mode = st.radio("Mode:", ["Tambah", "Edit"])

    if mode == "Edit":
        all_books = list_books()
        book_dict = {f"{r[0]} - {r[1]}": r for r in all_books}
        selected = st.selectbox("Pilih buku:", list(book_dict.keys()) )
        data = book_dict[selected]
        book_id_default = data[0]
        title_default = data[1]
        author_default = data[2]
        year_default = data[3]
        isbn_default = data[4]
    else:
        book_id_default = None
        title_default = ""
        author_default = ""
        year_default = ""
        isbn_default = ""

    title = st.text_input("Judul", title_default)
    author = st.text_input("Penulis", author_default)
    year = st.number_input("Tahun", min_value=0, max_value=3000, value=year_default or 0)
    isbn = st.text_input("ISBN", isbn_default)

    submitted = st.form_submit_button("Simpan")
    if submitted:
        if mode == "Tambah":
            add_book(title, author, year, isbn)
            st.success("Buku berhasil ditambahkan!")
        else:
            update_book(book_id_default, title, author, year, isbn)
            st.success("Buku berhasil diedit!")

# ---------- PENCARIAN ----------
st.subheader("Cari Buku")

search = st.text_input("Cari berdasarkan judul / penulis / ISBN:")

rows = list_books(search)

# ---------- TABEL BUKU ----------
st.subheader("Daftar Buku")

if rows:
    import pandas as pd
    df = pd.DataFrame(rows, columns=["ID","Judul","Penulis","Tahun","ISBN","Status","Peminjam","Tanggal Pinjam"])
    st.dataframe(df, use_container_width=True)
else:
    st.info("Tidak ada data ditemukan.")

# ---------- AKSI ----------
st.subheader("Aksi Buku")

all_books = list_books()
book_dict = {f"{r[0]} - {r[1]}": r for r in all_books}

if book_dict:
    action_book = st.selectbox("Pilih buku:", list(book_dict.keys()))
    selected_row = book_dict[action_book]
    book_id = selected_row[0]
    status = selected_row[5]

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Hapus Buku"):
            delete_book(book_id)
            st.success("Buku dihapus.")
            st.rerun()

    with col2:
        if status == "available":
            borrower = st.text_input("Masukkan nama peminjam:")
            if st.button("Pinjam Buku"):
                if borrower.strip():
                    borrow_book(book_id, borrower)
                    st.success("Buku dipinjam.")
                    st.rerun()
        else:
            if st.button("Kembalikan Buku"):
                return_book(book_id)
                st.success("Buku dikembalikan.")
                st.rerun()

    with col3:
        if st.button("Detail Buku"):
            st.info(
                f"""
                **ID:** {selected_row[0]}  
                **Judul:** {selected_row[1]}  
                **Penulis:** {selected_row[2]}  
                **Tahun:** {selected_row[3]}  
                **ISBN:** {selected_row[4]}  
                **Status:** {selected_row[5]}  
                {"**Peminjam:** " + selected_row[6] if selected_row[6] else ""}  
                {"**Tanggal Pinjam:** " + selected_row[7] if selected_row[7] else ""}  
                """
            )import streamlit as st
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
import streamlit as st
import sqlite3
from datetime import datetime

DB_FILE = "library.db"

# ---------- DATABASE ----------
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
        status TEXT DEFAULT 'available',
        borrower TEXT,
        borrowed_date TEXT
    )
    """)
    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def list_books(search=""):
    conn = get_conn()
    c = conn.cursor()

    if search:
        pattern = f"%{search}%"
        c.execute("""
            SELECT id, title, author, year, isbn, status, borrower, borrowed_date 
            FROM books
            WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?
            ORDER BY title COLLATE NOCASE
        """, (pattern, pattern, pattern))
    else:
        c.execute("""
            SELECT id, title, author, year, isbn, status, borrower, borrowed_date 
            FROM books ORDER BY title COLLATE NOCASE
        """)
    rows = c.fetchall()
    conn.close()
    return rows

def add_book(title, author, year, isbn):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO books (title, author, year, isbn) VALUES (?, ?, ?, ?)",
        (title, author, year, isbn)
    )
    conn.commit()
    conn.close()

def update_book(book_id, title, author, year, isbn):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        UPDATE books SET title=?, author=?, year=?, isbn=? WHERE id=?
    """, (title, author, year, isbn, book_id))
    conn.commit()
    conn.close()

def delete_book(book_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id=?", (book_id,))
    conn.commit()
    conn.close()

def borrow_book(book_id, borrower):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat(timespec='seconds')
    c.execute("""
        UPDATE books SET status='borrowed', borrower=?, borrowed_date=? 
        WHERE id=?
    """, (borrower, now, book_id))
    conn.commit()
    conn.close()

def return_book(book_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        UPDATE books SET status='available', borrower=NULL, borrowed_date=NULL 
        WHERE id=?
    """, (book_id,))
    conn.commit()
    conn.close()
init_db()

# ----------- FORM TAMBAH / EDIT ----------
st.subheader("Tambah / Edit Buku")

with st.form("book_form"):
    mode = st.radio("Mode:", ["Tambah", "Edit"])

    if mode == "Edit":
        all_books = list_books()
        book_dict = {f"{r[0]} - {r[1]}": r for r in all_books}
        selected = st.selectbox("Pilih buku:", list(book_dict.keys()) )
        data = book_dict[selected]
        book_id_default = data[0]
        title_default = data[1]
        author_default = data[2]
        year_default = data[3]
        isbn_default = data[4]
    else:
        book_id_default = None
        title_default = ""
        author_default = ""
        year_default = ""
        isbn_default = ""

    title = st.text_input("Judul", title_default)
    author = st.text_input("Penulis", author_default)
    year = st.number_input("Tahun", min_value=0, max_value=3000, value=year_default or 0)
    isbn = st.text_input("ISBN", isbn_default)

    submitted = st.form_submit_button("Simpan")
    if submitted:
        if mode == "Tambah":
            add_book(title, author, year, isbn)
            st.success("Buku berhasil ditambahkan!")
        else:
            update_book(book_id_default, title, author, year, isbn)
            st.success("Buku berhasil diedit!")

# ---------- PENCARIAN ----------
st.subheader("Cari Buku")

search = st.text_input("Cari berdasarkan judul / penulis / ISBN:")

rows = list_books(search)

# ---------- TABEL BUKU ----------
st.subheader("Daftar Buku")

if rows:
    import pandas as pd
    df = pd.DataFrame(rows, columns=["ID","Judul","Penulis","Tahun","ISBN","Status","Peminjam","Tanggal Pinjam"])
    st.dataframe(df, use_container_width=True)
else:
    st.info("Tidak ada data ditemukan.")

# ---------- AKSI ----------
st.subheader("Aksi Buku")

all_books = list_books()
book_dict = {f"{r[0]} - {r[1]}": r for r in all_books}

if book_dict:
    action_book = st.selectbox("Pilih buku:", list(book_dict.keys()))
    selected_row = book_dict[action_book]
    book_id = selected_row[0]
    status = selected_row[5]

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Hapus Buku"):
            delete_book(book_id)
            st.success("Buku dihapus.")
            st.rerun()

    with col2:
        if status == "available":
            borrower = st.text_input("Masukkan nama peminjam:")
            if st.button("Pinjam Buku"):
                if borrower.strip():
                    borrow_book(book_id, borrower)
                    st.success("Buku dipinjam.")
                    st.rerun()
        else:
            if st.button("Kembalikan Buku"):
                return_book(book_id)
                st.success("Buku dikembalikan.")
                st.rerun()

    with col3:
        if st.button("Detail Buku"):
            st.info(
                f"""
                **ID:** {selected_row[0]}  
                **Judul:** {selected_row[1]}  
                **Penulis:** {selected_row[2]}  
                **Tahun:** {selected_row[3]}  
                **ISBN:** {selected_row[4]}  
                **Status:** {selected_row[5]}  
                {"**Peminjam:** " + selected_row[6] if selected_row[6] else ""}  
                {"**Tanggal Pinjam:** " + selected_row[7] if selected_row[7] else ""}  
                """
            )
