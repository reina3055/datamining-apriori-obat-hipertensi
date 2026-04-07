import streamlit as st
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from datetime import datetime
import io

# ===== 1. CONFIG UTAMA =====
st.set_page_config(page_title="Sistem Apriori Obat", layout="wide", page_icon="💊")

# ===== 2. STYLE CSS =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&family=Poppins:wght@700;800;900&display=swap');
.stApp { background: linear-gradient(135deg, #0f0a1f 0%, #1a0f3d 50%, #2a145f 100%); }
* { font-family: 'Montserrat', sans-serif; }
h1, h2, h3, h4, h5, h6, p, label { color: white !important; }
section[data-testid="stSidebar"] { background: #140a2e !important; border-right: 1px solid rgba(255, 255, 255, 0.05); }
.sidebar-header-box { text-align: center; padding: 20px 10px; }
.title-solid { font-family: 'Poppins', sans-serif; font-size: 24px; font-weight: 800; color: #a366ff !important; margin-bottom: 0px !important; }
.metric-card { background: rgba(255, 255, 255, 0.04); padding: 20px; border-radius: 15px; border-top: 3px solid #7F3FBF; text-align: center; margin-bottom: 20px; }
.about-card { background: rgba(255, 255, 255, 0.03); padding: 25px; border-radius: 15px; border-left: 5px solid #a366ff; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# ===== 3. SESSION STATE =====
if "is_authenticated" not in st.session_state: st.session_state.is_authenticated = False
if "data" not in st.session_state: st.session_state.data = []
if "rules" not in st.session_state: st.session_state.rules = pd.DataFrame()
if "history" not in st.session_state: st.session_state.history = []
if "menu" not in st.session_state: st.session_state.menu = "Dashboard"

def set_menu(m): st.session_state.menu = m

# ===== 4. LOGIN INTERFACE =====
if not st.session_state.is_authenticated:
    st.title("🔐 Login Administrator")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Masuk Sistem", use_container_width=True):
        if u == "admin" and p == "123":
            st.session_state.is_authenticated = True
            st.rerun()
        else: st.error("Kredensial salah.")

# ===== 5. MAIN SYSTEM =====
else:
    with st.sidebar:
        st.markdown('<div class="sidebar-header-box"><p class="title-solid">DATA MINING</p><p style="color:rgba(255,255,255,0.5); font-size:10px; letter-spacing:2px;">OBAT HIPERTENSI</p></div>', unsafe_allow_html=True)
        st.button("🏠 Dashboard", use_container_width=True, on_click=set_menu, args=("Dashboard",))
        st.button("📊 Data Transaksi", use_container_width=True, on_click=set_menu, args=("Data Transaksi",))
        st.button("⚙️ Proses Apriori", use_container_width=True, on_click=set_menu, args=("Proses",))
        st.button("📈 Hasil Analisis", use_container_width=True, on_click=set_menu, args=("Hasil",))
        st.button("📤 Export Laporan", use_container_width=True, on_click=set_menu, args=("Export",))
        st.button("🕘 Riwayat Pengujian", use_container_width=True, on_click=set_menu, args=("Riwayat",))
        st.button("ℹ️ Tentang Sistem", use_container_width=True, on_click=set_menu, args=("Tentang",))
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.is_authenticated = False
            st.rerun()

    menu = st.session_state.menu
    
    if menu == "Dashboard":
        st.title("📊 Ringkasan Sistem")
        c1, c2, c3 = st.columns(3)
        unique_it = set()
        for r in st.session_state.data: unique_it.update([i.strip() for i in str(r['Item']).split(',')])
        with c1: st.markdown(f'<div class="metric-card"><h3>Total Data</h3><h2>{len(st.session_state.data)}</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><h3>Varian Obat</h3><h2>{len(unique_it)}</h2></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card"><h3>Aturan</h3><h2>{len(st.session_state.rules)}</h2></div>', unsafe_allow_html=True)

    elif menu == "Data Transaksi":
        st.title("📁 Olah Data Transaksi")
        f = st.file_uploader("Impor Excel", type=["xlsx"])
        if f:
            st.session_state.data = pd.read_excel(f).to_dict(orient="records")
            st.success("Data diimpor!")
            st.rerun()
        
        st.subheader("📝 Input Manual")
        # Auto ID
        next_id = f"T{len(st.session_state.data)+1:03d}"
        c_id, c_it = st.columns([1, 2])
        t_id = c_id.text_input("ID", value=next_id)
        t_it = c_it.text_input("Nama Obat (Koma sebagai pemisah)")
        
        if st.button("Simpan Data", use_container_width=True):
            if t_id and t_it:
                st.session_state.data.append({"ID Transaksi": t_id, "Item": t_it})
                st.success(f"Data {t_id} tersimpan!")
                st.rerun()

        st.markdown("---")
        if st.session_state.data:
            st.dataframe(pd.DataFrame(st.session_state.data), use_container_width=True)
            if st.button("🗑️ Reset"): st.session_state.data = []; st.rerun()

    elif menu == "Proses":
        st.title("⚙️ Jalankan Apriori")
        if not st.session_state.data: st.warning("Data kosong.")
        else:
            s = st.slider("Support", 0.01, 1.0, 0.1)
            c = st.slider("Confidence", 0.01, 1.0, 0.5)
            if st.button("Mulai Hitung"):
                # Encoding data
                df = pd.DataFrame(st.session_state.data)
                it_set = set()
                for items in df["Item"]: it_set.update([i.strip() for i in str(items).split(",")])
                enc = [{it: (1 if it in [i.strip() for i in str(row['Item']).split(",")] else 0) for it in it_set} for row in st.session_state.data]
                df_enc = pd.DataFrame(enc)
                freq = apriori(df_enc, min_support=s, use_colnames=True)
                if not freq.empty:
                    rules = association_rules(freq, metric="confidence", min_threshold=c)
                    st.session_state.rules = rules
                    st.session_state.history.append({"Waktu": datetime.now().strftime("%H:%M"), "Aturan": len(rules)})
                    st.success("Analisis selesai!")
                else: st.error("Support terlalu tinggi.")

    elif menu == "Hasil":
        st.title("📈 Hasil Pola")
        if st.session_state.rules.empty: st.info("Jalankan Apriori dulu.")
        else:
            res = st.session_state.rules.copy()
            res["Jika Beli"] = res["antecedents"].apply(lambda x: ', '.join(list(x)))
            res["Maka Beli"] = res["consequents"].apply(lambda x: ', '.join(list(x)))
            st.dataframe(res[["Jika Beli", "Maka Beli", "support", "confidence", "lift"]], use_container_width=True)

    elif menu == "Export":
        st.title("📤 Export Laporan")
        if st.session_state.rules.empty: st.warning("Belum ada hasil untuk di-export.")
        else:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                st.session_state.rules.to_excel(writer, index=False, sheet_name='Sheet1')
            st.download_button(label="📥 Download Excel", data=buffer.getvalue(), file_name="Laporan_Apriori.xlsx", mime="application/vnd.ms-excel")

    elif menu == "Riwayat":
        st.title("🕘 Log Pengujian")
        if st.session_state.history: st.table(pd.DataFrame(st.session_state.history))
        else: st.info("Kosong.")

    elif menu == "Tentang":
        st.title("ℹ️ Tentang Sistem")
        st.markdown("""
        <div class="about-card">
        <h3>Sistem Analisis Apriori Obat Hipertensi</h3>
        <p>Aplikasi ini dikembangkan untuk mengolah data transaksi obat guna menemukan pola kombinasi obat yang paling sering dibeli secara bersamaan.</p>
        <p><b>Dibuat oleh:</b> Reina</p>
        <p><b>Metode:</b> Algoritma Apriori (Data Mining)</p>
        </div>
        """, unsafe_allow_html=True)