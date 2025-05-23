def main_menu():
    print("=== Selamat Datang di Lahanku ===")
    print("[1] Login")
    print("[2] Register")
    pilihan = input("Pilih menu: ")
    
    if pilihan == '1':
            ()
    elif pilihan == '2':
        register()
    else:
        print("Pilihan tidak valid. Silakan coba lagi.")
        main_menu()

# def register():
#     print("=== Registrasi ===")
    
#     try:
#         users_df = pd.read_csv("users.csv", header=None)
#         users_df.columns = ["user_id", "nama", "email", "password", "ktp", "nomor_hp", "alamat", "level"]
#     except FileNotFoundError:
#         users_df = pd.DataFrame(columns=["user_id", "nama", "email", "password", "ktp", "nomor_hp", "alamat", "level"])
    
#     user_id = 1 if users_df.empty else users_df["user_id"].max() + 1

#     nama = input("Masukkan Nama: ")
#     email = input("Masukkan Email: ")
#     password = input("Masukkan Password: ")
#     ktp = input("Masukkan No KTP: ")
#     nomor_hp = input("Masukkan Nomor HP: ")
#     alamat = input("Masukkan Alamat: ")
    
#     print("Pilih jenis akun:")
#     print("[1] Pengguna")
#     print("[2] Pemilik Lahan")
#     pilihan_level = input("Pilih (1/2): ")
    
#     if pilihan_level == '1':
#         level = "pengguna"
#     elif pilihan_level == '2':
#         level = "pemilik_lahan"
#     else:
#         print("Pilihan tidak valid. Silakan coba lagi.")
#         register()
#         return
    
#     password = hashlib.sha256(password.encode()).hexdigest()
    
#     new_user = pd.DataFrame({
#         "user_id": [user_id],
#         "nama": [nama],
#         "email": [email],
#         "password": [password],
#         "ktp": [ktp],
#         "nomor_hp": [nomor_hp],
#         "alamat": [alamat],
#         "level": [level]
#     })
    
#     users_df = pd.concat([users_df, new_user], ignore_index=True)
    
#     users_df.to_csv("users.csv", index=False, header=False)
    
#     print("Registrasi berhasil! Silakan login.")
#     main_menu()

# # Fungsi login
# def is_valid_email(email):
#     return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# def login():
#     print("=== Login ===")
#     email = input("Masukkan Email: ").strip()
#     password = input("Masukkan Password: ").strip()

#     if not is_valid_email(email):
#         print("Format email tidak valid. Silakan coba lagi.")
#         login()
#         return

#     password_hash = hashlib.sha256(password.encode()).hexdigest()

#     try:
#         with open("users.csv", mode="r") as file:
#             reader = csv.reader(file)
#             for row in reader:
#                 if row[2] == email and row[3] == password_hash:
#                     print(f"Login berhasil! Selamat datang, {row[1]}")
#                     show_menu(row[7], row[0])
#                     return

#     except FileNotFoundError:
#         print("Database pengguna belum tersedia. Silakan registrasi terlebih dahulu.")
#     except Exception as e:
#         print(f"Terjadi kesalahan: {e}")

#     print("Email atau password salah. Coba lagi.")
#     main_menu()

# # Menu sesuai level
# def show_menu(level, user_id):
#     print("\n=== Menu Utama ===")
#     print("[0] Profil")
#     if level == "pengguna":
#         print("[1] Sewa Lahan")
#         print("[2] Data Perjanjian")
#         print("[3] Lihat History")
#         pilihan = input("Pilih menu: ")
#         if pilihan == '0':
#             show_profile(level, user_id)
#         elif pilihan == '1':
#             sewa_lahan(user_id)
#         elif pilihan == '2':
#             data_perjanjian(user_id)
#         elif pilihan == '3':
#             lihat_history(user_id)
#         else:
#             print("Pilihan tidak valid. Silahkan coba lagi")
#             show_menu(level, user_id)

