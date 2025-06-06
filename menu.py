from cls import clear_screen

def show_menu(role, user_id):
    from admin import kelola_data_guru,kelola_data_siswa ,kelola_data_mitra, kelola_data_periode, verifikasi_pengajuan_siswa;
    
    from siswa import ajukan_pkl, lihat_status_verifikasi, buat_laporan, lihat_nilai_akhir, cetak_surat;
    
    from guru import lihat_laporan, beri_nilai_akhir;
    
    from index import main_menu, show_profile;
    
    clear_screen()
    
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
