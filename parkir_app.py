import streamlit as st
import math
from datetime import datetime

# ========== STRUKTUR DATA: DOUBLY LINKED LIST ==========
class KendaraanNode:
    """Node Doubly Linked List untuk merepresentasikan satu unit Kendaraan"""
    def __init__(self, plat, merk, pemilik, status):
        self.plat = plat.upper()
        self.merk = merk
        self.pemilik = pemilik
        self.status = status.upper()  # VIP atau REGULER
        self.waktu_masuk = datetime.now()  # Menyimpan waktu real-time
        self.prev = None
        self.next = None

class SistemParkirValet:
    """Implementasi Doubly Linked List untuk Lajur Parkir"""
    def __init__(self):
        self.head = None  # Pintu Keluar (Paling Depan)
        self.tail = None  # Ujung Lajur (Paling Belakang)
        self.kapasitas = 0

    # ========== KENDARAAN MASUK ==========
    def parkir_vip(self, plat, merk, pemilik):
        """Insert di Awal (Prioritas VIP)"""
        mobil_baru = KendaraanNode(plat, merk, pemilik, "VIP")
        
        if self.head is None:
            self.head = mobil_baru
            self.tail = mobil_baru
        else:
            mobil_baru.next = self.head
            self.head.prev = mobil_baru
            self.head = mobil_baru
            
        self.kapasitas += 1
        return f"Kendaraan VIP {merk} ({mobil_baru.plat}) masuk di antrean DEPAN."

    def parkir_reguler(self, plat, merk, pemilik):
        """Insert di Akhir (Parkir standar)"""
        mobil_baru = KendaraanNode(plat, merk, pemilik, "REGULER")
        
        if self.tail is None:
            self.head = mobil_baru
            self.tail = mobil_baru
        else:
            mobil_baru.prev = self.tail
            self.tail.next = mobil_baru
            self.tail = mobil_baru
            
        self.kapasitas += 1
        return f"Kendaraan Reguler {merk} ({mobil_baru.plat}) masuk di antrean BELAKANG."

    # ========== KENDARAAN KELUAR & PEMBAYARAN ==========
    def proses_keluar(self, target_plat):
        """Menghapus Node dan menghitung biaya (Hapus dari posisi mana saja)"""
        target_plat = target_plat.upper()
        current = self.head
        
        while current:
            if current.plat == target_plat:
                # 1. Hitung Biaya & Waktu
                waktu_keluar = datetime.now()
                selisih_waktu = waktu_keluar - current.waktu_masuk
                
                # Mengubah detik menjadi jam simulasi (1 menit nyata = 1 jam parkir)
                lama_jam = math.ceil(selisih_waktu.total_seconds() / 60)
                if lama_jam == 0: 
                    lama_jam = 1 
                
                # Menentukan tarif berdasarkan status
                if current.status == "VIP":
                    biaya = 20000 + ((lama_jam - 1) * 10000)
                else: # REGULER
                    biaya = 5000 + ((lama_jam - 1) * 3000)

                # Simpan data struk untuk dilempar ke UI Streamlit
                data_struk = {
                    "plat": current.plat,
                    "merk": current.merk,
                    "pemilik": current.pemilik,
                    "status": current.status,
                    "waktu_masuk": current.waktu_masuk.strftime("%H:%M:%S"),
                    "waktu_keluar": waktu_keluar.strftime("%H:%M:%S"),
                    "lama_jam": lama_jam,
                    "total_biaya": biaya
                }

                # 2. Hapus Node dari Linked List
                if current == self.head:
                    self.head = self.head.next
                    if self.head:
                        self.head.prev = None
                    else:
                        self.tail = None 
                elif current == self.tail:
                    self.tail = self.tail.prev
                    if self.tail:
                        self.tail.next = None
                else:
                    current.prev.next = current.next
                    current.next.prev = current.prev
                
                self.kapasitas -= 1
                return data_struk  # Mengembalikan data struk jika sukses
                
            current = current.next
            
        return None  # Mengembalikan None jika tidak ditemukan

    def konversi_ke_matriks(self):
        """Mengubah antrean Linked List menjadi List standar (Matriks 2D) untuk tabel bawaan Streamlit"""
        data = []
        current = self.head
        nomor = 1
        while current:
            jam = current.waktu_masuk.strftime("%H:%M:%S")
            # Menyimpan data dalam format list biasa (baris per baris)
            data.append([nomor, current.plat, current.merk, current.pemilik, current.status, jam])
            current = current.next
            nomor += 1
        return data


# ========== APLIKASI UTAMA (STREAMLIT UI) ==========

st.set_page_config(page_title="Smart Parking System", page_icon="🚗", layout="centered")

st.title("🚗 Smart Parking System Dashboard")
st.caption("Implementasi Aplikasi Berbasis Struktur Data Doubly Linked List")

