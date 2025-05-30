import psycopg2
import re
import hashlib
from tabulate import tabulate
from datetime import datetime
from fpdf import FPDF

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

    print("\nJenis Akun:")
    print("[1] Siswa")
    print("[2] Guru")
    role = input("Pilih (1/2): ")

    if role == '1':
        kelas = input("Kelas: ")
        no_hp = input("No HP: ")
        nisn = input("NISN: ")
        try:
            cursor.execute("""
                INSERT INTO siswa (nama, email, password, kelas, no_hp, nisn)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nama, email, hash_password(password), kelas, no_hp, nisn))
            conn.commit()
            print("Registrasi siswa berhasil!\n")
        except psycopg2.Error as e:
            print("Registrasi gagal:", e)

    elif role == '2':
        nip = input("NIP: ")
        no_hp = input("No HP: ")
        try:
            cursor.execute("""
                INSERT INTO guru (nama, email, password, nip, no_hp)
                VALUES (%s, %s, %s, %s, %s)
            """, (nama, email, hash_password(password), nip, no_hp))
            conn.commit()
            print("Registrasi guru berhasil!\n")
        except psycopg2.Error as e:
            print("Registrasi gagal:", e)
    else:
        print("Pilihan tidak valid.")

    cursor.close()
    conn.close()

def login():
    print("\n=== LOGIN ===")
    conn = koneksi_db()
    cursor = conn.cursor()

    print("Login sebagai:")
    print("[1] Admin")
    print("[2] Guru")
    print("[3] Siswa")
    akun = input("Pilih (1/2/3): ").strip()

    if akun == '1':
        table = 'admin'
        role = 1
    elif akun == '2':
        table = 'guru'
        role = 2
    elif akun == '3':
        table = 'siswa'
        role = 3
    else:
        print("Pilihan tidak valid.")
        return

    email = input("Email: ").strip()
    password = input("Password: ").strip()

    try:
        cursor.execute(f"SELECT id, nama, password FROM {table} WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and user[2] == hash_password(password):
            print(f"Login berhasil! Selamat datang, {user[1]}")
            show_menu(role, user[0])
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
    if role == 3:
        print("[1] Ajukan PKL")
        print("[2] Lihat Status Verifikasi")
        print("[3] Cetak Surat Pengantar")
        print("[4] Buat Laporan")
        print("[5] Lihat Nilai Akhir")
    elif role == 2:
        print("[1] Lihat Laporan")
        print("[2] Beri Nilai Akhir")
    elif role == 1:
        print("[1] Kelola Data Guru")
        print("[2] Kelola Data Siswa")
        print("[3] Kelola Data Mitra PKL")
        print("[4] Kelola Data Periode PKL")
        print("[5] Verifikasi Pengajuan Siswa")
    else:
        print("Role tidak dikenali.")
        return
    print("[9] Logout")
    
    pilihan = input("Pilih menu: ")
    if pilihan == '0':
        show_profile(role, user_id)
    elif role == 1:
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
    elif role == 3:
        if pilihan == '1':
            ajukan_pkl(role, user_id)
        elif pilihan == '2':
            lihat_status_verifikasi(role, user_id)
        elif pilihan == '3':
            cetak_surat(role, user_id)
        elif pilihan == '4':
            buat_laporan(role, user_id)
        elif pilihan == '5':
            lihat_nilai_akhir(user_id)
        elif pilihan == '0':
            show_profile(role, user_id)
        elif pilihan == '9':
            main_menu()
    elif role == 2:
        if pilihan == '1':
            lihat_laporan(role, user_id)
        elif pilihan == '2':
            beri_nilai_akhir(role, user_id)
        elif pilihan == '9':
            main_menu()
    else:
        print("Fitur belum tersedia.")
        show_menu(role, user_id)
    return

def tampilkan_users(role):
    conn = koneksi_db()
    cur = conn.cursor()

    if role == 'siswa':
        query = "SELECT id, nama, email, no_hp, kelas FROM siswa ORDER BY id"
        headers = ["ID", "Nama", "Email", "No HP", "Kelas"]
    elif role == 'guru':
        query = "SELECT id, nama, email, no_hp, nip FROM guru ORDER BY id"
        headers = ["ID", "Nama", "Email", "No HP", "nip"]
    elif role == 'admin':
        query = "SELECT id, nama, email, no_hp FROM admin ORDER BY id"
        headers = ["ID", "Nama", "Email", "No HP"]
    else:
        print("Role tidak dikenali.")
        return

    try:
        cur.execute(query)
        data = cur.fetchall()
    except Exception as e:
        print("Gagal mengambil data:", e)
        data = []

    cur.close()
    conn.close()

    if not data:
        print(f"\nTidak ada data untuk role: {role}.")
    else:
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

def get_role_id(role_name):
    conn = koneksi_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM role WHERE role = %s", (role_name,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        return result[0]
    else:
        print(f"Role '{role_name}' tidak ditemukan.")
        return None

def tambah_user(role):
    if role not in ['admin', 'guru', 'siswa']:
        print("Role tidak dikenali.")
        return

    nama = input("Nama: ")
    email = input("Email: ")
    password = input("Password: ")
    no_hp = input("No HP: ")
    no_induk = input("No Induk: ")
    kelas = input("Kelas: ") if role == 'siswa' else None

    conn = koneksi_db()
    cur = conn.cursor()

    try:
        if role == 'siswa':
            query = """
                INSERT INTO siswa (nama, email, password, kelas, no_hp, nisn)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (nama, email, hash_password(password), kelas, no_hp, no_induk)
        elif role == 'guru':
            query = """
                INSERT INTO guru (nama, email, password, no_hp, nip)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (nama, email, hash_password(password), no_hp, no_induk)

        cur.execute(query, params)
        conn.commit()
        print(f"{role.capitalize()} berhasil ditambahkan.")
    except Exception as e:
        print("Gagal menambahkan:", e)
    finally:
        cur.close()
        conn.close()

def edit_user(role):
    if role not in ['admin', 'guru', 'siswa']:
        print("Role tidak dikenali.")
        return

    user_id = input(f"ID {role} yang ingin diedit: ")

    conn = koneksi_db()
    cur = conn.cursor()

    try:
        # Ambil data lama
        if role == 'siswa':
            cur.execute("SELECT nama, email, no_hp, kelas FROM siswa WHERE id = %s", (user_id,))
            user = cur.fetchone()
            if not user:
                print("Siswa tidak ditemukan.")
                return
            nama_lama, email_lama, no_hp_lama, kelas_lama = user
        else:
            cur.execute(f"SELECT nama, email, no_hp FROM {role} WHERE id = %s", (user_id,))
            user = cur.fetchone()
            if not user:
                print(f"{role.capitalize()} tidak ditemukan.")
                return
            nama_lama, email_lama, no_hp_lama = user

        nama_baru = input("Nama baru: ").strip() or nama_lama
        email_baru = input("Email baru: ").strip() or email_lama
        no_hp_baru = input("No HP baru: ").strip() or no_hp_lama
        if role == 'siswa':
            kelas_baru = input("Kelas baru: ").strip() or kelas_lama
            cur.execute("""
                UPDATE siswa SET nama = %s, email = %s, no_hp = %s, kelas = %s WHERE id = %s
            """, (nama_baru, email_baru, no_hp_baru, kelas_baru, user_id))
        else:
            cur.execute(f"""
                UPDATE {role} SET nama = %s, email = %s, no_hp = %s WHERE id = %s
            """, (nama_baru, email_baru, no_hp_baru, user_id))

        conn.commit()
        print(f"{role.capitalize()} berhasil diedit.")
    except Exception as e:
        print("Gagal mengedit:", e)
    finally:
        cur.close()
        conn.close()

def hapus_user(role):
    if role not in ['admin', 'guru', 'siswa']:
        print("Role tidak dikenali.")
        return

    user_id = input(f"ID {role} yang ingin dihapus: ")

    conn = koneksi_db()
    cur = conn.cursor()

    try:
        cur.execute(f"SELECT id FROM {role} WHERE id = %s", (user_id,))
        user = cur.fetchone()
        if not user:
            print(f"{role.capitalize()} dengan ID tersebut tidak ditemukan.")
            return

        confirm = input(f"Apakah Anda yakin ingin menghapus {role} dengan ID {user_id}? (y/n): ").lower()
        if confirm == 'y':
            cur.execute(f"DELETE FROM {role} WHERE id = %s", (user_id,))
            conn.commit()
            print(f"{role.capitalize()} berhasil dihapus.")
        else:
            print("Penghapusan dibatalkan.")
    except Exception as e:
        print("Gagal menghapus:", e)
    finally:
        cur.close()
        conn.close()


# Kelola mitra
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

# Kelola Periode PKL
def kelola_data_periode(role, user_id):
    while True:
        conn = koneksi_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id, p.nama_periode, p.tanggal_mulai, p.tanggal_selesai, s.status
            FROM periode_pkl p
            JOIN status_periode s ON p.status = s.id
            ORDER BY p.id
        """)
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
            
