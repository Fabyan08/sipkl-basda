import psycopg2
import re
import hashlib
from tabulate import tabulate
from datetime import datetime


def koneksi_db():
    try:
        return psycopg2.connect(
            dbname="GoPKL", user="postgres", password="gajahterbang",
            host="localhost", port="5432"
        )
    except psycopg2.Error as e:
        print("Gagal koneksi ke database:", e)
        return None
    
conn = koneksi_db()       
cur = conn.cursor() 

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register():
    print("\n=== REGISTRASI ===")
    conn = koneksi_db()
    cursor = conn.cursor()

    nama = input("Nama: ")
    email = input("Email: ")
    if not is_valid_email(email):
        print("Email tidak valid.")
        return

    password = input("Password: ")
    kelas = input("Kelas: ")
    no_hp = input("No HP: ")
    no_induk = input("No Induk: ")

    print("\nJenis Akun:")
    print("[1] Siswa")
    print("[2] Guru")
    role = input("Pilih (1/2): ")

    if role == '1':
        role = 'siswa'
    elif role == '2':
        role = 'guru'
    else:
        print("Pilihan tidak valid.")
        return

    try:
        cursor.execute("""
            INSERT INTO users (nama, email, password, kelas, no_hp, no_induk, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nama, email, hash_password(password), kelas, no_hp, no_induk, role))
        conn.commit()
        print("Registrasi berhasil!\n")
    except psycopg2.Error as e:
        print("Registrasi gagal:", e)
    finally:
        cursor.close()
        conn.close()

def login():
    print("\n=== LOGIN ===")
    conn = koneksi_db()
    cursor = conn.cursor()

    email = input("Email: ").strip()
    password = input("Password: ").strip()

    if not is_valid_email(email):
        print("Format email tidak valid.")
        return

    try:
        cursor.execute("SELECT id, nama, password, role FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user and user[2] == hash_password(password):
            print(f"Login berhasil! Selamat datang, {user[1]}")
            show_menu(user[3], user[0])
        else:
            print("Email atau password salah.")
    except psycopg2.Error as e:
        print("Terjadi kesalahan saat login:", e)
    finally:
        cursor.close()
        conn.close()

def show_menu(role, user_id):
    print("\n=== MENU UTAMA ===")
    print("[0] Profil")
    if role == "siswa":
        print("[1] Ajukan PKL")
        print("[2] Lihat Status Verifikasi")
        print("[3] Cetak Surat Pengantar")
        print("[4] Buat Laporan")
    elif role == "guru":
        print("[1] Lihat Laporan")
        print("[2] Beri Nilai Akhir")
    elif role == "admin":
        print("[1] Kelola Data Guru")
        print("[2] Kelola Data Siswa")
        print("[3] Kelola Data Mitra PKL")
        print("[4] Kelola Data Periode PKL")
        print("[5] Verifikasi Pengajuan Siswa")
    else:
        print("Role tidak dikenali.")
        return
    
    pilihan = input("Pilih menu: ")
    if pilihan == '0':
        show_profile(role, user_id)
    elif role == "admin":
        if pilihan == '1':
            kelola_data_guru(role,user_id)
        elif pilihan == '2':
            kelola_data_siswa(role,user_id)
        elif pilihan == '3':
             kelola_data_mitra(role, user_id)
        elif pilihan == '4':
            kelola_data_periode(role, user_id)
        elif pilihan == '5':
            verifikasi_pengajuan_siswa(role, user_id)
        elif pilihan == '0':
            show_profile(role, user_id)
        elif pilihan == '9':
            main_menu()
        else:
            print("Fitur belum tersedia.")
    elif role == "siswa":
        if pilihan == '1':
            ajukan_pkl(role, user_id)
        elif pilihan == '2':
            lihat_status_verifikasi(role, user_id)
        elif pilihan == '3':
            cetak_surat(user_id)
        elif pilihan == '4':
            buat_laporan(user_id)
        elif pilihan == '0':
            show_profile(role, user_id)
        elif pilihan == '9':
            main_menu()
    else:
        print("Fitur belum tersedia.")
        show_menu(role, user_id)
    return

def tampilkan_users(role):
    conn = koneksi_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nama, email, no_hp FROM users WHERE role = %s ORDER BY id", (role,))
    data = cur.fetchall()
    cur.close()
    conn.close()

    if not data:
        print(f"\nTidak ada data {role}.")
    else:
        headers = ["ID", "Nama", "Email", "No HP"]
        print("\n" + tabulate(data, headers=headers, tablefmt="grid"))

def kelola_data_guru(role, user_id):
    while True:
        print("\n=== KELOLA DATA GURU ===")
        tampilkan_users('guru')
        print("[1] Tambah Guru")
        print("[2] Edit Guru")
        print("[3] Hapus Guru")
        print("[0] Kembali")
        pilih = input("Pilih menu: ")
        if pilih == '1':
            tambah_user('guru')
        elif pilih == '2':
            edit_user('guru')
        elif pilih == '3':
            hapus_user('guru')
        elif pilih == '0':
            show_menu(role, user_id) 
            break       
        else:
            print("Pilihan tidak valid.")

def kelola_data_siswa(role, user_id):
    while True:
        print("\n=== KELOLA DATA SISWA ===")
        tampilkan_users('siswa')
        print("[1] Tambah Siswa")
        print("[2] Edit Siswa")
        print("[3] Hapus Siswa")
        print("[0] Kembali")
        pilih = input("Pilih menu: ")
        if pilih == '1':
            tambah_user('siswa')
        elif pilih == '2':
            edit_user('siswa')
        elif pilih == '3':
            hapus_user('siswa')
        elif pilih == '0':
            show_menu(role, user_id) 
            break
        else:
            print("Pilihan tidak valid.")
            
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def tambah_user(role):
    nama = input("Nama: ")
    email = input("Email: ")
    password = input("Password: ")
    kelas = input("Kelas (kosongkan jika guru): ") if role == 'siswa' else None
    no_hp = input("No HP: ")
    no_induk = input("No Induk: ")

    conn = koneksi_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (nama, email, password, kelas, no_hp, no_induk, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (nama, email, hash_password(password), kelas, no_hp, no_induk, role))
    conn.commit()
    cur.close()
    conn.close()
    print(f"{role.capitalize()} berhasil ditambahkan.")

def edit_user(role):
    user_id = input("ID {} yang ingin diedit: ".format(role))
    
    # Ambil data lama
    conn = koneksi_db()
    cur = conn.cursor()
    cur.execute("SELECT nama, email, no_hp FROM users WHERE id = %s AND role = %s", (user_id, role))
    user = cur.fetchone()

    if not user:
        print(f"{role.capitalize()} dengan ID tersebut tidak ditemukan.")
        cur.close()
        conn.close()
        return

    nama_lama, email_lama, no_hp_lama = user

    # Input baru (boleh kosong)
    nama_baru = input("Nama baru: ").strip()
    email_baru = input("Email baru: ").strip()
    no_hp_baru = input("No HP baru: ").strip()

    # Pakai data lama jika kosong
    if nama_baru == "":
        nama_baru = nama_lama
    if email_baru == "":
        email_baru = email_lama
    if no_hp_baru == "":
        no_hp_baru = no_hp_lama

    try:
        cur.execute("""
            UPDATE users
            SET nama = %s, email = %s, no_hp = %s
            WHERE id = %s AND role = %s
        """, (nama_baru, email_baru, no_hp_baru, user_id, role))
        conn.commit()
        print(f"{role.capitalize()} berhasil diedit.")
    except Exception as e:
        print("Gagal mengedit:", e)
    finally:
        cur.close()
        conn.close()

def hapus_user(role):
    user_id = input(f"ID {role} yang ingin dihapus: ")
    conn = koneksi_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=%s AND role=%s", (user_id, role))
    conn.commit()
    cur.close()
    conn.close()
    print(f"{role.capitalize()} berhasil dihapus.")

# Mitra

def kelola_data_mitra(role, user_id):
    while True:
        print("\n=== KELOLA DATA MITRA PKL ===")
        data = ambil_data_mitra()
        print(tabulate(data, headers=["ID", "Nama", "Alamat", "Kontak"], tablefmt="grid"))

        print("[1] Tambah Mitra")
        print("[2] Edit Mitra")
        print("[3] Hapus Mitra")
        print("[0] Kembali")
        pilihan = input("Pilih menu: ")

        if pilihan == '1':
            tambah_mitra()
        elif pilihan == '2':
            edit_mitra()
        elif pilihan == '3':
            hapus_mitra()
        elif pilihan == '0':
            show_menu(role, user_id)
            break
        else:
            print("Pilihan tidak valid.")

def ambil_data_mitra():
    cur = koneksi_db().cursor()
    cur.execute("SELECT id, nama, alamat, kontak_person FROM mitra_pkl ORDER BY id")
    return cur.fetchall()

def tambah_mitra():
    print("\n=== Tambah Mitra PKL ===")
    nama = input("Nama Mitra: ")
    alamat = input("Alamat: ")
    kontak = input("Kontak Person: ")

    cur.execute("INSERT INTO mitra_pkl (nama, alamat, kontak_person) VALUES (%s, %s, %s)", 
                (nama, alamat, kontak))
    conn.commit()
    print("Mitra PKL berhasil ditambahkan.")

def edit_mitra():
    id_mitra = input("ID mitra yang ingin diedit: ")

    cur.execute("SELECT * FROM mitra_pkl WHERE id = %s", (id_mitra,))
    mitra = cur.fetchone()
    if not mitra:
        print("Mitra tidak ditemukan.")
        return

    nama_baru = input(f"Nama baru (kosongkan untuk tetap '{mitra[1]}'): ") or mitra[1]
    alamat_baru = input(f"Alamat baru (kosongkan untuk tetap '{mitra[2]}'): ") or mitra[2]
    kontak_baru = input(f"Kontak baru (kosongkan untuk tetap '{mitra[3]}'): ") or mitra[3]

    cur.execute("""
        UPDATE mitra_pkl 
        SET nama = %s, alamat = %s, kontak_person = %s 
        WHERE id = %s
    """, (nama_baru, alamat_baru, kontak_baru, id_mitra))
    conn.commit()
    print("Mitra berhasil diedit.")

def hapus_mitra():
    id_mitra = input("ID mitra yang ingin dihapus: ")
    cur.execute("SELECT * FROM mitra_pkl WHERE id = %s", (id_mitra,))
    mitra = cur.fetchone()
    if not mitra:
        print("Mitra tidak ditemukan.") 
        return

    konfirmasi = input(f"Yakin ingin menghapus mitra '{mitra[1]}'? (y/n): ")
    if konfirmasi.lower() == 'y':
        cur.execute("DELETE FROM mitra_pkl WHERE id = %s", (id_mitra,))
        conn.commit()
        print("Mitra berhasil dihapus.")

# Periode PKL
def kelola_data_periode(role, user_id):
    while True:
        conn = koneksi_db()
        cur = conn.cursor()
        cur.execute("SELECT id, nama_periode, tanggal_mulai, tanggal_selesai, status_aktif FROM periode_pkl ORDER BY id")
        data = cur.fetchall()
        cur.close()
        conn.close()

        print("\n=== KELOLA DATA PERIODE PKL ===")
        headers = ["ID", "Nama Periode", "Mulai", "Selesai", "Status"]
        print(tabulate(data, headers=headers, tablefmt="grid"))

        print("[1] Tambah Periode")
        print("[2] Edit Periode")
        print("[3] Hapus Periode")
        print("[0] Kembali")

        pilihan = input("Pilih menu: ")
        if pilihan == '1':
            tambah_periode()
        elif pilihan == '2':
            edit_periode()
        elif pilihan == '3':
            hapus_periode()
        elif pilihan == '0':
            show_menu(role, user_id)
            break
        else:
            print("Pilihan tidak valid.")
            
def tambah_periode():
    print("\n=== Tambah Periode PKL ===")
    nama = input("Nama Periode: ")
    mulai = input("Tanggal Mulai (YYYY-MM-DD): ")
    selesai = input("Tanggal Selesai (YYYY-MM-DD): ")
    status = input("Status Aktif (aktif/tidak aktif): ")

    conn = koneksi_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO periode_pkl (nama_periode, tanggal_mulai, tanggal_selesai, status_aktif) VALUES (%s, %s, %s, %s)",
        (nama, mulai, selesai, status)
    )
    conn.commit()
    cur.close()
    conn.close()
    print("Periode PKL berhasil ditambahkan.")

def edit_periode():
    print("\n=== Edit Periode PKL ===")
    id_edit = input("ID periode yang ingin diedit: ")

    conn = koneksi_db()
    cur = conn.cursor()
    cur.execute("SELECT nama_periode, tanggal_mulai, tanggal_selesai, status_aktif FROM periode_pkl WHERE id = %s", (id_edit,))
    data = cur.fetchone()
    if not data:
        print("Data tidak ditemukan.")
        return

    nama_baru = input(f"Nama Periode Baru (kosongkan untuk tetap: {data[0]}): ")
    mulai_baru = input(f"Tanggal Mulai Baru (kosongkan untuk tetap: {data[1]}): ")
    selesai_baru = input(f"Tanggal Selesai Baru (kosongkan untuk tetap: {data[2]}): ")
    status_baru = input(f"Status Baru (kosongkan untuk tetap: {data[3]}): ")

    nama = nama_baru if nama_baru else data[0]
    mulai = mulai_baru if mulai_baru else data[1]
    selesai = selesai_baru if selesai_baru else data[2]
    status = status_baru if status_baru else data[3]

    cur.execute("""
        UPDATE periode_pkl
        SET nama_periode = %s, tanggal_mulai = %s, tanggal_selesai = %s, status_aktif = %s
        WHERE id = %s
    """, (nama, mulai, selesai, status, id_edit))
    conn.commit()
    cur.close()
    conn.close()
    print("Periode PKL berhasil diedit.")

def hapus_periode():
    print("\n=== Hapus Periode PKL ===")
    id_hapus = input("ID periode yang ingin dihapus: ")

    conn = koneksi_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM periode_pkl WHERE id = %s", (id_hapus,))
    conn.commit()
    cur.close()
    conn.close()
    print("Periode PKL berhasil dihapus.")

def verifikasi_pengajuan_siswa(role, user_id):
    print("\n=== VERIFIKASI PENGAJUAN PKL ===")
    
    conn = koneksi_db()
    cur = conn.cursor()
    
    # Ambil semua data pengajuan dengan JOIN
    cur.execute("""
        SELECT p.id, u.nama AS nama_siswa, m.nama AS nama_mitra, pr.nama_periode, p.status_pendaftaran
        FROM pendaftaran_pkl p
        JOIN users u ON p.user_id = u.id
        JOIN mitra_pkl m ON p.mitra_id = m.id
        JOIN periode_pkl pr ON p.periode_id = pr.id
        WHERE u.role = 'siswa' AND p.status_pendaftaran = 'belum disetujui'
    """)
    
    data = cur.fetchall()
    
    if not data:
        print("Tidak ada pengajuan yang perlu diverifikasi.")
        return

    # Tampilkan data dalam tabel
    print("+----+----------------+----------------+-----------------+---------------------+")
    print("| ID | Nama Siswa     | Mitra PKL      | Periode         | Status Pendaftaran  |")
    print("+----+----------------+----------------+-----------------+---------------------+")
    for row in data:
        print(f"| {str(row[0]).ljust(2)} | {row[1].ljust(14)} | {row[2].ljust(14)} | {row[3].ljust(15)} | {row[4].ljust(19)} |")
    print("+----+----------------+----------------+-----------------+---------------------+")

    id_pengajuan = input("Masukkan ID pengajuan yang ingin disetujui: ")

    # Tampilkan daftar guru
    cur.execute("SELECT id, nama FROM users where role = 'guru'")
    daftar_guru = cur.fetchall()

    print("\nDaftar Guru Pembimbing:")
    for guru in daftar_guru:
        print(f"[{guru[0]}] {guru[1]}")

    guru_id = input("Masukkan ID Guru Pembimbing: ")

    # Update pengajuan
    cur.execute("""
        UPDATE pendaftaran_pkl 
        SET status_pendaftaran = 'disetujui', guru_id = %s 
        WHERE id = %s
    """, (guru_id, id_pengajuan))

    conn.commit()
    print("Pengajuan berhasil disetujui dan guru pembimbing ditetapkan.")
    show_menu(role, user_id)

# ROLE SISWA
def ajukan_pkl(role, user_id):
    conn = koneksi_db()
    cur = conn.cursor()

    print("\n=== AJUKAN PKL ===")

    # Tampilkan daftar periode aktif
    cur.execute("SELECT id, nama_periode FROM periode_pkl WHERE status_aktif = 'aktif'")
    periode = cur.fetchall()
    if not periode:
        print("Tidak ada periode aktif.")
        return

    print("\n-- Periode PKL Aktif --")
    print(tabulate(periode, headers=["ID", "Nama Periode"], tablefmt="grid"))

    periode_id = input("Masukkan ID Periode: ")

    # Tampilkan daftar mitra
    cur.execute("SELECT id, nama FROM mitra_pkl")
    mitra = cur.fetchall()
    print("\n-- Daftar Mitra PKL --")
    print(tabulate(mitra, headers=["ID", "Nama Mitra"], tablefmt="grid"))

    mitra_id = input("Masukkan ID Mitra PKL: ")

    tanggal_daftar = datetime.today().strftime('%Y-%m-%d')
    status_pendaftaran = "belum disetujui"

    # Cek apakah siswa sudah pernah mengajukan
    cur.execute("SELECT * FROM pendaftaran_pkl WHERE user_id = %s AND periode_id = %s", (user_id, periode_id))
    if cur.fetchone():
        print("Kamu sudah mengajukan PKL untuk periode ini.")
        show_menu(role, user_id)
        return

    cur.execute("""
        INSERT INTO pendaftaran_pkl (user_id, periode_id, mitra_id, status_pendaftaran, tanggal_daftar)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, periode_id, mitra_id, status_pendaftaran, tanggal_daftar))

    conn.commit()
    cur.close()
    conn.close()
    print("Pengajuan PKL berhasil dikirim.")
    
    show_menu(role, user_id)

