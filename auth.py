import re
import hashlib
import psycopg2
from koneksi import koneksi_db
from menu import show_menu 
from cls import clear_screen

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register():
    clear_screen()

    conn = koneksi_db()       
    cur = conn.cursor() 
    print("\n=== REGISTRASI ===")

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
            cur.execute("""
                INSERT INTO siswa (nama_siswa, email_siswa, password_siswa, kelas_siswa, no_hp_siswa, nisn)
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
            cur.execute("""
                INSERT INTO guru (nama_guru, email_guru, password_guru, nip, no_hp_guru)
                VALUES (%s, %s, %s, %s, %s)
            """, (nama, email, hash_password(password), nip, no_hp))
            conn.commit()
            print("Registrasi guru berhasil!\n")
        except psycopg2.Error as e:
            print("Registrasi gagal:", e)
    else:
        print("Pilihan tidak valid.")

    cur.close()
    conn.close()

def login():
    clear_screen()

    print("\n=== LOGIN ===")
    
    conn = koneksi_db()       
    cur = conn.cursor() 
    
    print("Login sebagai:")
    print("[1] Admin")
    print("[2] Guru")
    print("[3] Siswa")
    akun = input("Pilih (1/2/3): ").strip()

    if akun == '1':
        table = 'admin'
        email_field = 'email_admin'
        password_field = 'password_admin'
        id_field = 'id_admin'
        name_field = 'nama_admin'
        role = 1
    elif akun == '2':
        table = 'guru'
        email_field = 'email_guru'
        password_field = 'password_guru'
        id_field = 'id_guru'
        name_field = 'nama_guru'
        role = 2
    elif akun == '3':
        table = 'siswa'
        email_field = 'email_siswa'
        password_field = 'password_siswa'
        id_field = 'id_siswa'
        name_field = 'nama_siswa'
        role = 3
    else:
        print("Pilihan tidak valid.")
        return

    email = input("Email: ").strip()
    password = input("Password: ").strip()

    try:
        query = f"SELECT {id_field}, {name_field}, {password_field} FROM {table} WHERE {email_field} = %s"
        cur.execute(query, (email,))
        user = cur.fetchone()

        if user and user[2] == hash_password(password):
            print(f"Login berhasil! Selamat datang, {user[1]}")
            show_menu(role, user[0])
        else:
            print("Email atau password salah.")
    except psycopg2.Error as e:
        print("Terjadi kesalahan saat login:", e)
    finally:
        cur.close()
        conn.close()