def get_status_options():
    conn = koneksi_db()
    cur = conn.cursor()
    cur.execute("SELECT id, status FROM status_periode")
    status_list = cur.fetchall()
    cur.close()
    conn.close()
    return status_list

def tambah_periode():
    print("\n=== Tambah Periode PKL ===")
    nama = input("Nama Periode: ")
    mulai = input("Tanggal Mulai (YYYY-MM-DD): ")
    selesai = input("Tanggal Selesai (YYYY-MM-DD): ")
    status = 1

    conn = koneksi_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO periode_pkl (nama_periode, tanggal_mulai, tanggal_selesai, status) VALUES (%s, %s, %s, %s)",
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
    cur.execute("SELECT nama_periode, tanggal_mulai, tanggal_selesai, status FROM periode_pkl WHERE id = %s", (id_edit,))
    data = cur.fetchone()
    if not data:
        print("Data tidak ditemukan.")
        return

    nama_baru = input(f"Nama Periode Baru (kosongkan untuk tetap: {data[0]}): ")
    mulai_baru = input(f"Tanggal Mulai Baru (kosongkan untuk tetap: {data[1]}): ")
    selesai_baru = input(f"Tanggal Selesai Baru (kosongkan untuk tetap: {data[2]}): ")

    # data_status = cur.execute("SELECT nama_periode, tanggal_mulai, tanggal_selesai, status FROM periode_pkl WHERE id = %s", (id_edit,))

    # Penyesuaian untuk status
    print("Status (kosongkan untuk tetap aktif atau ketik 'n' untuk tidak aktif.)")
    if data[3] == 1:
        data_status = 'aktif'
    else:
        data_status = 'tidak aktif'
    status_input = input(f"Status (saat ini: {data_status}): ").lower().strip()
    if status_input == 'n':
        status_baru = '2'  # ID status 'tidak aktif'
    elif status_input == '':
        status_baru = data[3]  # Tetap seperti sebelumnya
    else:
        status_baru = status_input  # Gunakan input apa adanya (misal langsung input ID)

    nama = nama_baru if nama_baru else data[0]
    mulai = mulai_baru if mulai_baru else data[1]
    selesai = selesai_baru if selesai_baru else data[2]
    status = status_baru

    cur.execute("""
        UPDATE periode_pkl
        SET nama_periode = %s, tanggal_mulai = %s, tanggal_selesai = %s, status = %s
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

# Kelola verifikasi siswa
def verifikasi_pengajuan_siswa(role, user_id):
    print("\n=== VERIFIKASI PENGAJUAN PKL ===")
    
    conn = koneksi_db()
    cur = conn.cursor()

    # Ambil data pengajuan yang masih menunggu persetujuan
    cur.execute("""
        SELECT p.id, s.nama AS nama_siswa, m.nama AS nama_mitra, pr.nama_periode, p.status_pendaftaran
        FROM pendaftaran_pkl p
        JOIN siswa s ON p.siswa_id = s.id
        JOIN mitra_pkl m ON p.mitra_id = m.id
        JOIN periode_pkl pr ON p.periode_id = pr.id
        WHERE p.status_pendaftaran = '1'
    """)

    data = cur.fetchall()

    if not data:
        print("Tidak ada pengajuan yang perlu diverifikasi.")
        return show_menu(role, user_id)

    # Tampilkan daftar pengajuan
    print("+----+----------------+----------------+-----------------+---------------------+")
    print("| ID | Nama Siswa     | Mitra PKL      | Periode         | Status Pendaftaran  |")
    print("+----+----------------+----------------+-----------------+---------------------+")
    for row in data:
        print(f"| {str(row[0]).ljust(2)} | {row[1].ljust(14)} | {row[2].ljust(14)} | {row[3].ljust(15)} | {'Menunggu'.ljust(19)} |")
    print("+----+----------------+----------------+-----------------+---------------------+")

    try:
        id_pengajuan = int(input("Masukkan ID pengajuan yang ingin disetujui: "))
    except ValueError:
        print("❌ ID tidak valid.")
        return show_menu(role, user_id)

    # Periksa apakah ID pengajuan valid
    cur.execute("SELECT id FROM pendaftaran_pkl WHERE id = %s AND status_pendaftaran = '1'", (id_pengajuan,))
    cek_pengajuan = cur.fetchone()
    if not cek_pengajuan:
        print("❌ ID pengajuan tidak ditemukan atau sudah disetujui.")
        return show_menu(role, user_id)

    # Tampilkan daftar guru pembimbing dari tabel guru
    cur.execute("SELECT id, nama FROM guru")
    daftar_guru = cur.fetchall()

    if not daftar_guru:
        print("❌ Tidak ada guru pembimbing yang tersedia.")
        return show_menu(role, user_id)

    print("\nDaftar Guru Pembimbing:")
    for guru in daftar_guru:
        print(f"[{guru[0]}] {guru[1]}")

    try:
        guru_id = int(input("Masukkan ID Guru Pembimbing: "))
    except ValueError:
        print("❌ ID guru tidak valid.")
        return show_menu(role, user_id)

    # Periksa apakah guru tersedia
    cur.execute("SELECT id FROM guru WHERE id = %s", (guru_id,))
    cek_guru = cur.fetchone()
    if not cek_guru:
        print("❌ Guru dengan ID tersebut tidak ditemukan.")
        return show_menu(role, user_id)

    # Setujui pengajuan dan tetapkan guru
    try:
        cur.execute("""
            UPDATE pendaftaran_pkl 
            SET status_pendaftaran = 2, guru_id = %s 
            WHERE id = %s
        """, (guru_id, id_pengajuan))
        conn.commit()
        print("✅ Pengajuan berhasil disetujui dan guru pembimbing ditetapkan.")
    except Exception as e:
        print("❌ Gagal memperbarui data:", e)
    finally:
        conn.close()

    show_menu(role, user_id)



# ROLE SISWA
def ajukan_pkl(role, user_id):
    conn = koneksi_db()
    cur = conn.cursor()

    print("\n=== AJUKAN PKL ===")

    # Tampilkan daftar periode aktif
    cur.execute("SELECT id, nama_periode, tanggal_mulai, tanggal_selesai FROM periode_pkl WHERE status = 1")
    periode = cur.fetchall()
    if not periode:
        print("Tidak ada periode aktif.")
        return

    print("\n-- Periode PKL Aktif --")
    print(tabulate(periode, headers=["ID", "Nama Periode", "Mulai", "Selesai"], tablefmt="grid"))

    periode_id = input("Masukkan ID Periode: ")

    # Tampilkan daftar mitra
    cur.execute("SELECT id, nama, alamat, kontak_person, kuota FROM mitra_pkl")
    mitra = cur.fetchall()
    print("\n-- Daftar Mitra PKL --")
    print(tabulate(mitra, headers=["ID", "Nama Mitra", "Alamat", "Kontak Person", "Kuota"], tablefmt="grid"))

    mitra_id = input("Masukkan ID Mitra PKL: ")

    tanggal_daftar = datetime.today().strftime('%Y-%m-%d')
    status_pendaftaran = 1  # diasumsikan sesuai ID di tabel status_pendaftaran

    # Cek apakah siswa sudah pernah mengajukan
    cur.execute("SELECT * FROM pendaftaran_pkl WHERE siswa_id = %s AND periode_id = %s", (user_id, periode_id))
    if cur.fetchone():
        print("Kamu sudah mengajukan PKL untuk periode ini.")
        show_menu(role, user_id)
        return

    # Cek kuota mitra
    cur.execute("SELECT kuota FROM mitra_pkl WHERE id = %s", (mitra_id,))
    kuota_row = cur.fetchone()
    if not kuota_row:
        print("Mitra tidak ditemukan.")
        show_menu(role, user_id)
        return

    kuota = kuota_row[0]

    # Hitung jumlah pendaftar di mitra tersebut dan periode tersebut
    cur.execute("""
        SELECT COUNT(*) FROM pendaftaran_pkl
        WHERE mitra_id = %s AND periode_id = %s
    """, (mitra_id, periode_id))
    jumlah_pendaftar = cur.fetchone()[0]

    if jumlah_pendaftar >= kuota:
        print(f"Kuota untuk mitra ini sudah penuh. (Kuota: {kuota}, Pendaftar: {jumlah_pendaftar})")
        show_menu(role, user_id)
        return

    # Simpan pendaftaran
    cur.execute("""
        INSERT INTO pendaftaran_pkl (siswa_id, periode_id, mitra_id, status_pendaftaran, tanggal_daftar, guru_id)
        VALUES (%s, %s, %s, %s, %s, NULL)
    """, (user_id, periode_id, mitra_id, status_pendaftaran, tanggal_daftar))

    conn.commit()
    cur.close()
    conn.close()
    print("Pengajuan PKL berhasil dikirim.")
    
    show_menu(role, user_id)
    
def lihat_status_verifikasi(role, user_id):
    conn = koneksi_db()
    cur = conn.cursor()

    print("\n=== DAFTAR PENDAFTARAN PKL ===")

    # Ambil semua data pendaftaran berdasarkan user
    query = """
        SELECT p.id, per.nama_periode, m.nama AS nama_mitra, p.status_pendaftaran, p.tanggal_daftar
        FROM pendaftaran_pkl p
        JOIN mitra_pkl m ON p.mitra_id = m.id
        JOIN periode_pkl per ON p.periode_id = per.id
        WHERE p.siswa_id = %s
        ORDER BY p.tanggal_daftar DESC
    """
    cur.execute(query, (user_id,))
    results = cur.fetchall()

    if not results:
        print("Belum ada pengajuan PKL yang ditemukan.")
        show_menu(role, user_id)
        return

    # Tampilkan daftar dalam bentuk tabel
    print("+----+-------------------+----------------+---------------------+------------------+")
    print("| ID | Periode           | Mitra          | Status Pendaftaran  | Tanggal Daftar   |")
    print("+----+-------------------+----------------+---------------------+------------------+")
    for row in results:
        id_pendaftaran = str(row[0]).ljust(2)
        periode = str(row[1]).ljust(17)
        mitra = str(row[2]).ljust(14)
        status = "belum disetujui" if row[3] == 1 else "disetujui" if row[3] == 2 else "ditolak"
        tanggal = str(row[4])
        print(f"| {id_pendaftaran} | {periode} | {mitra} | {status}     | {tanggal}         |")

    print("+----+-------------------+----------------+---------------------+------------------+")

    # Pilih salah satu untuk lihat detail
    id_pilihan = input("Masukkan ID pendaftaran yang ingin dilihat detailnya: ")

    # Ambil data detail berdasarkan ID pilihan
    detail_query = """
        SELECT p.id, m.nama, m.alamat, m.kontak_person,
               per.nama_periode, per.tanggal_mulai, per.tanggal_selesai,
               p.status_pendaftaran, p.tanggal_daftar
        FROM pendaftaran_pkl p
        JOIN mitra_pkl m ON p.mitra_id = m.id
        JOIN periode_pkl per ON p.periode_id = per.id
        WHERE p.id = %s AND p.siswa_id = %s
    """
    cur.execute(detail_query, (id_pilihan, user_id))
    detail = cur.fetchone()
    status = "belum disetujui" if detail[7] == 1 else "disetujui" if detail[7] == 2 else "ditolak"

    if detail:
        print("\n=== DETAIL PENDAFTARAN PKL ===")
        print(f"""
ID Pendaftaran     : {detail[0]}
Nama Mitra         : {detail[1]}
Alamat Mitra       : {detail[2]}
Kontak Person      : {detail[3]}
Periode PKL        : {detail[4]}
Tanggal Mulai      : {detail[5]}
Tanggal Selesai    : {detail[6]}
Status Pendaftaran : {status}
Tanggal Daftar     : {detail[8]}
        """)
    else:
        print("ID pendaftaran tidak ditemukan atau tidak sesuai dengan akun Anda.")

    # Kembali ke menu siswa
    show_menu(role, user_id)

def cetak_surat(role, user_id):
    conn = koneksi_db()
    cur = conn.cursor()

    # Ambil semua pendaftaran user
    query = """
        SELECT p.id, per.nama_periode, m.nama AS nama_mitra, p.status_pendaftaran
        FROM pendaftaran_pkl p
        JOIN mitra_pkl m ON p.mitra_id = m.id
        JOIN periode_pkl per ON p.periode_id = per.id
        WHERE p.siswa_id = %s
        ORDER BY p.tanggal_daftar DESC
    """
    cur.execute(query, (user_id,))
    results = cur.fetchall()

    if not results:
        print("Belum ada data pendaftaran PKL.")
        return

    # Tampilkan daftar pendaftaran
    print("\n=== DAFTAR PKL UNTUK CETAK SURAT ===")
    print("+----+-------------------+----------------+---------------------+")
    print("| ID | Periode           | Mitra          | Status Pendaftaran  |")
    print("+----+-------------------+----------------+---------------------+")
    for row in results:
        status = "belum disetujui" if row[3] == 1 else "disetujui" if row[3] == 2 else "ditolak"
        print(f"| {str(row[0]).ljust(2)} | {row[1].ljust(17)} | {row[2].ljust(14)} | {status.ljust(19)} |")
    print("+----+-------------------+----------------+---------------------+")

    id_pendaftaran = input("Masukkan ID pendaftaran yang ingin dicetak suratnya: ")

    # Ambil data detail untuk surat, termasuk status
    detail_query = """
        SELECT u.nama, u.nisn, m.nama, m.alamat, m.kontak_person, 
               per.nama_periode, per.tanggal_mulai, per.tanggal_selesai, p.id, p.status_pendaftaran
        FROM pendaftaran_pkl p
        JOIN siswa u ON p.siswa_id = u.id
        JOIN mitra_pkl m ON p.mitra_id = m.id
        JOIN periode_pkl per ON p.periode_id = per.id
        WHERE p.id = %s AND p.siswa_id = %s
    """
    cur.execute(detail_query, (id_pendaftaran, user_id))
    data = cur.fetchone()

    if not data:
        print("Data tidak ditemukan atau tidak sesuai.")
        return

    # Ambil data
    nama_user, no_induk, nama_mitra, alamat_mitra, kontak, periode, tgl_mulai, tgl_selesai, id_pendaftar, status_pendaftaran = data

    # Cek status
    if status_pendaftaran != 2:
        print("Pengajuan belum disetujui. Surat tidak dapat dicetak.")
        show_menu(role, user_id)
        return

    # Format tanggal
    tgl_mulai_fmt = tgl_mulai.strftime("%d-%m-%Y")
    tgl_selesai_fmt = tgl_selesai.strftime("%d-%m-%Y")

    # Buat PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "SURAT PENGANTAR PRAKTIK KERJA LAPANGAN (PKL)", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, f"""
Dengan hormat,

Sehubungan dengan pelaksanaan kegiatan Praktik Kerja Lapangan (PKL), kami dari sekolah memberikan pengantar kepada siswa berikut:

Nama     : {nama_user}
NISN     : {no_induk}
Periode  : {periode} ({tgl_mulai_fmt} s.d {tgl_selesai_fmt})

Untuk melaksanakan PKL di:

Mitra    : {nama_mitra}
Alamat   : {alamat_mitra}
Kontak   : {kontak}

Demikian surat ini dibuat untuk digunakan sebagaimana mestinya.

Hormat kami,



Panitia PKL
""")

    # Simpan file PDF
    nama_file = f"{id_pendaftar}_{nama_user.replace(' ', '_')}.pdf"
    pdf.output(nama_file)
    print(f"Surat pengantar berhasil dicetak: {nama_file}")
    show_menu(role, user_id)
    
def buat_laporan(role, user_id):
    import psycopg2
    conn = koneksi_db()
    cur = conn.cursor()

    print("\n=== BUAT LAPORAN PKL ===")

    # Tampilkan daftar pendaftaran PKL siswa
    query_pkl = """
        SELECT p.id, m.nama, per.nama_periode, p.status_pendaftaran
        FROM pendaftaran_pkl p
        JOIN mitra_pkl m ON p.mitra_id = m.id
        JOIN periode_pkl per ON p.periode_id = per.id
        WHERE p.siswa_id = %s
    """
    cur.execute(query_pkl, (user_id,))
    pkl_list = cur.fetchall()

    if not pkl_list:
        print("❌ Kamu belum pernah mendaftar PKL.")
        return

    # Tampilkan daftar PKL
    print("+----+--------------------+--------------------+")
    print("| ID | Nama Mitra         | Periode            |")
    print("+----+--------------------+--------------------+")
    for pkl in pkl_list:
        print(f"| {str(pkl[0]).ljust(2)} | {pkl[1].ljust(18)} | {pkl[2].ljust(18)} |")
    print("+----+--------------------+--------------------+")

    try:
        pkl_id = int(input("Masukkan ID Pendaftaran PKL | [0] untuk batalkan: "))
        if pkl_id == 0:
            return show_menu(role, user_id)
    except ValueError:
        print("❌ ID tidak valid.")
        return buat_laporan(role, user_id)

    # Cek apakah pendaftaran sudah disetujui
    cur.execute("SELECT status_pendaftaran FROM pendaftaran_pkl WHERE id = %s AND siswa_id = %s", (pkl_id, user_id))
    status = cur.fetchone()
    if not status:
        print("❌ Pendaftaran tidak ditemukan.")
        return buat_laporan(role, user_id)

    if status[0] == 1:  # Belum disetujui
        print("❌ Pendaftaran PKL ini belum disetujui. Kamu belum bisa membuat laporan.")
        return show_menu(role, user_id)

    # Tampilkan semua laporan sebelumnya
    query_laporan = """
        SELECT id, tanggal, kegiatan, catatan, nilai
        FROM laporan_pkl
        WHERE siswa_id = %s AND pendaftaran_pkl = %s
        ORDER BY tanggal DESC
    """
    cur.execute(query_laporan, (user_id, pkl_id))
    laporan_list = cur.fetchall()

    if laporan_list:
        print("\n=== Laporan Sebelumnya ===")
        print("+----+------------+------------------------------+----------------+---------+")
        print("| ID | Tanggal    | Kegiatan                     | Catatan        | Nilai   |")
        print("+----+------------+------------------------------+----------------+---------+")
        for lap in laporan_list:
            print(f"| {str(lap[0]).ljust(2)} | {str(lap[1])} | {lap[2][:28].ljust(28)} | {lap[3][:14].ljust(14)} |  {lap[4]} |")
        print("+----+------------+------------------------------+----------------+---------+")
    else:
        print("ℹ️  Belum ada laporan untuk pendaftaran ini.")

    # Menu aksi
    print("\nPilih aksi:")
    print("[1] Tambah Laporan Baru")
    print("[2] Edit Laporan Sebelumnya")
    print("[3] Hapus Laporan")
    print("[0] Kembali")

    aksi = input("Pilihan: ")

    if aksi == '1':
        tanggal = input("Masukkan tanggal (YYYY-MM-DD): ")
        kegiatan = input("Masukkan kegiatan harian PKL: ")
        catatan = input("Masukkan catatan tambahan: ")

        try:
            query_insert = """
                INSERT INTO laporan_pkl (siswa_id, tanggal, kegiatan, catatan, pendaftaran_pkl)
                VALUES (%s, %s, %s, %s, %s)
            """
            cur.execute(query_insert, (user_id, tanggal, kegiatan, catatan, pkl_id))
            conn.commit()
            print("✅ Laporan berhasil ditambahkan.\n")
        except Exception as e:
            print("❌ Terjadi kesalahan saat menyimpan laporan:", e)

        return buat_laporan(role, user_id)

    elif aksi == '2':
        try:
            edit_id = int(input("Masukkan ID laporan yang ingin diedit: "))
            cur.execute("SELECT tanggal, kegiatan, catatan FROM laporan_pkl WHERE id = %s AND siswa_id = %s", (edit_id, user_id))
            existing = cur.fetchone()

            if not existing:
                print("❌ Laporan tidak ditemukan.")
                return buat_laporan(role, user_id)

            tanggal_lama, kegiatan_lama, catatan_lama = existing

            tanggal = input(f"Masukkan tanggal baru (Enter untuk tetap '{tanggal_lama}'): ") or tanggal_lama
            kegiatan = input(f"Masukkan kegiatan baru (Enter untuk tetap '{kegiatan_lama}'): ") or kegiatan_lama
            catatan = input(f"Masukkan catatan baru (Enter untuk tetap '{catatan_lama}'): ") or catatan_lama

            query_update = """
                UPDATE laporan_pkl
                SET tanggal = %s, kegiatan = %s, catatan = %s
                WHERE id = %s AND siswa_id = %s
            """
            cur.execute(query_update, (tanggal, kegiatan, catatan, edit_id, user_id))
            conn.commit()
            print("✅ Laporan berhasil diperbarui.\n")
            show_menu(role, user_id)
        except Exception as e:
            print("❌ Gagal memperbarui laporan:", e)

        return buat_laporan(role, user_id)

    elif aksi == '3':
        try:
            del_id = int(input("Masukkan ID laporan yang ingin dihapus: "))
            query_delete = "DELETE FROM laporan_pkl WHERE id = %s AND siswa_id = %s"
            cur.execute(query_delete, (del_id, user_id))
            conn.commit()
            print("✅ Laporan berhasil dihapus.\n")
        except Exception as e:
            print("❌ Gagal menghapus laporan:", e)

        return buat_laporan(role, user_id)

    elif aksi == '0':
        show_menu(role, user_id)

    else:
        print("❌ Pilihan tidak valid.\n")
        return buat_laporan(role, user_id)

    conn.close()

def lihat_nilai_akhir(user_id):
    conn = koneksi_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT g.nama AS nama_guru, p.nilai, p.catatan_evaluasi
            FROM penilaian p
            JOIN guru g ON p.guru_id = g.id
            WHERE p.siswa_id = %s
        """, (user_id,))
        
        data = cursor.fetchall()

        print("\n=== NILAI AKHIR PKL ===")
        if not data:
            print("❌ Belum ada penilaian yang tersedia.")
        else:
            print("+----------------------+--------+--------------------------------------+")
            print("| Guru Pembimbing      | Nilai  | Catatan Evaluasi                     |")
            print("+----------------------+--------+--------------------------------------+")
            for row in data:
                guru = row[0][:20].ljust(20)
                nilai = str(row[1]).ljust(6)
                catatan = (row[2][:35] + "...") if len(row[2]) > 35 else row[2].ljust(35)
                print(f"| {guru} | {nilai} | {catatan} |")
            print("+----------------------+--------+--------------------------------------+")

    except Exception as e:
        print("❌ Terjadi kesalahan saat mengambil nilai:", e)
    finally:
        cursor.close()
        conn.close()
        input("\nTekan Enter untuk kembali ke menu...")
        show_menu(3, user_id)



