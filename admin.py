from koneksi import koneksi_db
from menu import show_menu
import hashlib
from tabulate import tabulate
from datetime import datetime
from cls import clear_screen

def tampilkan_users(role):
    clear_screen()

    conn = koneksi_db()       
    cur = conn.cursor()
    
    if role == 'siswa':
        query = "SELECT id_siswa, nama_siswa, email_siswa, no_hp_siswa, kelas_siswa FROM siswa ORDER BY id_siswa"
        headers = ["ID", "Nama", "Email", "No HP", "Kelas"]
    elif role == 'guru':
        query = "SELECT id_guru, nama_guru, email_guru, no_hp_guru, nip FROM guru ORDER BY id_guru"
        headers = ["ID", "Nama", "Email", "No HP", "nip"]
    elif role == 'admin':
        query = "SELECT id_admin, nama_admin, email_admin, no_hp_admin FROM admin ORDER BY id_admin"
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
    clear_screen()
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
    clear_screen()
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
    clear_screen()
    if role not in ['admin', 'guru', 'siswa']:
        print("Role tidak dikenali.")
        return
    if role == 'siswa':
        print("\n=== TAMBAH SISWA ===")
    elif role == 'guru':
        print("\n=== TAMBAH GURU ===")
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
                INSERT INTO siswa (nama_siswa, email_siswa, password_siswa, kelas_siswa, no_hp_siswa, nisn)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (nama, email, hash_password(password), kelas, no_hp, no_induk)
        elif role == 'guru':
            query = """
                INSERT INTO guru (nama_guru, email_guru, password_guru, no_hp_guru, nip)
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
        if role == 'admin':
            id_col = 'id_admin'
            nama_col = 'nama_admin'
            email_col = 'email_admin'
            no_hp_col = 'no_hp_admin'
        elif role == 'guru':
            id_col = 'id_guru'
            nama_col = 'nama_guru'
            email_col = 'email_guru'
            no_hp_col = 'no_hp_guru'
        elif role == 'siswa':
            id_col = 'id_siswa'
            nama_col = 'nama_siswa'
            email_col = 'email_siswa'
            no_hp_col = 'no_hp_siswa'
            kelas_col = 'kelas_siswa'

        # Ambil data lama
        if role == 'siswa':
            cur.execute(f"""
                SELECT {nama_col}, {email_col}, {no_hp_col}, {kelas_col}
                FROM {role}
                WHERE {id_col} = %s
            """, (user_id,))
            user = cur.fetchone()
            if not user:
                print("Siswa tidak ditemukan.")
                return
            nama_lama, email_lama, no_hp_lama, kelas_lama = user
        else:
            cur.execute(f"""
                SELECT {nama_col}, {email_col}, {no_hp_col}
                FROM {role}
                WHERE {id_col} = %s
            """, (user_id,))
            user = cur.fetchone()
            if not user:
                print(f"{role.capitalize()} tidak ditemukan.")
                return
            nama_lama, email_lama, no_hp_lama = user

        nama_baru = input("Nama baru: ").strip() or nama_lama
        email_baru = input("Email baru: ").strip() or email_lama
        no_hp_baru = input("No HP baru: ").strip() or no_hp_lama

        #  update
        if role == 'siswa':
            kelas_baru = input("Kelas baru: ").strip() or kelas_lama
            cur.execute(f"""
                UPDATE {role}
                SET {nama_col} = %s, {email_col} = %s, {no_hp_col} = %s, {kelas_col} = %s
                WHERE {id_col} = %s
            """, (nama_baru, email_baru, no_hp_baru, kelas_baru, user_id))
        else:
            cur.execute(f"""
                UPDATE {role}
                SET {nama_col} = %s, {email_col} = %s, {no_hp_col} = %s
                WHERE {id_col} = %s
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
        if role == 'admin':
            id_col = 'id_admin'
        elif role == 'guru':
            id_col = 'id_guru'
        elif role == 'siswa':
            id_col = 'id_siswa'

        # Cek apakah user ada
        cur.execute(f"SELECT {id_col} FROM {role} WHERE {id_col} = %s", (user_id,))
        user = cur.fetchone()
        if not user:
            print(f"{role.capitalize()} dengan ID tersebut tidak ditemukan.")
            return

        # Konfirmasi hapus
        confirm = input(f"Apakah Anda yakin ingin menghapus {role} dengan ID {user_id}? (y/n): ").lower()
        if confirm == 'y':
            cur.execute(f"DELETE FROM {role} WHERE {id_col} = %s", (user_id,))
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
    clear_screen()
    while True:
        print("\n=== KELOLA DATA MITRA PKL ===")
        data = ambil_data_mitra()
        print(tabulate(data, headers=["ID", "Nama", "Alamat", "Kontak", "Kuota"], tablefmt="grid"))

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
    clear_screen()
    conn = koneksi_db()       
    cur = conn.cursor()
    cur.execute("SELECT id_mitra, nama_mitra, alamat_mitra, contact_person_mitra, kuota FROM mitra_pkl ORDER BY id_mitra")
    return cur.fetchall()

