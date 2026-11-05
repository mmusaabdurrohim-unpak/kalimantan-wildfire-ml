from pathlib import Path
import io
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from analysis import validate, analyze, profile, FEATURES

st.set_page_config(page_title='Kalimantan Wildfire Intelligence', page_icon='🌿', layout='wide')
st.title('Kalimantan Wildfire Intelligence')
st.caption('Pengelompokan karakteristik termal hotspot dengan K-Means dan Agglomerative Clustering')
st.info('Hasil bersifat eksploratif. Nomor cluster menggambarkan kemiripan fitur dan tidak menyatakan tingkat bahaya atau prediksi kejadian kebakaran.')
ROOT = Path(__file__).resolve().parent
with st.sidebar:
    st.header('Data dan eksperimen')
    source = st.radio('Sumber data', ['Dataset bawaan', 'Unggah CSV'])
    uploaded = st.file_uploader('Unggah file hotspot CSV', type=['csv']) if source == 'Unggah CSV' else None
    st.caption('Kolom wajib: brightness, bright_t31, frp. Kolom lain bersifat opsional.')
    log_frp = st.checkbox('Transformasi log1p pada FRP', value=True)
    st.caption('StandardScaler selalu digunakan. Seed K-Means 42, n_init 30.')
try:
    if source == 'Unggah CSV':
        if uploaded is None:
            st.warning('Pilih CSV hotspot melalui sidebar untuk memulai.'); st.stop()
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_csv(ROOT/'data'/'kalimantan_hotspots_latest.csv')
    original_n = len(df)
    with st.sidebar:
        for col, title in [('province','Provinsi'), ('instrument','Instrumen')]:
            if col in df.columns:
                options = sorted(df[col].dropna().astype(str).unique())
                selected = st.multiselect(title, options, default=options)
                df = df.loc[df[col].astype(str).isin(selected)]
    df = validate(df).reset_index(drop=True)
except (ValueError, OSError, pd.errors.ParserError, UnicodeError) as exc:
    st.error(str(exc)); st.stop()

@st.cache_data(show_spinner='Menghitung seluruh konfigurasi model...')
def compute(data, use_log):
    return analyze(data, use_log)

try:
    scores, assignments, projection, variance = compute(df, log_frp)
except ValueError as exc:
    st.error(str(exc)); st.stop()
best = scores.iloc[0]
with st.sidebar:
    selection = st.radio('Pilihan hasil', ['Otomatis: silhouette tertinggi', 'Manual'])
    if selection == 'Manual':
        method = st.selectbox('Algoritma', ['K-Means','Agglomerative'])
        k = st.selectbox('Jumlah cluster', sorted(scores.loc[scores.model.eq(method),'k'].tolist()))
    else:
        method, k = str(best['model']), int(best['k'])
labels = assignments[(method,k)]
out, prof = profile(df, labels)
current = scores.loc[scores.model.eq(method) & scores.k.eq(k)].iloc[0]
cols = st.columns(4)
for c, title, value in zip(cols, ['Observasi aktif','Model aktif','Jumlah cluster','Silhouette'], [len(df),method,k,f'{current.silhouette:.4f}']):
    c.metric(title,value)
st.caption(f'{len(df)} dari {original_n} observasi. Mengubah filter atau transformasi akan menghitung ulang cluster, sehingga hasil dapat berbeda dari PPT yang memakai seluruh data bawaan.')
tabs = st.tabs(['01 Business Objective','02 Data Overview','03 EDA','04 Feature Engineering','05 Modelling & Evaluation'])
with tabs[0]:
    st.subheader('Tujuan penelitian')
    st.write('Mengidentifikasi kelompok observasi hotspot dengan karakteristik termal serupa dan membandingkan dua algoritma clustering pada skenario yang sama.')
    st.write('Pertanyaan: bagaimana profil tiap kelompok berdasarkan brightness, bright_t31, dan FRP?')
    st.write('Manfaat: eksplorasi awal untuk penelaahan data karhutla. Penetapan prioritas lapangan memerlukan data dan validasi tambahan.')
with tabs[1]:
    st.subheader('Data aktif')
    st.dataframe(df, width='stretch')
    st.write('Nilai kosong per kolom')
    st.dataframe(df.isna().sum().rename('nilai_kosong'), width='stretch')
    st.write(f'Baris duplikat persis: {df.duplicated().sum()}')
    if source == 'Dataset bawaan':
        st.caption('Hotspot: 180 × 30, 10–24 Agustus 2026. Cuaca: 8 stasiun pada satu waktu. Deret waktu: 90 hari Mei–Juli 2026. Data pendukung tidak digabung ke model.')
        with st.expander('Audit dua CSV pendukung'):
            w = pd.read_csv(ROOT/'data'/'kalimantan_weather_latest.csv')
            t = pd.read_csv(ROOT/'data'/'kalimantan_early_fire_onset_timeseries.csv')
            st.write('Cuaca'); st.dataframe(w)
            cs=['kalteng_hotspots','kalbar_hotspots','kalsel_hotspots','kaltim_hotspots','kaltara_hotspots']
            bad=t.loc[t[cs].sum(axis=1).ne(t.total_hotspots)].copy()
            bad['province_sum']=bad[cs].sum(axis=1)
            st.write('Selisih total provinsi pada 9 dan 17 Juli 2026'); st.dataframe(bad)
            st.caption('Sumber asli, arti is_peatland_target, rumus label, dan status data sintetis/observasional perlu dikonfirmasi.')