# ROLE GURU
def lihat_laporan(role, user_id):
    conn = koneksi_db()
    cur = conn.cursor()

    print("\n=== DAFTAR LAPORAN SISWA BIMBINGAN ===")

    query = """
        SELECT l.id, u.nama AS nama_siswa, m.nama AS nama_mitra, l.tanggal, l.kegiatan, l.nilai
        FROM laporan_pkl l
        JOIN pendaftaran_pkl p ON l.pendaftaran_pkl = p.id
        JOIN siswa u ON p.siswa_id = u.id
        JOIN mitra_pkl m ON p.mitra_id = m.id
        WHERE p.guru_id = %s
        ORDER BY l.tanggal DESC
    """
    cur.execute(query, (user_id,))
    laporan_list = cur.fetchall()

    if not laporan_list:
        print("Belum ada laporan dari siswa bimbingan Anda.\n")
        return show_menu(role, user_id)

    print("+----+--------------------+----------------------+------------+----------------------------+--------+")
    print("| ID | Nama Siswa         | Mitra PKL            | Tanggal    | Kegiatan                   | Nilai  |")
    print("+----+--------------------+----------------------+------------+----------------------------+--------+")
    for lap in laporan_list:
        nilai = str(lap[5]) if lap[5] is not None else "-"
        print(f"| {str(lap[0]).ljust(2)} | {lap[1][:20].ljust(20)} | {lap[2][:20].ljust(20)} | {lap[3]} | {lap[4][:26].ljust(26)} | {nilai.center(6)} |")
    print("+----+--------------------+----------------------+------------+----------------------------+--------+")


    # Pilih untuk lihat detail
    try:
        laporan_id = int(input("\nMasukkan ID laporan untuk melihat detail (0 untuk kembali): "))
        if laporan_id == 0:
            return show_menu(role, user_id)
    except ValueError:
        print("ID tidak valid.")
        return lihat_laporan(role, user_id)

   # Ambil detail laporan
    detail_query = """
        SELECT l.id, u.nama, m.nama, l.tanggal, l.kegiatan, l.catatan, l.nilai
        FROM laporan_pkl l
        JOIN pendaftaran_pkl p ON l.pendaftaran_pkl = p.id
        JOIN siswa u ON p.siswa_id = u.id
        JOIN mitra_pkl m ON p.mitra_id = m.id
        WHERE l.id = %s AND p.guru_id = %s
    """
    cur.execute(detail_query, (laporan_id, user_id))
    detail = cur.fetchone()

    if detail:
        nilai_saat_ini = detail[6] if detail[6] else "-"
        print(f"""
        === DETAIL LAPORAN ===
        ID Laporan   : {detail[0]}
        Nama Siswa   : {detail[1]}
        Mitra PKL    : {detail[2]}
        Tanggal      : {detail[3]}
        Kegiatan     : {detail[4]}
        Catatan      : {detail[5]}
        Nilai        : {nilai_saat_ini}
        """)

        ubah = input("Ingin memberikan/mengubah nilai? (y/n): ").lower()
        if ubah == 'y':
            nilai_baru = input("Masukkan nilai baru: ").strip()
            if nilai_baru:
                try:
                    nilai_baru_int = int(nilai_baru)
                    if 0 <= nilai_baru_int <= 100:
                        cur.execute("UPDATE laporan_pkl SET nilai = %s WHERE id = %s", (nilai_baru_int, laporan_id))
                        conn.commit()
                        print("✅ Nilai berhasil disimpan.")
                    else:
                        print("❌ Nilai harus antara 0 hingga 100.")
                except ValueError:
                    print("❌ Nilai harus berupa angka.")
        else:
            print("Tidak jadi melakukan edit nilai siswa")


    input("\nTekan Enter untuk kembali...")
    return lihat_laporan(role, user_id)

