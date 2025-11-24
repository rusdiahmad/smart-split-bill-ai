# app.py

import streamlit as st
import json
import os
from ai_service import extract_bill_data_gemini 

# --- Fungsi Utama Aplikasi Streamlit ---
def smart_split_bill_app():
    st.set_page_config(page_title="SmartSplit Bill AI", layout="wide")
    st.title("💰 SmartSplit Bill AI Prototype")
    st.caption("Mini Project SmartSplit Bill - Dibimbing")

    # Inisialisasi Session State
    if 'data_loaded' not in st.session_state:
        st.session_state['data_loaded'] = False
        st.session_state['extracted_data'] = None

    # --- 1. Upload & Ekstraksi AI ---
    st.header("1. Upload Nota & Ekstraksi Data")
    
    uploaded_file = st.file_uploader("Upload Gambar Nota (JPEG/PNG)", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Simpan file sementara untuk diolah oleh AI
        temp_file_path = f"temp_{uploaded_file.name}"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.image(uploaded_file, caption='Nota yang Diunggah', width=400)
        
        if st.button('Proses Nota dengan AI (Gemini)'):
            with st.spinner('AI sedang membaca dan mengekstrak data...'):
                raw_result, latency, extracted_data = extract_bill_data_gemini(temp_file_path)
                
                if isinstance(extracted_data, dict):
                    st.session_state['extracted_data'] = extracted_data
                    st.session_state['data_loaded'] = True
                    st.success(f"Ekstraksi data berhasil! (Latensi: {latency:.2f}s)")
                    st.json(extracted_data) # Tampilkan data mentah hasil ekstraksi
                else:
                    st.session_state['data_loaded'] = False
                    st.error(f"Gagal memproses hasil AI: {extracted_data}")
                    st.code(raw_result)
                    
    # --- 2. Split Bill Logics ---
    if st.session_state['data_loaded']:
        extracted_data = st.session_state['extracted_data']
        
      
        # Memastikan 'items' ada dan berupa list
        if not extracted_data or 'items' not in extracted_data or not isinstance(extracted_data['items'], list):
            st.error("⚠️ EKSTRAKSI GAGAL: Data yang diterima dari AI tidak lengkap atau tidak memiliki kunci 'items' (daftar item belanja) yang valid. Mohon periksa kembali output JSON di atas.")
            st.session_state['data_loaded'] = False # Reset status
            return # Hentikan proses split bill jika data utama tidak ada
        # =======================================================================
        
        st.markdown("---")
        st.header("2. Alokasi Biaya dan Split Bill")

        # 2a. Tampilkan Data Utama
        total_bill = extracted_data.get('total_harga_bill', 0.0)
        st.metric("TOTAL HARGA BILL DARI NOTA", f"Rp{total_bill:,.2f}")

        # 2b. Input Partisipan
        st.subheader("👥 Partisipan")
        participants_input = st.text_input(
            "Masukkan nama partisipan (dipisahkan koma)",
            value="Andi, Budi, Clara",
            key="participants_input"
        )
        participants = [name.strip() for name in participants_input.split(',') if name.strip()]
        
        if not participants:
            st.warning("Silakan masukkan minimal satu nama partisipan.")
            return

        # 2c. Tugaskan Item dan Biaya Tambahan
        st.subheader("🏷️ Tentukan Pembayar untuk Setiap Item")
        
       
        if 'assignments' not in st.session_state or len(st.session_state['assignments']) != len(extracted_data['items']):
            st.session_state['assignments'] = [participants[0]] * len(extracted_data['items']) 
            
        # Tampilan penugasan item
        for i, item in enumerate(extracted_data['items']):
            col1, col2, col3, col4 = st.columns([1, 4, 2, 4])
            
            col1.write(f"**{item['jumlah']}x**")
            col2.write(f"{item['nama_item']}")
            col3.write(f"Rp{item['total_harga_item']:,.2f}")
            
            default_index = participants.index(st.session_state['assignments'][i]) if st.session_state['assignments'][i] in participants else 0
                
            selected_participant = col4.selectbox(
                'Dibayar oleh:',
                participants,
                index=default_index,
                key=f"item_assign_{i}",
                on_change=lambda i=i: st.session_state.update({f'assignments': [
                    st.session_state[f"item_assign_{j}"] if j == i else st.session_state['assignments'][j] for j in range(len(extracted_data['items']))
                ]})
            )
            st.session_state['assignments'][i] = selected_participant


        # Alokasi Biaya Tambahan (dibagi rata untuk POC)
        st.subheader("⚙️ Biaya Tambahan (Dibagi Rata)")
        
        total_surcharge = (
            extracted_data.get('biaya_pengiriman', 0.0) +
            extracted_data.get('biaya_layanan', 0.0) +
            extracted_data.get('biaya_pengemasan', 0.0) +
            extracted_data.get('diskon_voucher', 0.0)
        )
        
        num_participants_paying_surcharge = len(participants)
        surcharge_per_person = total_surcharge / num_participants_paying_surcharge if num_participants_paying_surcharge > 0 else 0
        st.info(f"Total Biaya Tambahan/Diskon: Rp{total_surcharge:,.2f}. Dibagi rata menjadi **Rp{surcharge_per_person:,.2f} per orang**.")

        # 2d. Laporan Akhir
        st.markdown("---")
        st.header("3. Laporan Total Pembayaran Akhir")
        
        final_totals = {p: 0.0 for p in participants}

        # Hitung total item
        for i, item in enumerate(extracted_data['items']):
            payer = st.session_state['assignments'][i]
            final_totals[payer] += item['total_harga_item']
        
        # Hitung total akhir (Item + Surcharge)
        final_payment_totals = {
            p: final_totals[p] + surcharge_per_person for p in participants
        }

        # Tampilan Final
        final_table_data = {
            'Partisipan': participants,
            'Biaya Item': [f"Rp{final_totals[p]:,.2f}" for p in participants],
            'Biaya Tambahan/Diskon (Rata)': [f"Rp{surcharge_per_person:,.2f}" for p in participants],
            'TOTAL BAYAR': [f"**Rp{final_payment_totals[p]:,.2f}**" for p in participants]
        }
        
        st.table(final_table_data)



if __name__ == '__main__':
    smart_split_bill_app()
