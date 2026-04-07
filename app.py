import streamlit as st
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from datetime import datetime
import io

# ===== 1. CONFIG UTAMA =====
st.set_page_config(page_title="Sistem Apriori Obat", layout="wide")

# ===== 2. STYLE CSS (ELEGANT PURPLE - NO NEON) =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&family=Poppins:wght@700;800;900&display=swap');

/* Background Aplikasi */
.stApp {
    background: linear-gradient(135deg, #0f0a1f 0%, #1a0f3d 50%, #2a145f 100%);
}

* {
    font-family: 'Montserrat', sans-serif;
}

h1, h2, h3, h4, h5, h6, p, label {
    color: white !important;
}

/* ===== SIDEBAR STYLING ===== */
section[data-testid="stSidebar"] {
    background: #140a2e !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
    min-width: 320px !important;
}

/* Mengatur scrollbar sidebar agar tidak geser kanan-kiri */
section[data-testid="stSidebar"] > div {
    overflow-y: auto !important;
    overflow-x: hidden !important;
}

/* --- JUDUL SIDEBAR (CLEAN & BOLD) --- */
.sidebar-header-box {
    text-align: center;
    padding: 30px 10px 10px 10px;
    margin-bottom: 20px;
}

.title-solid {
    font-family: 'Poppins', sans-serif;
    font-size: 28px;
    font-weight: 800;
    line-height: 1.1;
    color: #a366ff !important; /* Warna ungu solid yang tegas */
    letter-spacing: 1px;
    margin-bottom: 5px !important;
}

.subtitle-clean {
    font-family: 'Montserrat', sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.5) !important;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-top: 0px;
}

/* Sidebar Menu Buttons */
.stSidebar div[data-testid="stButton"] button {
    background-color: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(127, 63, 191, 0.1) !important;
    color: rgba(255, 255, 255, 0.8) !important;
    text-align: left !important;
    padding: 12px 18px !important;
    border-radius: 10px !important;
    margin-bottom: -5px !important;
    transition: 0.3s ease;
}

.stSidebar div[data-testid="stButton"] button:hover {
    background-color: rgba(127, 63, 191, 0.1) !important;
    border-color: #a366ff !important;
    color: white !important;
    transform: translateX(5px);
}

/* Card Metrics */
.metric-card {
    background: rgba(255, 255, 255, 0.04);
    padding: 20px;
    border-radius: 15px;
    border-top: 3px solid #7F3FBF;
    text-align: center;
}