def beri_nilai_akhir(role, user_id):
    conn = koneksi_db()
    cur = conn.cursor()

    print("\n=== PENILAIAN AKHIR SISWA BIMBINGAN ===")

    # 1. Tampilkan daftar siswa yang dibimbing
    query = """
        SELECT 
        p.id, u.nama, m.nama, per.nama_periode, per.tanggal_mulai, per.tanggal_selesai,
        pn.nilai
        FROM pendaftaran_pkl p
        JOIN siswa u ON p.siswa_id = u.id
        JOIN mitra_pkl m ON p.mitra_id = m.id
        JOIN periode_pkl per ON p.periode_id = per.id
        LEFT JOIN penilaian pn ON pn.siswa_id = p.id AND pn.guru_id = %s
        WHERE p.guru_id = %s
    """
    cur.execute(query, (user_id, user_id))
    siswa_list = cur.fetchall()


    if not siswa_list:
        print("Belum ada siswa bimbingan.")
        input("\nTekan Enter untuk kembali...")
        return show_menu(role, user_id)
    print("+----+--------------------+--------------------+----------------------+------------+------------+--------+")
    print("| ID | Nama Siswa         | Mitra PKL          | Periode              | Mulai      | Selesai    | Nilai  |")
    print("+----+--------------------+--------------------+----------------------+------------+------------+--------+")
    for s in siswa_list:
        nilai = s[6] if s[6] is not None else '-'  # Indeks ke-6 sesuai kolom nilai
        print(f"| {str(s[0]).ljust(2)} | {s[1][:20].ljust(20)} | {s[2][:20].ljust(20)} | {s[3][:20].ljust(20)} | {s[4]} | {s[5]} | {str(nilai).center(5)} |")
    print("+----+--------------------+--------------------+----------------------+------------+------------+--------+")


    # 2. Pilih siswa untuk dinilai
    try:
        siswa_id = int(input("\nMasukkan ID siswa yang ingin dinilai (0 untuk kembali): "))
        if siswa_id == 0:
            return show_menu(role, user_id)
    except ValueError:
        print("❌ ID tidak valid.")
        return beri_nilai_akhir(role, user_id)

    # Pastikan siswa adalah bimbingan user
    cur.execute("""
        SELECT 
            p.id, u.nama, m.nama, per.nama_periode, per.tanggal_mulai, per.tanggal_selesai
        FROM pendaftaran_pkl p
        JOIN siswa u ON p.siswa_id = u.id
        JOIN mitra_pkl m ON p.mitra_id = m.id
        JOIN periode_pkl per ON p.periode_id = per.id
        WHERE p.id = %s AND p.guru_id = %s
    """, (siswa_id, user_id))
    siswa = cur.fetchone()


    if not siswa:
        print("❌ Siswa tidak ditemukan atau bukan bimbingan Anda.")
        input("\nTekan Enter untuk kembali...")
        return beri_nilai_akhir(role, user_id)

    print(f"""
    === DETAIL SISWA ===
    ID Pendaftaran : {siswa[0]}
    Nama Siswa     : {siswa[1]}
    Mitra PKL      : {siswa[2]}
    Periode        : {siswa[3]}
    Tanggal Mulai  : {siswa[4]}
    Tanggal Selesai: {siswa[5]}
    """)


    # 3. Masukkan nilai dan catatan evaluasi
    try:
        nilai = int(input("Masukkan nilai akhir / edit (0-100): "))
        if not (0 <= nilai <= 100):
            print("❌ Nilai harus antara 0 sampai 100.")
            return beri_nilai_akhir(role, user_id)
    except ValueError:
        print("❌ Nilai harus berupa angka.")
        return beri_nilai_akhir(role, user_id)

    catatan = input("Masukkan catatan evaluasi (opsional): ").strip()

    # Cek apakah penilaian sudah ada
    cur.execute("SELECT id FROM penilaian WHERE siswa_id = %s AND guru_id = %s", (siswa_id, user_id))
    existing = cur.fetchone()

    try:
        if existing:
            cur.execute("""
                UPDATE penilaian SET nilai = %s, catatan_evaluasi = %s WHERE id = %s
            """, (nilai, catatan, existing[0]))
            print("✅ Penilaian berhasil diperbarui.")
        else:
            cur.execute("""
                INSERT INTO penilaian (siswa_id, guru_id, nilai, catatan_evaluasi)
                VALUES (%s, %s, %s, %s)
            """, (siswa_id, user_id, nilai, catatan))
            print("✅ Penilaian berhasil disimpan.")

        conn.commit()
    except Exception as e:
        print("❌ Terjadi kesalahan saat menyimpan penilaian:", e)

    input("\nTekan Enter untuk kembali...")
    return show_menu(role, user_id)

