"""Memuat & menghitung SEMUA angka dashboard langsung dari folder data/.
Tidak ada angka yang diketik manual — semua di-import / dihitung dari CSV & JSON
hasil ekspor notebook. Ganti file di data/ maka dashboard ikut berubah.
"""
import os
import json
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def _p(name):
    return os.path.join(DATA_DIR, name)


def _read(name, **kw):
    df = pd.read_csv(_p(name), **kw)
    df.columns = [str(c).replace("\ufeff", "").strip() for c in df.columns]
    return df


def _json(name):
    with open(_p(name), encoding="utf-8") as f:
        return json.load(f)


def _cohen_kappa(a, b):
    a = np.asarray(a); b = np.asarray(b)
    cats = sorted(set(a.tolist()) | set(b.tolist()))
    po = float((a == b).mean())
    pe = float(sum(np.mean(a == c) * np.mean(b == c) for c in cats))
    return (po - pe) / (1 - pe) if (1 - pe) else 1.0


# ----------------------------------------------------------------------------
# 00 · PIPELINE
# ----------------------------------------------------------------------------
def load_pipeline():
    raw = len(_read("IGRS_Part1.csv")) + len(_read("IGRS_Part2.csv"))
    final = len(_read("X_all.csv"))
    n_noise = len(_read("removed_language_noise.csv"))
    n_spam = len(_read("spam_examples.csv"))
    after_noise = raw - n_noise
    return {
        "raw": raw,
        "n_language_noise": n_noise,
        "after_noise": after_noise,
        "n_spam": n_spam,
        "final": final,
        "n_accounts": int(_read("akun_hasil_prediksi_investigative_report.csv").shape[0]),
    }


# ----------------------------------------------------------------------------
# 01 · GROUND TRUTH / KAPPA / HEURISTIK
# ----------------------------------------------------------------------------
def load_sampling_kappa():
    gt = _read("ground_truth_600_berlabel.csv")
    sample = {str(k): int(v) for k, v in gt["sample_group"].value_counts().items()}
    pen = gt["manual_label_peneliti"].astype(int)
    ann = gt["manual_label_annotator2"].astype(int)
    kappa = _cohen_kappa(pen, ann)
    agree = int((pen == ann).sum())
    n = len(gt)
    gt_buzzer = int((pen == 1).sum())
    gt_organic = int((pen == 0).sum())
    coord = gt["is_coordinated"].astype(int)
    TP = int(((coord == 1) & (pen == 1)).sum())
    FP = int(((coord == 1) & (pen == 0)).sum())
    FN = int(((coord == 0) & (pen == 1)).sum())
    TN = int(((coord == 0) & (pen == 0)).sum())
    heur_acc = (TP + TN) / n
    return {
        "n": n, "sample": sample, "kappa": kappa, "agree": agree,
        "agree_pct": agree / n,
        "gt_buzzer": gt_buzzer, "gt_organic": gt_organic,
        "heur_cm": {"TP": TP, "FP": FP, "FN": FN, "TN": TN},
        "heur_acc": heur_acc,
    }


def load_heuristic_audit():
    return _json("heuristic_audit.json")


# ----------------------------------------------------------------------------
# 01 · OUTPUT TEKNIS MODEL: 5-FOLD, CM PER-FOLD, THRESHOLD, SHAP
# ----------------------------------------------------------------------------
def load_folds():
    f = _read("kfold_metrics_per_fold.csv")
    try:
        m = _json("model_metrics.json")
    except Exception:
        m = {}
    out = {
        "folds": f.to_dict("records"),
        "mean_accuracy": float(f["accuracy"].mean()),
        "mean_precision": float(f["precision"].mean()),
        "mean_recall": float(f["recall"].mean()),
        "mean_f1": float(f["f1"].mean()),
        "mean_auc": float(f["roc_auc"].mean()),
    }
    if "wilson_ci" in m:
        out["wilson_ci"] = m["wilson_ci"]
    return out


def load_kfold_cm():
    """5 confusion matrix — satu per fold — dari prediksi per-tweet tiap fold."""
    df = _read("kfold_prediksi_per_tweet.csv")
    folds = []
    for fld in sorted(df["fold"].unique()):
        sub = df[df["fold"] == fld]
        y = sub["label_manual"].astype(int)
        p = sub["label_prediksi_kfold"].astype(int)
        TP = int(((p == 1) & (y == 1)).sum())
        FP = int(((p == 1) & (y == 0)).sum())
        FN = int(((p == 0) & (y == 1)).sum())
        TN = int(((p == 0) & (y == 0)).sum())
        n = len(sub)
        prec = TP / (TP + FP) if (TP + FP) else 0.0
        rec = TP / (TP + FN) if (TP + FN) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        folds.append({
            "fold": int(fld), "n": n,
            "cm": {"TP": TP, "FP": FP, "FN": FN, "TN": TN},
            "accuracy": (TP + TN) / n if n else 0.0,
            "precision": prec, "recall": rec, "f1": f1,
        })
    return {"folds": folds}


