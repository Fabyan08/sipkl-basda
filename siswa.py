from koneksi import koneksi_db
from menu import show_menu
from tabulate import tabulate
from datetime import datetime
from cls import clear_screen
from fpdf import FPDF

# ROLE SISWA
def ajukan_pkl(role, user_id):
    clear_screen()
    conn = koneksi_db()       
    cur = conn.cursor()

    print("\n=== AJUKAN PKL ===")

    today = datetime.today().strftime('%Y-%m-%d')

    # Ambil periode aktif berdasarkan tanggal
    cur.execute("""
        SELECT id_periode, nama_periode, tanggal_mulai, tanggal_selesai
        FROM periode_pkl
        WHERE %s BETWEEN tanggal_mulai AND tanggal_selesai
    """, (today,))
    periode = cur.fetchall()
    
    if not periode:
        print("Tidak ada periode PKL yang aktif hari ini.")
        cur.close()
        conn.close() 
        return

    print("\n-- Periode PKL Aktif --")
    print(tabulate(periode, headers=["ID", "Nama Periode", "Mulai", "Selesai"], tablefmt="grid"))

    periode_id = input("Masukkan ID Periode: ")

    # Cek apakah siswa sudah pernah mendaftar di periode manapun
    cur.execute("SELECT * FROM pendaftaran_pkl WHERE siswa_id = %s", (user_id,))
    if cur.fetchone():
        print("Kamu sudah pernah mengajukan PKL dan tidak bisa mengajukan lagi.")
        input("Tekan enter untuk kembali...")
        cur.close()
        conn.close()
        show_menu(role, user_id)
        return

    # Tampilkan daftar mitra
    cur.execute("SELECT id_mitra, nama_mitra, alamat_mitra, contact_person_mitra, kuota FROM mitra_pkl")
    mitra = cur.fetchall()
    print("\n-- Daftar Mitra PKL --")
    print(tabulate(mitra, headers=["ID", "Nama Mitra", "Alamat", "Kontak Person", "Kuota"], tablefmt="grid"))

    mitra_id = input("Masukkan ID Mitra PKL: ")

    tanggal_daftar = today
    status_pendaftaran = "menunggu"

    # Cek kuota mitra
    cur.execute("SELECT kuota FROM mitra_pkl WHERE id_mitra = %s", (mitra_id,))
    kuota_row = cur.fetchone()
    if not kuota_row:
        print("Mitra tidak ditemukan.")
        cur.close()
        conn.close()
        show_menu(role, user_id)
        return

    kuota = kuota_row[0]

    # Hitung jumlah pendaftar di mitra dan periode yang dipilih
    cur.execute("""
        SELECT COUNT(*) FROM pendaftaran_pkl
        WHERE mitra_id = %s AND periode_id = %s
    """, (mitra_id, periode_id))
    jumlah_pendaftar = cur.fetchone()[0]

    if jumlah_pendaftar >= kuota:
        print(f"Kuota untuk mitra ini sudah penuh. (Kuota: {kuota}, Pendaftar: {jumlah_pendaftar})")
        cur.close()
        conn.close()
        show_menu(role, user_id)
        return

    # Simpan data pendaftaran
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
    clear_screen
    conn = koneksi_db()       
    cur = conn.cursor()

    print("\n=== DAFTAR PENDAFTARAN PKL ===")

    # Ambil semua data pendaftaran berdasarkan user
    query = """
        SELECT p.id_pendaftaran, per.nama_periode, m.nama_mitra AS nama_mitra, p.status_pendaftaran, p.tanggal_daftar
        FROM pendaftaran_pkl p
        JOIN mitra_pkl m ON p.mitra_id = m.id_mitra
        JOIN periode_pkl per ON p.periode_id = per.id_periode
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
        status = str(row[3]).ljust(19)
        tanggal = str(row[4])
        print(f"| {id_pendaftaran} | {periode} | {mitra} | {status}     | {tanggal}         |")

    print("+----+-------------------+----------------+---------------------+------------------+")

    # Pilih salah satu untuk lihat detail
    id_pilihan = input("Masukkan ID pendaftaran yang ingin dilihat detailnya: ")

    # Ambil data detail berdasarkan ID pilihan
    detail_query = """
        SELECT p.id_pendaftaran, m.nama_mitra, m.alamat_mitra, m.contact_person_mitra,
               per.nama_periode, per.tanggal_mulai, per.tanggal_selesai,
               p.status_pendaftaran, p.tanggal_daftar
        FROM pendaftaran_pkl p
        JOIN mitra_pkl m ON p.mitra_id = m.id_mitra
        JOIN periode_pkl per ON p.periode_id = per.id_periode
        WHERE p.id_pendaftaran = %s AND p.siswa_id = %s
    """
    cur.execute(detail_query, (id_pilihan, user_id))
    detail = cur.fetchone()
    status = detail[7]

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
    input("Tekan enter untuk kembali...")
    # Kembali ke menu siswa
    show_menu(role, user_id)

def cetak_surat(role, user_id):
    clear_screen()
    conn = koneksi_db()       
    cur = conn.cursor()

    # Ambil semua pendaftaran user
    query = """
        SELECT p.id_pendaftaran, per.nama_periode, m.nama_mitra AS nama_mitra, p.status_pendaftaran
        FROM pendaftaran_pkl p
        JOIN mitra_pkl m ON p.mitra_id = m.id_mitra
        JOIN periode_pkl per ON p.periode_id = per.id_periode
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
        status = row[3]
        print(f"| {str(row[0]).ljust(2)} | {row[1].ljust(17)} | {row[2].ljust(14)} | {status.ljust(19)} |")
    print("+----+-------------------+----------------+---------------------+")

    id_pendaftaran = input("Masukkan ID pendaftaran yang ingin dicetak suratnya: ")

    # Ambil data detail untuk surat, termasuk status
    detail_query = """
        SELECT u.nama_siswa, u.nisn, m.nama_mitra, m.alamat_mitra, m.contact_person_mitra, 
               per.nama_periode, per.tanggal_mulai, per.tanggal_selesai, p.id_pendaftaran, p.status_pendaftaran
        FROM pendaftaran_pkl p
        JOIN siswa u ON p.siswa_id = u.id_siswa
        JOIN mitra_pkl m ON p.mitra_id = m.id_mitra
        JOIN periode_pkl per ON p.periode_id = per.id_periode
        WHERE p.id_pendaftaran = %s AND p.siswa_id = %s
    """
    cur.execute(detail_query, (id_pendaftaran, user_id))
    data = cur.fetchone()

    if not data:
        print("Data tidak ditemukan atau tidak sesuai.")
        return

    # Ambil data
    nama_user, no_induk, nama_mitra, alamat_mitra, kontak, periode, tgl_mulai, tgl_selesai, id_pendaftar, status_pendaftaran = data

    # Cek status
    if status_pendaftaran == "menunggu":
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
    nama_file = f"surat/{id_pendaftar}_{nama_user.replace(' ', '_')}.pdf"
    pdf.output(nama_file)
    print(f"Surat pengantar berhasil dicetak: {nama_file}")
    input ("Tekan enter untuk kembali ke menu...")
    show_menu(role, user_id)
    