# Semua role
def show_profile(role, user_id):
    conn = koneksi_db()
    cursor = conn.cursor()

    try:
        # Tentukan nama tabel berdasarkan role
        if role == 1:  # Admin
            table = "admin"
            fields = ("ID", "Nama", "Email", "-", "No HP", "-", "Role")
        elif role == 2:  # Guru
            table = "guru"
            fields = ("ID", "Nama", "Email", "-", "No HP", "NIP", "Guru")
        elif role == 3:  # Siswa
            table = "siswa"
            fields = ("ID", "Nama", "Email", "Kelas", "No HP", "NISN", "Siswa")
        else:
            print("❌ Role tidak dikenali.")
            return

        cursor.execute(f"SELECT * FROM {table} WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            print("❌ Data pengguna tidak ditemukan.")
            return

        print("\n=== PROFIL ===")
        print(f"ID        : {user[0]}")
        print(f"Nama      : {user[1]}")
        print(f"Email     : {user[2]}")
        if role == 3:
            print(f"Kelas     : {user[4]}")
            print(f"No HP     : {user[5]}")
            print(f"NISN      : {user[6]}")
        elif role == 2:
            print(f"No HP     : {user[5]}")
            print(f"NIP       : {user[4]}")

        print("\nPilih data yang ingin diubah:")
        print("[1] Nama")
        print("[2] Email")
        if role == 3:
            print("[3] Kelas")
            print("[4] No HP")
            print("[5] NISN")
        elif role == 2:
            print("[3] NIP")
            print("[4] No HP")
        print("[0] Kembali")

        pilihan = input("Pilihan: ")
        kolom = None

        if pilihan == '1':
            kolom = "nama"
        elif pilihan == '2':
            kolom = "email"
        elif role == 3:
            if pilihan == '3':
                kolom = "kelas"
            elif pilihan == '4':
                kolom = "no_hp"
            elif pilihan == '5':
                kolom = "nisn"
        elif role == 2:
            if pilihan == '3':
                kolom = "nip"
            elif pilihan == '4':
                kolom = "no_hp"
        elif pilihan == '0':
            return show_menu(role, user_id)
        else:
            print("❌ Pilihan tidak valid.")
            return

        if kolom:
            nilai_baru = input(f"Masukkan {kolom} baru: ")
            cursor.execute(f"UPDATE {table} SET {kolom} = %s WHERE id = %s", (nilai_baru, user_id))
            conn.commit()
            print(f"✅ {kolom} berhasil diperbarui.")

    except Exception as e:
        print("❌ Terjadi kesalahan:", e)
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