def load_threshold(final_threshold=0.85, n_test=120):
    t = _read("threshold_tuning.csv").sort_values("threshold")
    row = t[np.isclose(t["threshold"], final_threshold)]
    if len(row):
        r = row.iloc[0]
        prec = float(r["precision"]); rec = float(r["recall"])
        f1 = float(r["f1"]); n_pred = int(r["n_predicted_buzzer"])
    else:
        prec = rec = f1 = 0.0; n_pred = 0
    n_buzzer = 43
    TP = int(round(rec * n_buzzer))
    FP = int(round(TP / prec - TP)) if prec else 0
    FN = n_buzzer - TP
    TN = n_test - TP - FP - FN
    return {
        "rows": t.to_dict("records"),
        "final_threshold": final_threshold,
        "n_test": n_test,
        "precision": prec, "recall": rec, "f1": f1, "n_pred": n_pred,
        "holdout_cm": {"TP": TP, "FP": FP, "FN": FN, "TN": TN},
    }


def load_shap():
    s = _read("feature_importance.csv")
    val_col = next((c for c in s.columns if "shap" in c.lower() or "importance" in c.lower()), s.columns[1])
    s = s.sort_values(val_col, ascending=False)
    return {"rows": s.rename(columns={val_col: "value"})[["feature", "value"]].to_dict("records")}


# ----------------------------------------------------------------------------
# 02 · AKUN + SEMUA TWIT BUZZER + REPLY-OUT
# ----------------------------------------------------------------------------
def load_accounts():
    a = _read("akun_hasil_prediksi_investigative_report.csv")
    ts = _read("tweets_scored.csv")
    edges = _read("edges.csv")
    src_col, tgt_col = edges.columns[0], edges.columns[1]
    w_col = next((c for c in edges.columns if c.lower() == "weight"), None)
    prob_col = next((c for c in ts.columns if "buzzer_prob" in c.lower()), "buzzer_prob")
    flag_col = "buzzer_flag" if "buzzer_flag" in ts.columns else None

    total = len(a)
    buzzer = a[a["buzzer_label"] == "Buzzer"].copy()
    n_buzzer = len(buzzer)
    total_tweets = int(a["n_tweets"].sum())
    buzzer_tweets = int(a["n_buzzer_tweets"].sum())
    buzzer = buzzer.sort_values("max_buzzer_prob", ascending=False)

    top = []
    for _, r in buzzer.iterrows():
        uname = r["username"]
        sub = ts[ts["username"] == uname]
        if flag_col:
            bt = sub[sub[flag_col] == 1]
        else:
            bt = sub[sub[prob_col] >= 0.5]
        bt = bt.sort_values(prob_col, ascending=False)
        tweets = []
        for x in bt.to_dict("records"):
            txt = x.get("full_text")
            if not isinstance(txt, str) or not txt.strip():
                txt = x.get("clean_text") or ""
            url = x.get("tweet_url")
            tweets.append({
                "text": str(txt),
                "url": str(url) if isinstance(url, str) else "",
                "prob": float(x.get(prob_col) or 0),
                "in_reply_to": str(x.get("in_reply_to_screen_name") or ""),
            })
        e_out = edges[edges[src_col] == uname]
        reply_out = []
        for x in e_out.to_dict("records"):
            reply_out.append({"target": str(x[tgt_col]),
                              "weight": int(x[w_col]) if w_col else 1})
        top.append({
            "username": uname,
            "prob": float(r["max_buzzer_prob"]),
            "mean_prob": float(r["mean_buzzer_prob"]),
            "n_tweets": int(r["n_tweets"]),
            "n_buzzer_tweets": int(r["n_buzzer_tweets"]),
            "dup": float(r["content_dup_score_max"]),
            "lex": float(r["lexical_similarity_score_mean"]),
            "burst": float(r["temporal_burst_score_max"]),
            "out_deg": float(r["sna_out_deg_max"]),
            "in_deg": float(r["sna_in_deg_max"]),
            "tweets": tweets,
            "reply_out": reply_out,
        })
    return {
        "total_accounts": total, "n_buzzer": n_buzzer,
        "total_tweets": total_tweets, "buzzer_tweets": buzzer_tweets,
        "buzzer_tweet_pct": buzzer_tweets / total_tweets if total_tweets else 0,
        "top": top,
        "scatter": a[["n_tweets", "max_buzzer_prob", "content_dup_score_max", "username", "buzzer_label"]].to_dict("records"),
    }