def buat_laporan(role, user_id):
    # clear_screen()
    conn = koneksi_db()       
    cur = conn.cursor()

    print("\n=== BUAT LAPORAN PKL ===")

    # Tampilkan daftar pendaftaran PKL siswa
    query_pkl = """
        SELECT p.id_pendaftaran, m.nama_mitra, per.nama_periode, p.status_pendaftaran
        FROM pendaftaran_pkl p
        JOIN mitra_pkl m ON p.mitra_id = m.id_mitra
        JOIN periode_pkl per ON p.periode_id = per.id_periode
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
    cur.execute("SELECT status_pendaftaran FROM pendaftaran_pkl WHERE id_pendaftaran = %s AND siswa_id = %s", (pkl_id, user_id))
    status = cur.fetchone()
    if not status:
        print("❌ Pendaftaran tidak ditemukan.")
        return buat_laporan(role, user_id)

    if status[0] == 1:  # Belum disetujui
        print("❌ Pendaftaran PKL ini belum disetujui. Kamu belum bisa membuat laporan.")
        return show_menu(role, user_id)

    # Tampilkan semua laporan sebelumnya
    query_laporan = """
        SELECT l.id_laporan, l.tanggal, l.kegiatan, l.catatan, l.nilai_laporan
        FROM laporan_pkl l
        JOIN pendaftaran_pkl p ON l.pendaftaran_pkl = p.id_pendaftaran
        WHERE p.siswa_id = %s AND p.id_pendaftaran = %s
        ORDER BY l.tanggal DESC

    """
    cur.execute(query_laporan, (user_id, pkl_id))
    laporan_list = cur.fetchall()

    if laporan_list:
        print("\n=== Laporan Sebelumnya ===")
        print("+----+------------+------------------------------+----------------+---------+")
        print("| ID | Tanggal    | Kegiatan                     | Catatan        | Nilai   |")
        print("+----+------------+------------------------------+----------------+---------+")
        for lap in laporan_list:
            print(f"| {str(lap[0]).ljust(2)} | {str(lap[1])} | {lap[2][:28].ljust(28)} | {lap[3][:14].ljust(14)} |  {lap[4] if lap[4] is not None else "-"}  "   "|")
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
                INSERT INTO laporan_pkl (tanggal, kegiatan, catatan, pendaftaran_pkl)
                VALUES (%s, %s, %s, %s)
            """
            cur.execute(query_insert, (tanggal, kegiatan, catatan, pkl_id))
            conn.commit()
            print("✅ Laporan berhasil ditambahkan.\n")
        except Exception as e:
            print("❌ Terjadi kesalahan saat menyimpan laporan:", e)

        return buat_laporan(role, user_id)

    elif aksi == '2':
        try:
            edit_id = int(input("Masukkan ID laporan yang ingin diedit: "))
            cur.execute("SELECT l.tanggal, l.kegiatan, l.catatan FROM laporan_pkl l JOIN pendaftaran_pkl p ON l.pendaftaran_pkl = p.id_pendaftaran WHERE l.id_laporan = %s", (edit_id,))
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
                FROM pendaftaran_pkl
                WHERE laporan_pkl.pendaftaran_pkl = pendaftaran_pkl.id_pendaftaran
                AND laporan_pkl.id_laporan = %s
                AND pendaftaran_pkl.siswa_id = %s
            """
            cur.execute(query_update, (tanggal, kegiatan, catatan, edit_id, user_id))
            conn.commit()
            print("✅ Laporan berhasil diperbarui.\n")
            input("Tekan Enter untuk melanjutkan...")
            show_menu(role, user_id)
        except Exception as e:
            print("❌ Gagal memperbarui laporan:", e)

        return buat_laporan(role, user_id)

    elif aksi == '3':
        try:
            del_id = int(input("Masukkan ID laporan yang ingin dihapus: "))
            query_delete = "DELETE FROM laporan_pkl USING pendaftaran_pkl WHERE laporan_pkl.pendaftaran_pkl = pendaftaran_pkl.id_pendaftaran AND laporan_pkl.id_laporan = %s AND pendaftaran_pkl.siswa_id = %s"
            cur.execute(query_delete, (del_id, user_id))
            conn.commit()
            print("✅ Laporan berhasil dihapus.\n")
            input("Tekan Enter untuk melanjutkan...")
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
    clear_screen()
    conn = koneksi_db()       
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT g.nama_guru AS nama_guru, p.nilai_akhir, p.catatan_evaluasi
            FROM penilaian p
            JOIN pendaftaran_pkl pd ON p.pendaftaran_pkl_id = pd.id_pendaftaran
            JOIN guru g ON pd.guru_id = g.id_guru
            WHERE pd.siswa_id = %s
        """, (user_id,))
        
        data = cur.fetchall()

        print("\n=== NILAI AKHIR PKL ===")
        if not data:
            print("❌ Belum ada penilaian yang tersedia.")
        else:
            print("+----------------------+--------+--------------------------------------+")
            print("| Guru Pembimbing      | Nilai  | Catatan Evaluasi                     |")
            print("+----------------------+--------+--------------------------------------+")
            for row in data:
                guru = row[0][:20].ljust(20)
                nilai = str(row[1]) if row[1] is not None else "-"
                nilai = nilai.ljust(6)
                catatan = (row[2][:35] + "...") if row[2] and len(row[2]) > 35 else (row[2] or "-").ljust(35)
                print(f"| {guru} | {nilai} | {catatan} |")
            print("+----------------------+--------+--------------------------------------+")
    except Exception as e:
        print("❌ Terjadi kesalahan saat mengambil nilai:", e)
    finally:
        cur.close()
        conn.close()
        input("\nTekan Enter untuk kembali ke menu...")
        show_menu(3, user_id)