.about-card {
    background: rgba(255, 255, 255, 0.03);
    padding: 20px;
    border-radius: 15px;
    border-left: 4px solid #7F3FBF;
}
</style>
""", unsafe_allow_html=True)

# ===== 3. SESSION SECURITY =====
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False

if "data" not in st.session_state: st.session_state.data = []
if "rules" not in st.session_state: st.session_state.rules = pd.DataFrame()
if "history" not in st.session_state: st.session_state.history = []
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

def set_menu(m):
    st.session_state.menu = m

# ===== 4. LOGIN INTERFACE =====
if not st.session_state.is_authenticated:
    st.title("🔐 Login Administrator")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Masuk Sistem", use_container_width=True):
        if u == "admin" and p == "123":
            st.session_state.is_authenticated = True
            st.rerun()
        else: st.error("Kredensial salah, akses ditolak.")

# ===== 5. MAIN SYSTEM (LOGGED IN) =====
else:
    with st.sidebar:
        # HEADER SIDEBAR (VERSI CLEAN)
        st.markdown("""
        <div class="sidebar-header-box">
            <p class="title-solid">DATA MINING</p>
            <p class="subtitle-clean">Obat Hipertensi</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.button("🏠 Dashboard", use_container_width=True, on_click=set_menu, args=("Dashboard",))
        st.button("📊 Data Transaksi", use_container_width=True, on_click=set_menu, args=("Data Transaksi",))
        st.button("⚙️ Proses Apriori", use_container_width=True, on_click=set_menu, args=("Proses Apriori",))
        st.button("📈 Hasil Analisis", use_container_width=True, on_click=set_menu, args=("Hasil",))
        st.button("📤 Export Laporan", use_container_width=True, on_click=set_menu, args=("Export",))
        st.button("🕘 Riwayat Pengujian", use_container_width=True, on_click=set_menu, args=("Riwayat",))
        st.button("ℹ️ Tentang Sistem", use_container_width=True, on_click=set_menu, args=("Tentang",))
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.is_authenticated = False
            st.rerun()

    menu = st.session_state.menu
    
    # --- DASHBOARD ---
    if menu == "Dashboard":
        st.title("📊 Ringkasan Sistem")
        c1, c2, c3 = st.columns(3)
        unique_it = set()
        if st.session_state.data:
            for r in st.session_state.data: unique_it.update([i.strip() for i in r['Item'].split(',')])
        
        with c1: st.markdown(f'<div class="metric-card"><h3>Total Data</h3><h2>{len(st.session_state.data)}</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><h3>Varian Obat</h3><h2>{len(unique_it) if unique_it else 0}</h2></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card"><h3>Aturan</h3><h2>{len(st.session_state.rules)}</h2></div>', unsafe_allow_html=True)

    # --- DATA TRANSAKSI ---
    elif menu == "Data Transaksi":
        st.title("📁 Olah Data Transaksi")
        f = st.file_uploader("Impor Excel", type=["xlsx"])
        if f:
            st.session_state.data = pd.read_excel(f).to_dict(orient="records")
            st.success("Data berhasil diunggah!")
        
        st.subheader("Input Data Manual")
        t_id = st.text_input("ID Transaksi")
        t_it = st.text_input("Nama Obat (Gunakan koma)")
        if st.button("Simpan Data"):
            if not t_id or not t_it: st.warning("ID dan Nama Obat tidak boleh kosong!")
            else:
                st.session_state.data.append({"ID Transaksi": t_id, "Item": t_it})
                st.toast("Data disimpan ke sesi.")
                st.rerun()
        if st.session_state.data:
            st.dataframe(pd.DataFrame(st.session_state.data), use_container_width=True)

    # --- PROSES APRIORI ---
    elif menu == "Proses Apriori":
        st.title("⚙️ Jalankan Algoritma")
        if not st.session_state.data: st.warning("Data belum tersedia untuk diproses.")
        else:
            df = pd.DataFrame(st.session_state.data)
            it_set = set()
            for items in df["Item"]: it_set.update([i.strip() for i in items.split(",")])
            enc = [{it: (1 if it in [i.strip() for i in row['Item'].split(",")] else 0) for it in it_set} for row in st.session_state.data]
            df_enc = pd.DataFrame(enc)
            s = st.slider("Support", 0.01, 1.0, 0.1)
            c = st.slider("Confidence", 0.01, 1.0, 0.1)
            if st.button("Mulai Hitung"):
                freq = apriori(df_enc, min_support=s, use_colnames=True)
                rules = association_rules(freq, metric="confidence", min_threshold=c)
                st.session_state.rules = rules
                st.session_state.history.append({"Waktu": datetime.now().strftime("%H:%M"), "Aturan": len(rules)})
                st.success("Proses selesai.")

    # --- HASIL ---
    elif menu == "Hasil":
        st.title("📈 Hasil Pola")
        if st.session_state.rules.empty: st.info("Silakan jalankan proses Apriori terlebih dahulu.")
        else:
            res = st.session_state.rules.copy()
            res["Jika Beli"] = res["antecedents"].apply(lambda x: ', '.join(list(x)))
            res["Maka Beli"] = res["consequents"].apply(lambda x: ', '.join(list(x)))
            st.dataframe(res[["Jika Beli", "Maka Beli", "support", "confidence", "lift"]], use_container_width=True)

    # --- EXPORT ---
    elif menu == "Export":
        st.title("📤 Export Laporan")
        if not st.session_state.rules.empty:
            out = io.BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as w:
                pd.DataFrame(st.session_state.rules).to_excel(w, index=False)
            st.download_button("📥 Unduh Hasil (.xlsx)", out.getvalue(), "Laporan_Obat.xlsx")

    # --- RIWAYAT ---
    elif menu == "Riwayat":
        st.title("🕘 Log Pengujian")
        if st.session_state.history: 
            st.table(pd.DataFrame(st.session_state.history))
            if st.button("Hapus Log"):
                st.session_state.history = []
                st.rerun()
        else: st.info("Belum ada riwayat pengujian.")

    # --- TENTANG ---