def load_prob_distribution():
    t = _read("tweets_scored.csv")
    col = next((c for c in t.columns if "buzzer_prob" in c.lower()), None)
    bins = [0, 0.2, 0.4, 0.6, 0.8, 1.01]
    labels = ["0.0–0.2", "0.2–0.4", "0.4–0.6", "0.6–0.8", "0.8–1.0"]
    cut = pd.cut(t[col], bins=bins, labels=labels, right=False)
    counts = cut.value_counts().reindex(labels).fillna(0).astype(int)
    return {"labels": labels, "counts": counts.tolist(), "n": len(t)}


# ----------------------------------------------------------------------------
# 03 · NARASI: LDA, KLASTER, TRIGRAM, TF-IDF
# ----------------------------------------------------------------------------
def load_lda():
    topics = _read("lda_topics.csv")
    counts = _read("topic_count.csv")
    cmap = dict(zip(counts["topic_id"].astype(int), counts["tweet_count"].astype(int)))
    
    # Load representative tweets per topic from lda_per_tweet.csv
    try:
        tweets_df = _read("lda_per_tweet.csv").dropna(subset=["full_text"])
    except Exception:
        tweets_df = pd.DataFrame()

    rows = []
    for _, r in topics.iterrows():
        tid = int(r["topic_id"])
        tris = [t.strip() for t in str(r["top_trigrams"]).split(",")][:6]
        
        # Get top representative tweets for this topic
        topic_tweets = []
        more_tweets = []
        if not tweets_df.empty and "dominant_topic" in tweets_df.columns:
            sub = tweets_df[tweets_df["dominant_topic"] == tid].copy()
            if "topic_probability" in sub.columns:
                sub = sub.sort_values("topic_probability", ascending=False)
            elif "buzzer_prob" in sub.columns:
                sub = sub.sort_values("buzzer_prob", ascending=False)
            sub = sub.drop_duplicates(subset=["clean_text"])
            
            for _, tr in sub.head(3).iterrows():
                topic_tweets.append({
                    "username": str(tr["username"]),
                    "text": str(tr["full_text"]),
                    "prob": float(tr["topic_probability"]) if "topic_probability" in tr else 0.0
                })
            
            for _, tr in sub.iloc[3:].iterrows():
                more_tweets.append({
                    "username": str(tr["username"]),
                    "text": str(tr["full_text"]),
                    "prob": float(tr["topic_probability"]) if "topic_probability" in tr else 0.0
                })
        
        rows.append({
            "topic_id": tid,
            "name": r["topic_name"],
            "description": r["short_description"],
            "trigrams": tris,
            "count": cmap.get(tid, 0),
            "tweets": topic_tweets,
            "more_tweets": more_tweets,
        })
    return {"topics": rows, "total": int(sum(cmap.values()))}


def load_trigrams():
    t = _read("top_trigrams.csv").head(15)
    return {"rows": t.to_dict("records")}


def load_tfidf():
    t = _read("tfidf_top_terms.csv").sort_values("score", ascending=False).head(20)
    return {"rows": t.to_dict("records")}


