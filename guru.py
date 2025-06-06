from koneksi import koneksi_db
from menu import show_menu
from tabulate import tabulate
from cls import clear_screen

def lihat_laporan(role, user_id):
    clear_screen()

    conn = koneksi_db()       
    cur = conn.cursor()

    print("\n=== DAFTAR LAPORAN SISWA BIMBINGAN ===")

    query = """
        SELECT l.id_laporan, u.nama_siswa AS nama_siswa, m.nama_mitra AS nama_mitra, l.tanggal, l.kegiatan, l.nilai_laporan
        FROM laporan_pkl l
        JOIN pendaftaran_pkl p ON l.pendaftaran_pkl = p.id_pendaftaran
        JOIN siswa u ON p.siswa_id = u.id_siswa
        JOIN mitra_pkl m ON p.mitra_id = m.id_mitra
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
        SELECT l.id_laporan, u.nama_siswa, m.nama_mitra, l.tanggal, l.kegiatan, l.catatan, l.nilai_laporan
        FROM laporan_pkl l
        JOIN pendaftaran_pkl p ON l.pendaftaran_pkl = p.id_pendaftaran
        JOIN siswa u ON p.siswa_id = u.id_siswa
        JOIN mitra_pkl m ON p.mitra_id = m.id_mitra
        WHERE l.id_laporan = %s AND p.guru_id = %s
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
                        cur.execute("UPDATE laporan_pkl SET nilai_laporan = %s WHERE id_laporan = %s", (nilai_baru_int, laporan_id))
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
    clear_screen()
    conn = koneksi_db()       
    cur = conn.cursor()

    print("\n=== PENILAIAN AKHIR SISWA BIMBINGAN ===")

    query = """
        SELECT 
        p.id_pendaftaran, u.nama_siswa, m.nama_mitra, per.nama_periode, per.tanggal_mulai, per.tanggal_selesai,
        pn.nilai_akhir
        FROM pendaftaran_pkl p
        JOIN siswa u ON p.siswa_id = u.id_siswa
        JOIN mitra_pkl m ON p.mitra_id = m.id_mitra
        JOIN periode_pkl per ON p.periode_id = per.id_periode
        LEFT JOIN penilaian pn ON pn.siswa_id = p.id_pendaftaran AND pn.guru_id = %s
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


    try:
        siswa_id = int(input("\nMasukkan ID siswa yang ingin dinilai (0 untuk kembali): "))
        if siswa_id == 0:
            return show_menu(role, user_id)
    except ValueError:
        print("❌ ID tidak valid.")
        return beri_nilai_akhir(role, user_id)

    cur.execute("""
        SELECT 
            p.id_pendaftaran, u.nama_siswa, m.nama_mitra, per.nama_periode, per.tanggal_mulai, per.tanggal_selesai
        FROM pendaftaran_pkl p
        JOIN siswa u ON p.siswa_id = u.id_siswa
        JOIN mitra_pkl m ON p.mitra_id = m.id_mitra
        JOIN periode_pkl per ON p.periode_id = per.id_periode
        WHERE p.id_pendaftaran = %s AND p.guru_id = %s
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
    cur.execute("SELECT id_penilaian FROM penilaian WHERE siswa_id = %s AND guru_id = %s", (siswa_id, user_id))
    existing = cur.fetchone()

    try:
        if existing:
            cur.execute("""
                UPDATE penilaian SET nilai_akhir = %s, catatan_evaluasi = %s WHERE id_penilaian = %s
            """, (nilai, catatan, existing[0]))
            print("✅ Penilaian berhasil diperbarui.")
        else:
            cur.execute("""
                INSERT INTO penilaian (siswa_id, guru_id, nilai_akhir, catatan_evaluasi)
                VALUES (%s, %s, %s, %s)
            """, (siswa_id, user_id, nilai, catatan))
            print("✅ Penilaian berhasil disimpan.")

        conn.commit()
    except Exception as e:
        print("❌ Terjadi kesalahan saat menyimpan penilaian:", e)

    input("\nTekan Enter untuk kembali...")
    return show_menu(role, user_id)
