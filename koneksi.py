import psycopg2

def koneksi_db():
    try:
        return psycopg2.connect(
            dbname="GoPKL", user="postgres", password="gajahterbang",
            host="localhost", port="5432"
        )
    except psycopg2.Error as e:
        print("Gagal koneksi ke database:", e)
        return None
    