def tambah_mitra():
    clear_screen()
    conn = koneksi_db()       
    cur = conn.cursor()
    
    print("\n=== Tambah Mitra PKL ===")
    nama = input("Nama Mitra: ")
    alamat = input("Alamat: ")
    kontak = input("Kontak Person: ")
    kuota = input("Kuota: ")

    cur.execute("INSERT INTO mitra_pkl (nama_mitra, alamat_mitra, contact_person_mitra, kuota) VALUES (%s, %s, %s, %s)", 
                (nama, alamat, kontak, kuota))
    conn.commit()
    print("Mitra PKL berhasil ditambahkan.")

    cur.close()
    conn.close()

def edit_mitra():
    conn = koneksi_db()       
    cur = conn.cursor()
    id_mitra = input("ID mitra yang ingin diedit: ")

    cur.execute("SELECT * FROM mitra_pkl WHERE id_mitra = %s", (id_mitra,))
    mitra = cur.fetchone()
    if not mitra:
        print("Mitra tidak ditemukan.")
        return

    nama_baru = input(f"Nama baru (kosongkan untuk tetap '{mitra[1]}'): ") or mitra[1]
    alamat_baru = input(f"Alamat baru (kosongkan untuk tetap '{mitra[2]}'): ") or mitra[2]
    kontak_baru = input(f"Kontak baru (kosongkan untuk tetap '{mitra[3]}'): ") or mitra[3]
    kuota_baru = input(f"Kuota baru (kosongkan untuk tetap '{mitra[4]}'): ") or mitra[4]

    cur.execute("""
        UPDATE mitra_pkl 
        SET nama_mitra = %s, alamat_mitra = %s, contact_person_mitra = %s , kuota = %s
        WHERE id_mitra = %s
    """, (nama_baru, alamat_baru, kontak_baru,kuota_baru, id_mitra))
    conn.commit()
    print("Mitra berhasil diedit.")

def hapus_mitra():
    conn = koneksi_db()       
    cur = conn.cursor()
    id_mitra = input("ID mitra yang ingin dihapus: ")
    cur.execute("SELECT * FROM mitra_pkl WHERE id_mitra = %s", (id_mitra,))
    mitra = cur.fetchone()
    if not mitra:
        print("Mitra tidak ditemukan.") 
        return

    konfirmasi = input(f"Yakin ingin menghapus mitra '{mitra[1]}'? (y/n): ")
    if konfirmasi.lower() == 'y':
        cur.execute("DELETE FROM mitra_pkl WHERE id_mitra = %s", (id_mitra,))
        conn.commit()
        print("Mitra berhasil dihapus.")

def kelola_data_periode(role, user_id): 
    clear_screen()
    conn = koneksi_db()       
    cur = conn.cursor()
    while True:
        cur.execute("""
            SELECT id_periode, nama_periode, tanggal_mulai, tanggal_selesai
            FROM periode_pkl
            ORDER BY id_periode
        """)
        data = cur.fetchall()
        cur.close()
        conn.close()

        print("\n=== KELOLA DATA PERIODE PKL ===")
        headers = ["ID", "Nama Periode", "Mulai", "Selesai", "Status"]
        rows = []

        today = datetime.now().date()
        for d in data:
            tgl_mulai = d[2]
            tgl_selesai = d[3]
            status = "Aktif" if tgl_mulai <= today <= tgl_selesai else "Tidak Aktif"
            rows.append((d[0], d[1], str(tgl_mulai), str(tgl_selesai), status))

        print(tabulate(rows, headers=headers, tablefmt="grid"))

        print("[1] Tambah Periode")
        print("[2] Edit Periode")
        print("[3] Hapus Periode")
        print("[0] Kembali")

        pilihan = input("Pilih menu: ")
        if pilihan == '1':
            tambah_periode(role, user_id)
        elif pilihan == '2':
            edit_periode(role , user_id)
        elif pilihan == '3':
            hapus_periode(role, user_id)
        elif pilihan == '0':
            show_menu(role, user_id)
            break
        else:
            print("Pilihan tidak valid.")
            
