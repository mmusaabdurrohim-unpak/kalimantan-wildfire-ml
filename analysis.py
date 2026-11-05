"""Analisis bersama untuk aplikasi dan pengujian."""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.decomposition import PCA

FEATURES = ['brightness', 'bright_t31', 'frp']

def validate(df):
    missing = [c for c in FEATURES if c not in df.columns]
    if missing:
        raise ValueError('Kolom wajib belum tersedia: ' + ', '.join(missing))
    clean = df.copy()
    for c in FEATURES:
        clean[c] = pd.to_numeric(clean[c], errors='coerce')
    a = clean[FEATURES].to_numpy(dtype=float)
    if not np.isfinite(a).all():
        raise ValueError('Fitur wajib harus berisi angka lengkap dan berhingga. Perbaiki nilai kosong/teks pada CSV.')
    if (clean.frp < 0).any():
        raise ValueError('FRP tidak boleh negatif.')
    if len(clean) < 8:
        raise ValueError('Gunakan minimal 8 observasi setelah filter untuk eksperimen ini.')
    if clean[FEATURES].drop_duplicates().shape[0] < 3:
        raise ValueError('Diperlukan minimal 3 kombinasi fitur berbeda.')
    if len(clean) > 3000:
        raise ValueError('Demo dibatasi 3.000 observasi agar perhitungan jarak tetap ringan. Unggah subset yang sesuai.')
    return clean

def analyze(df, log_frp=True):
    df = validate(df)
    X = df[FEATURES].copy()
    if log_frp:
        X.frp = np.log1p(X.frp)
    Z = StandardScaler().fit_transform(X)
    maxk = min(6, len(df)-1, X.drop_duplicates().shape[0])
    rows, assignments = [], {}
    for k in range(2, maxk+1):
        for name, model in [('K-Means', KMeans(n_clusters=k, n_init=30, random_state=42)),
                            ('Agglomerative', AgglomerativeClustering(n_clusters=k, linkage='ward'))]:
            labels = model.fit_predict(Z)
            sizes = pd.Series(labels).value_counts().sort_index()
            if not 1 < len(sizes) < len(df):
                continue
            rows.append({'model': name, 'k': k, 'silhouette': silhouette_score(Z, labels),
                         'davies_bouldin': davies_bouldin_score(Z, labels),
                         'ukuran_cluster': '/'.join(map(str, sizes.tolist()))})
            assignments[(name, k)] = labels
    if not rows:
        raise ValueError('Data tidak menghasilkan partisi yang dapat dievaluasi.')
    scores = pd.DataFrame(rows).sort_values(['silhouette', 'davies_bouldin'], ascending=[False, True]).reset_index(drop=True)
    pca = PCA(n_components=2)
    projection = pca.fit_transform(Z)
    return scores, assignments, projection, pca.explained_variance_ratio_

def profile(df, labels):
    out = df.copy()
    out['cluster'] = labels
    p = out.groupby('cluster').agg(jumlah=('cluster','size'), brightness_median=('brightness','median'),
                                 bright_t31_median=('bright_t31','median'), frp_median=('frp','median'))
    return out, p