def lihat_status_verifikasi(role, user_id):
    conn = koneksi_db()
    cur = conn.cursor()

    print("\n=== STATUS VERIFIKASI PKL ===")

    query = """
        SELECT p.id, m.nama, m.alamat, m.kontak_person,
               per.nama_periode, per.tanggal_mulai, per.tanggal_selesai,
               p.status_pendaftaran, p.tanggal_daftar
        FROM pendaftaran_pkl p
        JOIN mitra_pkl m ON p.mitra_id = m.id
        JOIN periode_pkl per ON p.periode_id = per.id
        WHERE p.user_id = %s
        ORDER BY p.tanggal_daftar DESC
        LIMIT 1
    """
    cur.execute(query, (user_id,))
    result = cur.fetchone()

    if result:
        print(f"""
ID Pendaftaran     : {result[0]}
Nama Mitra         : {result[1]}
Alamat Mitra       : {result[2]}
Kontak Person      : {result[3]}
Periode PKL        : {result[4]}
Tanggal Mulai      : {result[5]}
Tanggal Selesai    : {result[6]}
Status Pendaftaran : {result[7]}
Tanggal Daftar     : {result[8]}
        """)
    else:
        print("Belum ada pengajuan PKL yang ditemukan.")

    # Kembali ke menu siswa
    show_menu(role, user_id)


