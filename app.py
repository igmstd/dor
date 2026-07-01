import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Penjualan Mobil", layout="wide")
st.title("📊 Dashboard Penjualan Mobil")

df = pd.read_csv("penjualan_mobil_indonesia_jan_jun_2024.csv")
df["tanggal"] = pd.to_datetime(df["tanggal"])

# --- Kontrol interaktif di sidebar ---
kota_pilihan = st.sidebar.multiselect(
    "Pilih kota", options=df["kota"].unique(),
    default=df["kota"].unique()
)
df_filtered = df[df["kota"].isin(kota_pilihan)]

# --- Kartu ringkasan ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Pendapatan", f"Rp {df_filtered['pendapatan_jt'].sum():,.0f} jt")
col2.metric("Rata-rata Bulanan", f"Rp {df_filtered['pendapatan_jt'].mean():,.1f} jt")
col3.metric("Kota Teraktif", df_filtered.groupby("kota")["pendapatan_jt"].sum().idxmax())

# --- Grafik interaktif ---
fig = px.line(df_filtered, x="tanggal", y="pendapatan_jt", color="kota", markers=True)
st.plotly_chart(fig, use_container_width=True)
st.dataframe(df_filtered)

# Buat kolom bulan
df['bulan'] = df['tanggal'].dt.strftime('%Y-%m')

# Agregasi data per Kota dan Bulan
df_agregasi = df.groupby(['kota', 'bulan'], as_index=False)['pendapatan_jt'].sum()

fig_sunburst = px.sunburst(
    df_agregasi, 
    path=["kota", "bulan"], 
    values="pendapatan_jt",
    title="Penjualan per Kota dan Bulan"
)
st.plotly_chart(fig_sunburst, use_container_width=True)

# --- MAP CHART ---
# Agregasi data per kota
df_Kota = df.groupby("kota", as_index=False)["pendapatan_jt"].sum()

# Dictionary koordinat (TAMBAHKAN SEMUA KOTA DI DATASET ANDA)
koordinat = {
    "Balikpapan": (-6.2088, 106.8456),
    "Bandung": (-6.9175, 107.6191),
    "Bandar Lampung": (-7.2575, 112.7521),
    "Bekasi": (-7.7956, 110.3695),
    "Bogor": (-6.9667, 110.4167),
    "Denpasar": (3.5952, 98.6722),
    "Depok": (-5.1477, 119.4327),
    "Jakarta": (-8.6705, 115.2126),
    "Makassar": (-2.9909, 104.7568),
    "Malang": (-6.1783, 106.6319),
    "Manado": (-6.2383, 106.9754),
    "Medan": (-6.4025, 106.7942),
    "Padang": (-6.5950, 106.8167),
    "Palembang": (-7.9797, 112.6304),
    "Pekanbaru": (-1.2379, 116.8529),
    "Samarinda": (1.4748, 124.8421),
    "Semarang": (0.5071, 101.4478),
    "Surabaya": (-0.9471, 100.4172),
    "Tangerang": (-0.0263, 109.3425),
    "Yogyakarta": (-3.3186, 114.5904),
   }

# Fungsi aman untuk mengambil koordinat
def get_koordinat(kota, idx):
    if kota in koordinat:
        return koordinat[kota][idx]
    else:
        return 0  # Default ke 0 jika tidak ditemukan

df_Kota["lat"] = df_Kota["kota"].apply(lambda k: get_koordinat(k, 0))
df_Kota["lon"] = df_Kota["kota"].apply(lambda k: get_koordinat(k, 1))

# Buat map
fig_map = px.scatter_mapbox(
    df_Kota,
    lat="lat",
    lon="lon",
    size="pendapatan_jt",
    color="pendapatan_jt",
    hover_name="kota",
    zoom=3,
    center={"lat": -2.5, "lon": 118},
    mapbox_style="open-street-map",
    title="📍 Sebaran Penjualan per Kota"
)
st.plotly_chart(fig_map, use_container_width=True)

fig = px.line(
    df, 
    x="tanggal", 
    y="pendapatan_jt", 
    color="kota",
    color_discrete_sequence=px.colors.qualitative.Set1   # <--- INI KUNCI WARNA CERAH
)

# Hover biar lebih kece dan informatif
fig.update_traces(
    hovertemplate="<b>%{x}</b><br>Kota: %{data.name}<br>Pendapatan: Rp %{y:.1f} jt<extra></extra>"
)

fig.update_layout(template="plotly_white")  # Ganti background putih biar warna kontras
fig.show()

# Zoom drag-select aktif secara default di semua grafik Plotly
fig = px.line(df, x="tanggal", y="pendapatan_jt")
fig.update_layout(
    xaxis=dict(rangeslider_visible=True)  # Ini untuk zoom
)
fig.show()  # seret pada grafik, atau geser slider bawah