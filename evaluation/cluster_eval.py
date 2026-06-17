"""
cluster_eval.py
===============
E1: Cluster-Only Recall
Evaluates how accurately the LLM predicts the correct semantic cluster
(C1-C2-C3) without requiring exact item-level match.
This gives an upper-bound estimate for the Hybrid Pipeline.
"""
import sys, os, json, math
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parents[1]))
import config as cfg
import pandas as pd
import numpy as np

def main():
    print("="*60)
    print("  E1: Cluster-Only Recall Evaluation")
    print("="*60)

    catalog_path = cfg.WINE_SEMANTIC_CSV
    greedy_results_path = cfg.RESULTS / "constrained_eval_results.csv"
    test_path = cfg.TEST_JSONL

    if not os.path.exists(catalog_path):
        print(f"ERROR: {catalog_path} not found.")
        sys.exit(1)
    if not os.path.exists(greedy_results_path):
        print(f"ERROR: {greedy_results_path} not found. Run constrained_eval.py first.")
        sys.exit(1)

    cat = pd.read_csv(catalog_path)
    df_pred = pd.read_csv(greedy_results_path).iloc[:500]

    with open(test_path, encoding='utf-8') as f:
        test = [json.loads(line) for line in f][:500]

    cluster_hits = 0
    exact_hits = 0
    valid_ids = 0
    cluster_sizes = []
    records = []

    for i, item in enumerate(test):
        target_id = item['target_id']
        pred_id = str(df_pred.iloc[i]['pred_id'])

        # Extract clusters
        target_parts = target_id.split('-')
        pred_parts = pred_id.split('-')

        target_cluster = '-'.join(target_parts[:3]) if len(target_parts) >= 3 else ''
        pred_cluster   = '-'.join(pred_parts[:3])   if len(pred_parts)  >= 3 else ''

        is_valid = (pred_id != 'INVALID_ID' and len(pred_parts) >= 3)
        is_cluster_hit = (pred_cluster == target_cluster and pred_cluster != '')
        is_exact_hit   = (pred_id == target_id)

        if is_valid:
            valid_ids += 1
        if is_cluster_hit:
            cluster_hits += 1
        if is_exact_hit:
            exact_hits += 1

        # Count catalog items in predicted cluster
        if pred_cluster:
            sz = len(cat[cat['Semantic_ID'].str.startswith(pred_cluster)])
            cluster_sizes.append(sz)

        records.append({
            'target_id': target_id,
            'pred_id': pred_id,
            'target_cluster': target_cluster,
            'pred_cluster': pred_cluster,
            'valid': is_valid,
            'cluster_hit': is_cluster_hit,
            'exact_hit': is_exact_hit
        })

    n = len(test)
    valid_rate    = valid_ids   / n * 100
    cluster_rate  = cluster_hits / n * 100
    exact_rate    = exact_hits  / n * 100
    avg_clust_sz  = np.mean(cluster_sizes) if cluster_sizes else 0

    print(f"\n=== CLUSTER EVALUATION RESULTS (N={n}) ===")
    print(f"Valid ID Rate    : {valid_rate:.2f}%")
    print(f"Cluster Match@1  : {cluster_rate:.2f}%  (predicted C1-C2-C3 == target C1-C2-C3)")
    print(f"Exact Match@1    : {exact_rate:.4f}%  (predicted full ID == target)")
    print(f"Avg cluster size : {avg_clust_sz:.1f} items per predicted cluster")
    print(f"Theoretical max Recall@10 if cluster correct: {min(10/avg_clust_sz*100,100):.2f}%")
    print("==========================================\n")

    df_out = pd.DataFrame(records)
    out_path = cfg.RESULTS / "cluster_eval_500.csv"
    df_out.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")

    summary = {
        "Method": "TIGER (Cluster-Only)",
        "Valid_ID_Rate": valid_rate,
        "Cluster_Match@1": cluster_rate,
        "Exact_Match@1": exact_rate,
        "Avg_Cluster_Size": avg_clust_sz,
        "N": n
    }
    pd.DataFrame([summary]).to_csv(cfg.RESULTS / "cluster_eval_summary.csv", index=False)
    return summary

if __name__ == "__main__":
    main()