# Jembatan pengaman memori Streamlit (State Management)
if 'parkiran' not in st.session_state:
    st.session_state.parkiran = SistemParkirValet()

parkiran = st.session_state.parkiran

# Membuat Menu Menggunakan Tab Layout
tab1, tab2, tab3 = st.tabs(["📥 Check-In Parkir", "📤 Check-Out & Struk", "📊 Denah & Kapasitas"])

# --- TAB 1: KENDARAAN MASUK ---
with tab1:
    st.header("Form Registrasi Kendaraan Masuk")
    with st.form("form_pendaftaran", clear_on_submit=True):
        plat_input = st.text_input("Plat Nomor Kendaraan", placeholder="Contoh: B 1234 ABC")
        merk_input = st.text_input("Merk / Model Kendaraan", placeholder="Contoh: Honda Brio Hitam")
        pemilik_input = st.text_input("Nama Lengkap Pemilik", placeholder="Contoh: Ahmad Subarjo")
        status_input = st.radio("Pilih Tipe Layanan Parkir", ["Reguler (Antrean Belakang)", "VIP (Prioritas Depan)"])
        
        proses_masuk = st.form_submit_button("Daftarkan & Parkirkan")
        
        if proses_masuk:
            if plat_input and merk_input and pemilik_input:
                if "VIP" in status_input:
                    hasil_pesan = parkiran.parkir_vip(plat_input, merk_input, pemilik_input)
                else:
                    hasil_pesan = parkiran.parkir_reguler(plat_input, merk_input, pemilik_input)
                st.success(f"[+] BERHASIL: {hasil_pesan}")
            else:
                st.error("Gagal! Semua kolom formulir data kendaraan wajib diisi.")

# --- TAB 2: KENDARAAN KELUAR ---
with tab2:
    st.header("Form Penjemputan & Billing Kasir")
    plat_keluar = st.text_input("Masukkan Plat Nomor Mobil yang Ingin Keluar")
    tombol_keluar = st.button("Proses Pembayaran Keluar", type="primary")
    
    if tombol_keluar:
        if plat_keluar:
            struk = parkiran.proses_keluar(plat_keluar)
            if struk:
                st.success("Akses Terverifikasi! Kendaraan dilepaskan dari lajur antrean.")
                
                # Tampilan Nota/Struk Digital yang Cantik
                st.markdown("### 🧾 STRUK NOTA SMART PARKING")
                st.markdown("---")
                col_kiri, col_kanan = st.columns(2)
                with col_kiri:
                    st.markdown(f"**Plat Nomor** : {struk['plat']}")
                    st.markdown(f"**Kendaraan** : {struk['merk']}")
                    st.markdown(f"**Pemilik** : {struk['pemilik']}")
                    st.markdown(f"**Status Kelas** : {struk['status']}")
                with col_kanan:
                    st.markdown(f"**Jam Masuk** : {struk['waktu_masuk']}")
                    st.markdown(f"**Jam Keluar** : {struk['waktu_keluar']}")
                    st.markdown(f"**Durasi Parkir** : {struk['lama_jam']} Jam (Skala Simulasi)")
                st.markdown("---")
                st.info(f"### TOTAL TAGIHAN: Rp {struk['total_biaya']:,}")
            else:
                st.error(f"[-] ERROR: Kendaraan dengan plat nomor '{plat_keluar.upper()}' tidak ditemukan di sistem parkir.")
        else:
            st.warning("Silakan isi plat nomor target terlebih dahulu.")

# --- TAB 3: DENAH PARKIRAN ---
with tab3:
    st.header("Monitoring Denah Jalur Parkir")
    
    # Menampilkan indikator angka kapasitas terisi
    st.metric(label="Jumlah Kendaraan Terparkir Saat Ini", value=f"{parkiran.kapasitas} Unit")
    
    # Ambil konversi data linked list berupa List-of-List
    list_mobil = parkiran.konversi_ke_matriks()
    
    if list_mobil:
        st.markdown("**Urutan Lajur Parkir (Pintu Keluar [HEAD] → Ujung Lajur [TAIL])**")
        
        # Definisikan nama kolom secara manual
        nama_kolom = ["No", "Plat Nomor", "Merk/Model", "Nama Pemilik", "Status", "Jam Masuk"]
        
        # Gunakan komponen tabel statis bawaan Streamlit (st.table)
        # Kita buat dictionary dengan nama kolom sebagai key agar terbaca rapi oleh st.table
        tabel_statis = [dict(zip(nama_kolom, mobil)) for mobil in list_mobil]
        st.table(tabel_statis)
    else:
        st.info("Kondisi Parkiran Kosong. Belum ada kendaraan yang terdaftar masuk.")