# Semua role
def show_profile(role, user_id):
    conn = koneksi_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            print("Data pengguna tidak ditemukan.")
            return

        print("\n=== PROFIL ===")
        print(f"ID        : {user[0]}")
        print(f"Nama      : {user[1]}")
        print(f"Email     : {user[2]}")
        print(f"Kelas     : {user[4]}")
        print(f"No HP     : {user[5]}")
        print(f"No Induk  : {user[6]}")
        print(f"Role      : {user[7]}")

        print("\nPilih data yang ingin diubah:")
        print("[1] Nama")
        print("[2] Email")
        print("[3] Kelas")
        print("[4] No HP")
        print("[5] No Induk")
        print("[0] Kembali")

        pilihan = input("Pilihan: ")
        kolom = None
        if pilihan == '1':
            kolom = "nama"
        elif pilihan == '2':
            kolom = "email"
        elif pilihan == '3':
            kolom = "kelas"
        elif pilihan == '4':
            kolom = "no_hp"
        elif pilihan == '5':
            kolom = "no_induk"
        elif pilihan == '0':
            show_menu(role, user_id)
            return
        else:
            print("Pilihan tidak valid.")
            return

        nilai_baru = input(f"Masukkan {kolom} baru: ")
        cursor.execute(f"UPDATE users SET {kolom} = %s WHERE id = %s", (nilai_baru, user_id))
        conn.commit()
        print(f"{kolom} berhasil diperbarui.")
    except Exception as e:
        print("Terjadi kesalahan:", e)
    finally:
        cursor.close()
        conn.close()
        show_menu(role, user_id)

def main_menu():
    while True:
        print("\n=== SELAMAT DATANG DI SPKL ===")
        print("[1] Login")
        print("[2] Register")
        print("[9] Keluar")
        pilihan = input("Pilih menu: ")

        if pilihan == '1':
            login()
        elif pilihan == '2':
            register()
        elif pilihan == '9':
            print("Sampai jumpa!")
            break
        else:
            print("Pilihan tidak valid.")

# Jalankan program
if __name__ == "__main__":
    main_menu()
    
