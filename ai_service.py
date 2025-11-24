# ai_service.py

import os
import json
import time
from PIL import Image
from google import genai
from google.api_core.exceptions import InvalidArgument

# =======================================================================
# PENTING: GANTI placeholder di bawah dengan kunci API Gemini baru Anda.
# Cara ini kurang disarankan, tapi mengatasi masalah lingkungan sementara.
# Untuk praktik terbaik, gunakan export GEMINI_API_KEY="..." di terminal
# dan gunakan client = genai.Client() saja.
# =======================================================================
# GANTI API KEY ANDA DI BAWAH INI
GEMINI_API_KEY = "AIzaSyBoSIk5bV3x7pqyVGcVySU2uzCFUGXVC0Q"
# GANTI API KEY ANDA DI ATAS INI
# =======================================================================

try:
    # Inisialisasi client dengan kunci API yang Anda masukkan
    client = genai.Client(api_key=GEMINI_API_KEY) 
except Exception as e:
    # Ini akan menangani error jika kunci tidak valid saat inisialisasi
    print(f"Error in Gemini Client initialization: {e}")
    # Jika Anda menggunakan Variabel Lingkungan, gunakan: client = genai.Client()
    
# --- Fungsi Utama Ekstraksi Data ---
def extract_bill_data_gemini(image_path: str):
    """
    Menggunakan Gemini untuk mengekstrak data transaksi nota ke format JSON.
    Mengandung logika prompt engineering dan pembersihan output.
    """
    if not os.path.exists(image_path):
        return f"File not found: {image_path}", 0, None

    img = Image.open(image_path)
    
    # Prompt engineering yang ketat untuk mendapatkan output JSON murni
    prompt = (
        "Dari gambar nota ini, ekstrak semua data pembelian item, subtotal, "
        "semua biaya tambahan (layanan, pengiriman, pengemasan), dan total harga bill. "
        "Sajikan hasilnya dalam format JSON yang terstruktur. "
        "Daftar item harus mencakup: 'nama_item' (string), 'jumlah' (int), 'harga_per_item' (float), dan 'total_harga_item' (float). "
        "Pastikan semua harga dalam satuan Rupiah (Rp) dikonversi ke float (misal: 41000.00). "
        "Diskon/Voucher harus dicatat sebagai nilai negatif."
        
        # Instruksi KRITIS untuk mencegah error JSON
        "\n\nHasil output Anda HARUS berupa objek JSON tunggal dan valid. JANGAN sertakan teks, penjelasan, atau markdown (seperti ```json) di luar blok JSON."
    )

    print(f"Mengirim {image_path} ke Gemini API...")
    start_time = time.time()
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, img]
        )
        latency = time.time() - start_time
        raw_result = response.text.strip()
        
        # Logika pembersihan dan konversi ke JSON
        try:
            # Pengecekan jika model menyertakan markdown
            if raw_result.startswith('```json'):
                cleaned_result = raw_result.replace('```json', '').replace('```', '').strip()
            else:
                cleaned_result = raw_result
                
            data = json.loads(cleaned_result)
            return raw_result, latency, data
            
        except json.JSONDecodeError as e:
            # Mengembalikan error JSON jika pembersihan gagal
            return raw_result, latency, f"JSON Error: {e}"
        
    except InvalidArgument as e:
        latency = time.time() - start_time
        return f"API Error: {e}", latency, None
    except Exception as e:
        latency = time.time() - start_time
        return f"General Error: {e}", latency, None

# --- Fungsi untuk Pengujian Cepat ---
def test_extraction(image_path):
    raw_res, latency, data = extract_bill_data_gemini(image_path)
    print(f"\n--- Hasil Ekstraksi untuk {image_path} ---")
    print(f"Latensi: {latency:.2f}s")
    print("Data yang Dikonversi:")
    if isinstance(data, dict):
        print(json.dumps(data, indent=2))
    else:
        print(f"Gagal Konversi: {data}")
    return data

if __name__ == '__main__':
    # Pastikan file contoh1.jpg dan contoh2.jpg ada di direktori
    test_extraction('contoh1.jpg')
    test_extraction('contoh2.jpg')