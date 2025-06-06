# Import file lain
from koneksi import koneksi_db
from auth import login, register
from menu import show_menu
from cls import clear_screen

def show_profile(role, user_id):
    clear_screen()
    conn = koneksi_db()       
    cur = conn.cursor()

    try:
        if role == 1:  # Admin
            table = "admin"
            kolom_id = "id_admin"
            kolom_nama = "nama_admin"
            kolom_email = "email_admin"
            kolom_nohp = "no_hp_admin"
        elif role == 2:  # Guru
            table = "guru"
            kolom_id = "id_guru"
            kolom_nama = "nama_guru"
            kolom_email = "email_guru"
            kolom_nohp = "no_hp_guru"
            kolom_nip = "nip"
        elif role == 3:  # Siswa
            table = "siswa"
            kolom_id = "id_siswa"
            kolom_nama = "nama_siswa"
            kolom_email = "email_siswa"
            kolom_kelas = "kelas_siswa"
            kolom_nohp = "no_hp_siswa"
            kolom_nisn = "nisn"
        else:
            print("❌ Role tidak dikenali.")
            return

        cur.execute(f"SELECT * FROM {table} WHERE {kolom_id} = %s", (user_id,))
        user = cur.fetchone()

        if not user:
            print("❌ Data pengguna tidak ditemukan.")
            return

        print("\n=== PROFIL ===")
        print(f"ID        : {user[0]}")
        print(f"Nama      : {user[1]}")
        print(f"Email     : {user[2]}")

        if role == 3:
            print(f"Kelas     : {user[3]}")
            print(f"No HP     : {user[4]}")
            print(f"NISN      : {user[5]}")
        elif role == 2:
            print(f"NIP       : {user[3]}")
            print(f"No HP     : {user[4]}")
        elif role == 1:
            print(f"No HP     : {user[3]}")

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
        elif role == 1:
            print("[3] No HP")
        print("[0] Kembali")

        pilihan = input("Pilihan: ")
        kolom = None

        if pilihan == '1':
            kolom = kolom_nama
        elif pilihan == '2':
            kolom = kolom_email
        elif role == 3:
            if pilihan == '3':
                kolom = kolom_kelas
            elif pilihan == '4':
                kolom = kolom_nohp
            elif pilihan == '5':
                kolom = kolom_nisn
        elif role == 2:
            if pilihan == '3':
                kolom = kolom_nip
            elif pilihan == '4':
                kolom = kolom_nohp
        elif role == 1 and pilihan == '3':
            kolom = kolom_nohp
        elif pilihan == '0':
            return show_menu(role, user_id)
        else:
            print("❌ Pilihan tidak valid.")
            return

        if kolom:
            nilai_baru = input(f"Masukkan {kolom} baru: ")
            cur.execute(f"UPDATE {table} SET {kolom} = %s WHERE {kolom_id} = %s", (nilai_baru, user_id))
            conn.commit()
            print(f"✅ {kolom} berhasil diperbarui.")

    except Exception as e:
        print("❌ Terjadi kesalahan:", e)
    finally:
        cur.close()
        conn.close()
        show_menu(role, user_id)

def main_menu():
    clear_screen()
    conn = koneksi_db()       
    cur = conn.cursor()
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