with tabs[2]:
    st.subheader('Distribusi fitur')
    fig, axs = plt.subplots(1,3,figsize=(12,3.3))
    for ax,f in zip(axs,FEATURES):
        ax.hist(df[f],bins=15,color='#16846b',edgecolor='white'); ax.set_title(f)
    fig.tight_layout(); st.pyplot(fig);plt.close(fig)
    st.dataframe(df[FEATURES].describe().round(2),width='stretch')
    if 'instrument' in df:
        st.write('Median fitur menurut instrumen');st.dataframe(df.groupby('instrument')[FEATURES].median())
    if 'province' in df:
        st.write('Jumlah observasi per provinsi');st.bar_chart(df.province.value_counts())
with tabs[3]:
    st.subheader('Fitur pembentuk cluster')
    st.dataframe(pd.DataFrame({'fitur':FEATURES,'perlakuan':['StandardScaler','StandardScaler','log1p + StandardScaler' if log_frp else 'StandardScaler']}),hide_index=True)
    st.write('ID, koordinat, tanggal, hazard_score, hazard_severity, hazard_badge, dan hazard_color tidak menjadi fitur model. Koordinat hanya digunakan pada visualisasi.')
    st.warning('MODIS dan VIIRS dapat memiliki karakteristik pengukuran berbeda. Gunakan filter instrumen untuk analisis terpisah. Definisi dan kesetaraan fitur termal perlu dikonfirmasi.')
with tabs[4]:
    st.subheader('Perbandingan konfigurasi')
    st.dataframe(scores.round(4),hide_index=True,width='stretch')
    fig, ax=plt.subplots(figsize=(9,3.4))
    for m,g in scores.groupby('model'):
        g=g.sort_values('k');ax.plot(g.k,g.silhouette,'o-',label=m)
    ax.set(xlabel='Jumlah cluster',ylabel='Silhouette');ax.legend();fig.tight_layout();st.pyplot(fig);plt.close(fig)
    st.subheader(f'Profil {method}, k={k}')
    st.dataframe(prof.round(2),width='stretch')
    st.caption('Median menggunakan satuan asli. Jangan mengurutkan tingkat bahaya berdasarkan nomor cluster.')
    fig,ax=plt.subplots(figsize=(8,4))
    for cl in sorted(out.cluster.unique()):
        mask=labels==cl;ax.scatter(projection[mask,0],projection[mask,1],label=f'Cluster {cl}',alpha=.8)
    ax.set(xlabel='PC1',ylabel='PC2',title='Proyeksi PCA');ax.legend();fig.tight_layout();st.pyplot(fig);plt.close(fig)
    st.caption(f'Dua komponen PCA menjelaskan {variance.sum():.2%} variasi fitur terolah. Visualisasi ini bukan validasi risiko.')
    if {'latitude','longitude'}.issubset(out.columns):
        coords=out[['latitude','longitude']].apply(pd.to_numeric,errors='coerce')
        good=coords.notna().all(axis=1) & coords.latitude.between(-90,90) & coords.longitude.between(-180,180)
        if good.any():
            mapped=coords.loc[good].copy();palette=['#0f766e','#f97316','#7c3aed','#db2777','#2563eb','#ca8a04']
            mapped['color']=[palette[int(c)%len(palette)] for c in out.loc[good,'cluster']]
            st.map(mapped,latitude='latitude',longitude='longitude',color='color')
            st.caption('Peta dasar memerlukan internet. Hasil analisis dan PCA tetap tersedia tanpa peta dasar.')
    if 'hazard_severity' in out:
        st.write('Perbandingan deskriptif dengan label bahaya');st.dataframe(pd.crosstab(out.cluster,out.hazard_severity))
    st.download_button('Unduh hasil cluster CSV',out.to_csv(index=False).encode('utf-8-sig'),'hotspot_dengan_cluster.csv','text/csv')
    st.download_button('Unduh evaluasi CSV',scores.to_csv(index=False).encode('utf-8-sig'),'evaluasi_model.csv','text/csv')
    st.download_button('Unduh profil CSV',prof.to_csv().encode('utf-8-sig'),'profil_cluster.csv','text/csv')
    st.write('Evaluasi menggunakan sampel yang sama untuk eksplorasi. Generalisasi memerlukan data baru dari periode atau wilayah lain. Kualitas cluster tidak membuktikan sebab kebakaran.')