def tambah_periode(role, user_id):
    clear_screen()
    conn = koneksi_db()       
    cur = conn.cursor()
    print("\n=== Tambah Periode PKL ===")
    nama = input("Nama Periode: ")
    mulai = input("Tanggal Mulai (YYYY-MM-DD): ")
    selesai = input("Tanggal Selesai (YYYY-MM-DD): ")
    status = 1

    cur.execute(
        "INSERT INTO periode_pkl (nama_periode, tanggal_mulai, tanggal_selesai, status) VALUES (%s, %s, %s, %s)",
        (nama, mulai, selesai, status)
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Periode PKL berhasil ditambahkan.")
    show_menu(role, user_id)

def edit_periode(role, user_id):
    print("\n=== Edit Periode PKL ===")
    id_edit = input("ID periode yang ingin diedit: ")

    conn = koneksi_db()       
    cur = conn.cursor()

    cur.execute("SELECT nama_periode, tanggal_mulai, tanggal_selesai FROM periode_pkl WHERE id_periode = %s", (id_edit,))
    data = cur.fetchone()
    if not data:
        print("Data tidak ditemukan.")
        return

    nama_baru = input(f"Nama Periode Baru (kosongkan untuk tetap: {data[0]}): ")
    mulai_baru = input(f"Tanggal Mulai Baru (kosongkan untuk tetap: {data[1]}): ")
    selesai_baru = input(f"Tanggal Selesai Baru (kosongkan untuk tetap: {data[2]}): ")

    nama = nama_baru if nama_baru else data[0]
    mulai = mulai_baru if mulai_baru else data[1]
    selesai = selesai_baru if selesai_baru else data[2]

    cur.execute("""
        UPDATE periode_pkl
        SET nama_periode = %s, tanggal_mulai = %s, tanggal_selesai = %s
        WHERE id_periode = %s
    """, (nama, mulai, selesai, id_edit))
    conn.commit()
    cur.close()
    conn.close()
    print("Periode PKL berhasil diedit.")
    show_menu(role, user_id)

def hapus_periode(role, user_id):
    print("\n=== Hapus Periode PKL ===")
    id_hapus = input("ID periode yang ingin dihapus: ")

    conn = koneksi_db()       
    cur = conn.cursor()

    cur.execute("DELETE FROM periode_pkl WHERE id_periode = %s", (id_hapus,))
    conn.commit()
    cur.close()
    conn.close()
    print("Periode PKL berhasil dihapus.")
    show_menu(role, user_id)
    
# Kelola verifikasi siswa
def verifikasi_pengajuan_siswa(role, user_id):
    print("\n=== VERIFIKASI PENGAJUAN PKL ===")
    
    conn = koneksi_db()       
    cur = conn.cursor()

    # Ambil data pengajuan yang masih menunggu persetujuan
    cur.execute("""
        SELECT p.id_pendaftaran, s.nama_siswa AS nama_siswa, m.nama_mitra AS nama_mitra, pr.nama_periode, p.status_pendaftaran
        FROM pendaftaran_pkl p
        JOIN siswa s ON p.siswa_id = s.id_siswa
        JOIN mitra_pkl m ON p.mitra_id = m.id_mitra
        JOIN periode_pkl pr ON p.periode_id = pr.id_periode
        WHERE p.status_pendaftaran = 'menunggu'
    """)

    data = cur.fetchall()

    if not data:
        print("Tidak ada pengajuan yang perlu diverifikasi.")
        input("Tekan Enter untuk kembali ke menu utama...")
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
    cur.execute("SELECT id_pendaftaran FROM pendaftaran_pkl WHERE id_pendaftaran = %s AND status_pendaftaran = 'menunggu'", (id_pengajuan,))
    cek_pengajuan = cur.fetchone()
    if not cek_pengajuan:
        print("❌ ID pengajuan tidak ditemukan atau sudah disetujui.")
        return show_menu(role, user_id)

    # Tampilkan daftar guru pembimbing dari tabel guru
    cur.execute("SELECT id_guru, nama_guru FROM guru")
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
    cur.execute("SELECT id_guru FROM guru WHERE id_guru = %s", (guru_id,))
    cek_guru = cur.fetchone()
    if not cek_guru:
        print("❌ Guru dengan ID tersebut tidak ditemukan.")
        return show_menu(role, user_id)

    # Setujui pengajuan dan tetapkan guru
    try:
        cur.execute("""
            UPDATE pendaftaran_pkl 
            SET status_pendaftaran = 'disetujui', guru_id = %s , admin_id = %s
            WHERE id_pendaftaran = %s
        """, (guru_id,  user_id, id_pengajuan))
        conn.commit()
        print("✅ Pengajuan berhasil disetujui dan guru pembimbing ditetapkan.")
    except Exception as e:
        print("❌ Gagal memperbarui data:", e)
    finally:
        conn.close()

    show_menu(role, user_id)
