import streamlit as st
import os
from services.image_reader import extract_receipt
from services.split_service import compute_splits

st.set_page_config(page_title="Smart Split Bill AI", layout="wide")

# ========================
# INIT SESSION STATE
# ========================
if "page" not in st.session_state:
    st.session_state.page = 1

if "parsed" not in st.session_state:
    st.session_state.parsed = None

if "report" not in st.session_state:
    st.session_state.report = None

def go_to(step):
    st.session_state.page = step
    st.rerun()


# ========================
# PAGE 1 — UPLOAD
# ========================
def page_upload():
    st.title("📸 Upload Receipt")

    uploaded = st.file_uploader("Upload foto nota", type=["jpg", "jpeg", "png"])

    if uploaded:
        img_path = os.path.join("assets", uploaded.name)
        with open(img_path, "wb") as f:
            f.write(uploaded.getbuffer())

        st.image(img_path, caption="Preview Nota", use_column_width=True)

        backend = st.radio("Pilih metode OCR:", ["manual", "ai"])

        parsed = extract_receipt(img_path, backend=backend)

        st.session_state.parsed = extract_receipt("assets/nota1.jpg", backend="manual")

        st.subheader("Hasil Parsing")
        st.json(parsed)

        if st.button("Next →"):
            go_to(2)

    st.subheader("Contoh Nota")
    col1, col2 = st.columns(2)

    if col1.button("Gunakan nota1.jpg"):
        st.session_state.parsed = extract_receipt("assets/nota1.jpg", backend="manual")
        go_to(2)

    if col2.button("Gunakan nota2.jpg"):
        st.session_state.parsed = extract_receipt("assets/nota2.jpg", backend="manual")
        go_to(2)


# ========================
# PAGE 2 — SPLIT
# ========================
def page_split():
    st.title("🧮 Split Bill")

    parsed = st.session_state.parsed
    if parsed is None:
        st.error("Silakan upload nota dulu.")
        return

    items = parsed.get("items", [])
    extras = parsed.get("extras", [])
    subtotal = parsed.get("subtotal", 0)
    total = parsed.get("total", 0)

    st.subheader("Daftar Item")
    st.table([{"Item": it["name"], "Harga": it["total_price"]} for it in items])

    st.info(f"Subtotal: Rp {subtotal:,}")
    st.info(f"Total: Rp {total:,}")

    names = st.text_input("Nama peserta (pisahkan dengan koma)", "A,B")
    participants = [n.strip() for n in names.split(",") if n.strip()]

    st.subheader("Assign item ke peserta")
    assignments = {}

    for idx, it in enumerate(items):
        assignments[idx] = st.multiselect(
            f"{it['name']} – Rp {it['total_price']:,}",
            participants,
            default=participants[:1]
        )

    if st.button("Hitung →"):
        st.session_state.report = compute_splits(parsed, assignments, participants)
        go_to(3)

    if st.button("← Back"):
        go_to(1)


# ========================
# PAGE 3 — REPORT
# ========================
def page_report():
    st.title("📊 Report Pembayaran")

    report = st.session_state.report
    if report is None:
        st.error("Belum ada laporan.")
        return

    st.subheader("Total Per Orang")
    st.table([
        {"Nama": p, "Total (Rp)": report["totals"][p]}
        for p in report["totals"]
    ])

    st.subheader("Detail Per Orang")
    for p in report["totals"]:
        st.write(f"### {p}")
        st.table(report["breakdown"][p])

    if st.button("← Back"):
        go_to(2)


# ========================
# PAGE ROUTING
# ========================
if st.session_state.page == 1:
    page_upload()
elif st.session_state.page == 2:
    page_split()
elif st.session_state.page == 3:
    page_report()
else:
    st.write("Error: Page tidak ditemukan.")