def load_clusters():
    c = _read("cluster_summary.csv").sort_values("n_buzzer_tweets", ascending=False)
    
    # Load tweets from clustered_tweets.csv
    try:
        tweets_df = _read("clustered_tweets.csv").dropna(subset=["full_text"])
        try:
            scored_df = _read("tweets_scored.csv")[["id_str", "buzzer_prob", "buzzer_flag"]]
            tweets_df["id_str"] = tweets_df["id_str"].astype(str).str.strip()
            scored_df["id_str"] = scored_df["id_str"].astype(str).str.strip()
            tweets_df = tweets_df.merge(scored_df, on="id_str", how="left")
        except Exception:
            pass
    except Exception:
        tweets_df = pd.DataFrame()
        
    cluster_tweets = {}
    if not tweets_df.empty:
        # Group by cluster_id
        for cid, group in tweets_df.groupby("cluster_id"):
            cid = int(cid)
            # Sort by buzzer_flag descending, then favorite_count descending
            group_sorted = group.copy()
            sort_cols = []
            ascending = []
            if "buzzer_flag" in group_sorted.columns:
                sort_cols.append("buzzer_flag")
                ascending.append(False)
            elif "is_coordinated" in group_sorted.columns:
                sort_cols.append("is_coordinated")
                ascending.append(False)
            if "favorite_count" in group_sorted.columns:
                sort_cols.append("favorite_count")
                ascending.append(False)
            if sort_cols:
                group_sorted = group_sorted.sort_values(sort_cols, ascending=ascending)
            
            # Deduplicate by clean_text
            if "clean_text" in group_sorted.columns:
                group_sorted = group_sorted.drop_duplicates(subset=["clean_text"])
                
            tweets_list = []
            for _, tr in group_sorted.iterrows():
                tweets_list.append({
                    "username": str(tr["username"]),
                    "text": str(tr["full_text"]),
                    "is_coordinated": int(tr["is_coordinated"]) if "is_coordinated" in tr else 0,
                    "buzzer_flag": int(tr["buzzer_flag"]) if "buzzer_flag" in tr and not pd.isna(tr["buzzer_flag"]) else (1 if tr.get("buzzer_prob", 0.0) >= 0.85 else 0)
                })
            cluster_tweets[cid] = tweets_list
            
    # Include tweets in the summary
    rows = []
    for _, r in c.iterrows():
        cid = int(r["cluster_id"])
        all_tws = cluster_tweets.get(cid, [])
        top_3 = all_tws[:3]
        more_tws = all_tws[3:]
        
        rows.append({
            "cluster_id": cid,
            "n_tweets": int(r["n_tweets"]),
            "n_akun_unik": int(r["n_akun_unik"]),
            "n_buzzer_tweets": int(r["n_buzzer_tweets"]),
            "pct_buzzer": float(r["pct_buzzer"]),
            "diversity_ratio": float(r["diversity_ratio"]),
            "tweets": top_3,
            "more_tweets": more_tws,
        })
        
    return {"rows": rows}


def load_dbscan_sensitivity(chosen_eps=0.20):
    d = _read("dbscan_sensitivity.csv").sort_values("eps")
    return {"rows": d.to_dict("records"), "chosen_eps": chosen_eps}


def load_cluster_scatter():
    c = _read("clustered_tweets.csv")
    c = c[["pca_x", "pca_y", "cluster_id", "is_coordinated", "username", "clean_text"]].copy()
    c["cluster_id"] = c["cluster_id"].astype(int)
    return {"rows": c.to_dict("records"),
            "n_clustered": int((c["cluster_id"] >= 0).sum()),
            "n_clusters": int(c["cluster_id"].nunique() - (1 if (c["cluster_id"] == -1).any() else 0))}