#     elif level == "pemilik_lahan":
#         print("[1] Data Lahan")
#         print("[2] List Penyewa")
#         pilihan = input("Pilih menu: ")
#         if pilihan == '0':
#             show_profile(level, user_id)
#         elif pilihan == '1':
#             data_lahan(user_id)
#         elif pilihan == '2':
#             list_penyewa(user_id)
#         else:
#             print("Pilihan tidak valid. Silahkan coba lagi")
#             show_menu(level, user_id)

#     elif level == "admin":
#         print("[1] Rekap Penyewaan")
#         print("[2] Rekap Jumlah Pengguna")

#         while True:
#             pilihan = input("Pilih menu: ")
#             if pilihan == '1':
#                 rekap_penyewaan(user_id)
#                 break
#             elif pilihan == '2':
#                 rekap_jumlah_pengguna(user_id)
#                 break
#             elif pilihan == '0':
#                 show_profile(level, user_id)
#                 break
#             else:
#                 print("Pilihan tidak valid. Silakan coba lagi.")
#     else:
#         print("Level akses tidak dikenali.")
#         return

# # SEMUA HAK AKSES
# def show_profile(level, user_id):
#     try:
#         with open('users.csv', 'r') as file:
#             users = list(csv.reader(file))

#         user_index = next((i for i, u in enumerate(users) if u[0] == user_id), None)

#         if user_index is None:
#             print("Pengguna tidak ditemukan.")
#             return

#         user = users[user_index]

#         print("\n=== Profil Pengguna ===")
#         print(f"ID Pengguna: {user[0]}")
#         print(f"Nama: {user[1]}")
#         print(f"Email: {user[2]}")
#         print(f"Nomor KTP: {user[4]}")
#         print(f"Nomor HP: {user[5]}")
#         print(f"Alamat: {user[6]}")
#         print("=" * 30)

#         print("Pilih data yang ingin diubah:")
#         print("[1] Nama")
#         print("[2] Email")
#         print("[3] Nomor KTP")
#         print("[4] Nomor HP")
#         print("[5] Alamat")
#         print("[0] Kembali ke Menu Utama")
#         print(" ")
#         print("=====Logout=====")
#         print("[9] Logout")

#         pilihan = input("Pilih menu: ")

#         if pilihan == '1':
#             new_name = input("Masukkan nama baru: ")
#             users[user_index][1] = new_name
#             print(f"Nama berhasil diubah menjadi {new_name}")
#         elif pilihan == '2':
#             new_email = input("Masukkan email baru: ")
#             users[user_index][2] = new_email
#             print(f"Email berhasil diubah menjadi {new_email}")
#         elif pilihan == '3':
#             new_ktp = input("Masukkan nomor KTP baru: ")
#             users[user_index][4] = new_ktp
#             print(f"Nomor KTP berhasil diubah menjadi {new_ktp}")
#         elif pilihan == '4':
#             new_phone = input("Masukkan nomor HP baru: ")
#             users[user_index][5] = new_phone
#             print(f"Nomor HP berhasil diubah menjadi {new_phone}")
#         elif pilihan == '5':
#             new_address = input("Masukkan alamat baru: ")
#             users[user_index][6] = new_address
#             print(f"Alamat berhasil diubah menjadi {new_address}")
#         elif pilihan == '0':
#             show_menu(level, user_id)
#             return
#         elif pilihan == '9':
#             print("Terima kasih telah menggunakan layanan kami. Sampai jumpa kembali!")
#             return
#         else:
#             print("Pilihan tidak valid. Kembali ke menu utama.")
#             show_menu(level, user_id)
#             return

#         with open('users.csv', 'w', newline='') as file:
#             writer = csv.writer(file)
#             writer.writerows(users)

#         show_menu(level, user_id)

#     except Exception as e:
#         print(f"Terjadi kesalahan: {e}")

