# Dashboard Deteksi Buzzer IGRS — Streamlit (Tema Editorial)

Dashboard investigatif untuk deteksi akun buzzer terkoordinasi pada diskursus
kebijakan IGRS. Tema editorial (Fraunces/Inter/DM Mono, krem–terracotta),
**4 tab** dengan **interpretasi naratif** di setiap bagian — bukan sekadar grafik.

## Cara menjalankan

### Windows
Klik dua kali `run_windows.bat`, atau dari dalam folder ini jalankan:
```

```

### macOS / Linux
```
bash run_unix.sh
```
atau:
```
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

Browser akan terbuka di http://localhost:8501

## Struktur (mengikuti referensi HTML)

- **01 · Validasi Modelpy -m pip install -r requirements.txt
py -m streamlit run app.py** — pipeline 6 langkah, ground truth & Cohen's Kappa,
  kasus ketidaksepakatan anotator, heuristik vs AI, 5-fold CV, confusion
  matrix holdout, threshold tuning, SHAP, sensitivitas DBSCAN.
- **02 · Hasil Investigasi** — ringkasan, distribusi probabilitas bimodal,
  15 akun buzzer paling mencurigakan (metrik + tweet representatif),
  scatter volume vs probabilitas.
- **03 · Analisis Narasi** — kartu topik LDA + trigram, distribusi topik,
  trigram & TF-IDF, tabel klaster, peta PCA klaster.
- **04 · Jaringan Serangan** — ringkasan SNA, graf bipartit sumber→target,
  tabel target, sentralitas PageRank, pola temporal (puncak aktivitas).

Setiap angka dihitung **langsung dari folder `data/`** lewat `data_loader.py`.
Ganti file di `data/` → dashboard otomatis menyesuaikan.

## Isi folder data/ (33 file)

Data inti: `IGRS_Part1/2.csv`, `X_all.csv`, `clean_df.csv`, `tweets_scored.csv`,
`ground_truth_600_berlabel.csv`, `akun_hasil_prediksi_investigative_report.csv`.

Data tambahan yang sebelumnya tidak terpakai, kini dimuat:
`removed_language_noise.csv`, `spam_examples.csv` (funnel penuh 1.439→1.307→1.264),
`annotator_disagreements.csv`, `heuristic_audit.json`, `model_metrics.json`,
`kfold_metrics_per_fold.csv`, `threshold_tuning.csv`, `feature_importance.csv`,
`representative_buzzer_tweets.csv`, `kfold_representative_buzzer.csv`,
`cluster_summary.csv`, `clustered_tweets.csv`, `dbscan_sensitivity.csv`,
`lda_topics.csv`, `lda_per_tweet.csv`, `topic_count.csv`, `top_trigrams.csv`,
`tfidf_top_terms.csv`, `nodes_centrality.csv`, `target_analysis.csv`,
`temporal_windows.csv`, `temporal_top_windows.csv`, dll.

## Catatan angka

Angka dihitung ulang dari CSV saat runtime, sehingga konsisten satu sama lain.
Beberapa berbeda ±1 dari file HTML referensi (mis. 98 vs 99 akun buzzer,
201 vs 203 tweet) karena HTML memakai snapshot ekspor yang sedikit berbeda;
dashboard ini selalu memakai hasil hitung dari `data/`.
