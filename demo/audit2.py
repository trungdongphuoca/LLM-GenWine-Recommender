import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

# The key data point: fair_comparison
df = pd.read_csv('results/fair_comparison/all_models_comparison.csv', encoding='latin-1')
print('=== FAIR COMPARISON (chinh thuc) ===')
print(df.to_string())
print()

# llm_eval_results
llm = pd.read_csv('results/llm_eval_results.csv')
print('=== LLM EVAL DETAILS ===')
print('Columns:', llm.columns.tolist())
print('N rows:', len(llm))
if 'pred_id' in llm.columns:
    print('Sample pred_id:', llm['pred_id'].head(3).tolist())
if 'target_id' in llm.columns:
    print('Sample target_id:', llm['target_id'].head(3).tolist())
print()
# Check metrics columns
metric_cols = [c for c in llm.columns if 'recall' in c.lower() or 'ndcg' in c.lower() or 'mrr' in c.lower()]
if metric_cols:
    print('Metrics:')
    for c in metric_cols:
        print(f'  {c}: {llm[c].mean()*100:.3f}%')
print()

hy = pd.read_csv('results/hybrid_summary.csv')
print('=== HYBRID (TIGER + Price Rerank) ===')
print(hy.to_string())
print()

# ablation_results
ab = pd.read_csv('results/ablation_results.csv')
print('=== ABLATION RESULTS ===')
print(ab.to_string())
