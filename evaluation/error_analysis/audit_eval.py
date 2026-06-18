import pandas as pd, os

# constrained_eval summary
df = pd.read_csv('results/constrained_eval_beam10_500.csv')
print("=== TIGER Greedy (constrained_eval_beam10_500) ===")
print(f"N = {len(df)}")
print(f"Recall@1        : {df['Recall@1'].mean()*100:.2f}%")
print(f"Recall@10       : {df['Recall@10'].mean()*100:.2f}%")
print(f"ClusterMatch@1  : {df['ClusterMatch@1'].mean()*100:.2f}%")
print(f"ClusterMatch@10 : {df['ClusterMatch@10'].mean()*100:.2f}%")
print(f"MRR             : {df['MRR'].mean()*100:.2f}%")
print()

print("=== evaluation_results_summary ===")
ev = pd.read_csv('results/evaluation_results_summary.csv')
print(ev.to_string())
print()

print("=== llm_eval_results ===")
llm = pd.read_csv('results/llm_eval_results.csv')
print(llm.to_string())
print()

print("=== fair_comparison files ===")
for f in os.listdir('results/fair_comparison'):
    path = f'results/fair_comparison/{f}'
    print(f"  {f}: {os.path.getsize(path)} bytes")
    try:
        tmp = pd.read_csv(path)
        print(tmp.to_string())
    except Exception as e:
        print("  (error:", e, ")")
print()

print("=== scientific_metrics files ===")
for f in os.listdir('results/scientific_metrics'):
    path = f'results/scientific_metrics/{f}'
    print(f"  {f}: {os.path.getsize(path)} bytes")
    try:
        tmp = pd.read_csv(path)
        print(tmp.to_string())
    except Exception as e:
        print("  (error:", e, ")")
