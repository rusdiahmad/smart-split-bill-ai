Assignment: Mini Project Product AI - Machine Learning Bootcamp
1. Deskripsi Proyek
SmartSplit Bill AI adalah prototipe aplikasi web yang dikembangkan untuk memecahkan masalah pembagian tagihan dan pencatatan transaksi. Aplikasi ini menggunakan teknologi Vision AI (Large Multimodal Model) untuk mengekstrak data terstruktur (item, harga, biaya tambahan, total) langsung dari gambar nota atau struk belanja, dan kemudian memungkinkan pengguna untuk membagi tagihan item per item (split bill) di antara beberapa partisipan.

2. Teknologi & Persiapan
Proyek ini dibangun menggunakan:

Backend/Logic: Python

AI Model: Google Gemini API (gemini-2.5-flash)

Web Framework: Streamlit

Dependencies: google-genai, streamlit, Pillow

A. Instalasi
Clone Repository:

Bash

# Asumsi Anda menggunakan Git
# git clone <repository-url>
# cd smartsplit_bill_ai
Instal Pustaka Python:

Bash

pip install streamlit google-genai pillow
Siapkan API Key: Ganti placeholder GEMINI_API_KEY di file ai_service.py dengan kunci API Gemini Anda yang valid.

B. Cara Menjalankan Aplikasi
Jalankan aplikasi Streamlit dari terminal Anda:

Bash

streamlit run app.py
Aplikasi akan otomatis terbuka di browser Anda (biasanya di http://localhost:8501).