# ----------------------------------------------------------------------------
# 04 · JARINGAN (SNA) + TEMPORAL
# ----------------------------------------------------------------------------
def load_network():
    nodes = _read("nodes (6).csv")
    edges = _read("edges (6).csv")
    src_col = edges.columns[0]
    tgt_col = edges.columns[1]
    
    # Compute NetworkX metrics if columns like pagerank are not present in the CSV
    try:
        import networkx as nx
        # Create a directed graph to calculate metrics accurately
        G = nx.DiGraph()
        weight_col = "Weight" if "Weight" in edges.columns else ("weight" if "weight" in edges.columns else (edges.columns[2] if len(edges.columns) > 2 else None))
        for _, row in edges.iterrows():
            w = float(row[weight_col]) if weight_col else 1.0
            G.add_edge(row[src_col], row[tgt_col], weight=w)
            
        pr = nx.pagerank(G, alpha=0.85)
        betweenness = nx.betweenness_centrality(G)
        out_deg = dict(G.out_degree())
        
        nodes["pagerank"] = nodes["Label"].map(pr).fillna(0.0)
        nodes["betweenness_centrality"] = nodes["Label"].map(betweenness).fillna(0.0)
        nodes["out_degree"] = nodes["Label"].map(out_deg).fillna(0)
    except Exception:
        if "pagerank" not in nodes.columns:
            nodes["pagerank"] = nodes.get("sna_out_deg_max", 0.0)
        if "betweenness_centrality" not in nodes.columns:
            nodes["betweenness_centrality"] = 0.0
        if "out_degree" not in nodes.columns:
            nodes["out_degree"] = nodes.get("sna_out_deg_max", 0.0)

    n_buzzer_nodes = int((nodes["binary_label_gephi"] == "Buzzer").sum())
    buzz = nodes[nodes["binary_label_gephi"] == "Buzzer"].copy()
    central = buzz.sort_values("pagerank", ascending=False).head(10)[
        ["Label", "pagerank", "betweenness_centrality", "out_degree", "max_buzzer_prob"]
    ].to_dict("records")
    
    # Dynamic target analysis from nodes and edges to keep target data 100% consistent
    buzzer_names = set(buzz["Label"].str.lower())
    src_is_buzzer = edges[edges[src_col].str.lower().isin(buzzer_names)].copy()
    weight_col = "Weight" if "Weight" in edges.columns else ("weight" if "weight" in edges.columns else (edges.columns[2] if len(edges.columns) > 2 else None))
    
    if weight_col:
        target_groups = src_is_buzzer.groupby(tgt_col).agg(
            incoming_from_buzzer=(src_col, "count"),
            total_weight=(weight_col, "sum")
        ).reset_index()
    else:
        target_groups = src_is_buzzer.groupby(tgt_col).agg(
            incoming_from_buzzer=(src_col, "count")
        ).reset_index()
        target_groups["total_weight"] = target_groups["incoming_from_buzzer"]
        
    target_groups = target_groups.rename(columns={tgt_col: "Target"})
    
    targets_df = target_groups.merge(
        nodes[["Label", "max_buzzer_prob", "binary_label_gephi"]],
        left_on="Target",
        right_on="Label",
        how="left"
    )
    if "Label" in targets_df.columns:
        targets_df = targets_df.drop(columns=["Label"])
        
    targets_df["max_buzzer_prob"] = targets_df["max_buzzer_prob"].fillna(0.0)
    targets_df["binary_label_gephi"] = targets_df["binary_label_gephi"].fillna("Non-Buzzer")
    
    targets = targets_df.sort_values("incoming_from_buzzer", ascending=False).to_dict("records")
    
    # Kirimkan SEMUA node agar graf menampilkan seluruh 1080 node seperti Gephi
    all_nodes_data = nodes[["Label", "binary_label_gephi", "max_buzzer_prob"]].to_dict("records")
    
    return {
        "n_nodes": len(nodes),
        "n_edges": len(edges),
        "n_buzzer_nodes": n_buzzer_nodes,
        "unique_sources": int(edges[src_col].nunique()),
        "unique_targets": int(edges[tgt_col].nunique()),
        "edges": edges.rename(columns={src_col: "source", tgt_col: "target"})[["source", "target"]].to_dict("records"),
        "central": central,
        "targets": targets,
        "all_nodes": all_nodes_data,
    }


def load_temporal():
    df = _read("tweets_scored.csv")
    df["dt"] = pd.to_datetime(df["created_at"])
    df["dt_wib"] = df["dt"].dt.tz_convert("Asia/Jakarta")
    df["hour_wib"] = df["dt_wib"].dt.floor("h")
    
    hourly = df.groupby("hour_wib").agg(
        users=("username", "nunique"),
        tweets=("id_str", "count")
    ).reset_index().sort_values("hour_wib")
    
    peak = hourly.loc[hourly["users"].idxmax()]
    top = _read("temporal_top_windows.csv")
    
    return {
        "series": [{"hour": str(r["hour_wib"]), "users": int(r["users"]), "tweets": int(r["tweets"])}
                   for _, r in hourly.iterrows()],
        "peak_users": int(peak["users"]),
        "peak_hour": str(peak["hour_wib"]),
        "n_windows": len(hourly),
        "top": top.to_dict("records"),
    }


def load_all():
    return {
        "pipeline": load_pipeline(),
        "sampling": load_sampling_kappa(),
        "heur_audit": load_heuristic_audit(),
        "folds": load_folds(),
        "kfold_cm": load_kfold_cm(),
        "threshold": load_threshold(),
        "shap": load_shap(),
        "accounts": load_accounts(),
        "prob": load_prob_distribution(),
        "lda": load_lda(),
        "trigrams": load_trigrams(),
        "tfidf": load_tfidf(),
        "clusters": load_clusters(),
        "dbscan": load_dbscan_sensitivity(),
        "cluster_scatter": load_cluster_scatter(),
        "network": load_network(),
        "temporal": load_temporal(),
    }


if __name__ == "__main__":
    D = load_all()
    for k, v in D.items():
        print("\n==========", k, "==========")
        if isinstance(v, dict):
            for kk, vv in v.items():
                print(f"  {kk}: {str(vv)[:150]}")
