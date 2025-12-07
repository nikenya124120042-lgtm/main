import streamlit as st
import sqlite3
from datetime import datetime

DB_FILE = "library.db"

# ============================
# DATABASE USER LOGIN
# ============================
def init_user_table():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()

    # Tambahkan user default jika belum ada
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password) VALUES ('admin','123')")
        conn.commit()

    conn.close()


# ============================
# DATABASE BUKU
# ============================
def init_book_table():
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

def validate_login(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    return result


# ==================================
# INISIALISASI DATABASE
# ==================================
init_user_table()
init_book_table()

# ==================================
# CSS TEMA
# ==================================
st.markdown("""
<style>
.big-title {
    font-size: 42px;
    font-weight: 900;
    color: #1A5276;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
* { font-family: 'Poppins', sans-serif !important; }
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
}
.stButton>button:hover {
    background-color: #64B5F6;
    transform: scale(1.04);
}
</style>
""", unsafe_allow_html=True)

# ==================================
# FITUR LOGIN
# ==================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<div class='big-title'>Login Perpustakaan</div>", unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if validate_login(username, password):
            st.session_state.logged_in = True
            st.success("Login berhasil!")
            st.rerun()
        else:
            st.error("Username atau password salah!")
    st.stop()

# ==================================
# MULAI APLIKASI JIKA SUDAH LOGIN
# ==================================
st.markdown("<div class='big-title'>Aplikasi Perpustakaan</div>", unsafe_allow_html=True)

# ---- Fungsi buku ----
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
    c.execute("UPDATE books SET title=?, author=?, year=?, isbn=? WHERE id=?",
              (title, author, year, isbn, book_id))
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
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        UPDATE books SET status='borrowed', borrower=?, borrowed_date=? WHERE id=?
    """, (borrower, now, book_id))
    conn.commit()
    conn.close()

def return_book(book_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        UPDATE books SET status='available', borrower=NULL, borrowed_date=NULL WHERE id=?
    """, (book_id,))
    conn.commit()
    conn.close()

# ==================================
# FORM TAMBAH / EDIT BUKU
# ==================================
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
        year_default = 0
        isbn_default = ""

    title = st.text_input("Judul", title_default)
    author = st.text_input("Penulis", author_default)
    year = st.number_input("Tahun", value=year_default, min_value=0, max_value=3000)
    isbn = st.text_input("ISBN", isbn_default)

    if st.form_submit_button("Simpan"):
        if mode == "Tambah":
            add_book(title, author, year, isbn)
            st.success("Buku berhasil ditambahkan!")
        else:
            update_book(book_id_default, title, author, year, isbn)
            st.success("Buku berhasil diedit!")

# ==================================
# TABEL BUKU
# ==================================
st.subheader("Daftar Buku")

search = st.text_input("Cari buku (judul/penulis/ISBN):")
rows = list_books(search)

import pandas as pd

if rows:
    df = pd.DataFrame(rows, columns=["ID","Judul","Penulis","Tahun","ISBN","Status","Peminjam","Tanggal Pinjam"])
    st.dataframe(df, use_container_width=True)
else:
    st.info("Tidak ada data ditemukan.")

# ==================================
# AKSI
# ==================================
st.subheader("Aksi Buku")

all_books = list_books()
book_dict = {f"{r[0]} - {r[1]}": r for r in all_books}

if book_dict:
    selected_action_book = st.selectbox("Pilih buku:", list(book_dict.keys()))
    data = book_dict[selected_action_book]
    book_id, status = data[0], data[5]

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Hapus Buku"):
            delete_book(book_id)
            st.success("Buku dihapus.")
            st.rerun()

    with col2:
        if status == "available":
            borrower = st.text_input("Nama peminjam:")
            if st.button("Pinjam Buku"):
                if borrower.strip():
                    borrow_book(book_id, borrower)
                    st.success("Buku berhasil dipinjam!")
                    st.rerun()
        else:
            if st.button("Kembalikan Buku"):
                return_book(book_id)
                st.success("Buku dikembalikan!")
                st.rerun()

    with col3:
        if st.button("Detail Buku"):
            st.info(f"""
            **ID:** {data[0]}  
            **Judul:** {data[1]}  
            **Penulis:** {data[2]}  
            **Tahun:** {data[3]}  
            **ISBN:** {data[4]}  
            **Status:** {data[5]}  
            **Peminjam:** {data[6] or '-'}  
            **Tanggal Pinjam:** {data[7] or '-'}  
            """)

# ==================================
# LOGOUT
# ==================================
if st.button("Logout"):
    st.session_state.logged_in = False
    st.success("Anda telah logout.")
    st.rerun()
