"""
Generate error analysis data for demo API.
Run from project root with .venv python.
"""
import json, re
import pandas as pd

tiger_df = pd.read_csv('results/constrained_eval_beam10_500.csv')

instructions = []
with open('data/processed/wine_test_130k.jsonl', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= 500: break
        d = json.loads(line)
        instructions.append(d['instruction'])

tiger_df['instruction'] = instructions

def parse_instruction(txt):
    v = re.search(r'Recommend a (.+?) from', txt)
    c = re.search(r'from (.+?) that', txt)
    p = re.search(r'around \$([0-9]+(?:\.[0-9]+)?)', txt)
    try:
        price = float(p.group(1)) if p else 0.0
    except Exception:
        price = 0.0
    return (
        v.group(1) if v else '',
        c.group(1) if c else '',
        price
    )

tiger_df['variety'], tiger_df['country'], tiger_df['price'] = zip(*tiger_df['instruction'].map(parse_instruction))
tiger_df['pred_top1'] = tiger_df['pred_top10'].apply(lambda x: x.split('|')[0] if pd.notna(x) and '|' in str(x) else str(x))
tiger_df['target_cluster'] = tiger_df['target_id'].apply(lambda x: '-'.join(str(x).split('-')[:3]))
tiger_df['pred_cluster']   = tiger_df['pred_top1'].apply(lambda x: '-'.join(str(x).split('-')[:3]))
tiger_df['cluster_ok'] = tiger_df['target_cluster'] == tiger_df['pred_cluster']

# Price bucket
bins = [0, 15, 30, 50, 100, 1000]
labels = ['<$15', '$15-30', '$30-50', '$50-100', '>$100']
tiger_df['price_bucket'] = pd.cut(tiger_df['price'], bins=bins, labels=labels)

# Failure types
def classify_failure(row):
    if row['Recall@10'] == 1:
        return 'success'
    top1_valid = str(row['pred_top1']).count('-') >= 3
    if not top1_valid:
        return 'invalid_id'
    if row['ClusterMatch@1'] == 0:
        if row['price'] > 100:
            return 'high_price_ambiguity'
        elif row['country'] in ['Italy', 'France', 'Spain']:
            return 'old_world_ambiguity'
        else:
            return 'wrong_cluster'
    return 'cluster_ok_item_miss'

tiger_df['failure_type'] = tiger_df.apply(classify_failure, axis=1)

stats = {
    'total': len(tiger_df),
    'recall1': round(tiger_df['Recall@1'].mean()*100, 2),
    'recall10': round(tiger_df['Recall@10'].mean()*100, 2),
    'cluster_match1': round(tiger_df['ClusterMatch@1'].mean()*100, 2),
    'cluster_match10': round(tiger_df['ClusterMatch@10'].mean()*100, 2),
    'failure_breakdown': tiger_df['failure_type'].value_counts().to_dict(),
    'fail_by_price': tiger_df[tiger_df['Recall@10']==0]['price_bucket'].value_counts().to_dict(),
    'fail_by_country': tiger_df[tiger_df['Recall@10']==0]['country'].value_counts().head(8).to_dict(),
}

# Sample failure cases
samples = []
for ftype in ['wrong_cluster', 'old_world_ambiguity', 'high_price_ambiguity', 'cluster_ok_item_miss']:
    rows = tiger_df[tiger_df['failure_type']==ftype].head(2)
    for _, row in rows.iterrows():
        samples.append({
            'type': ftype,
            'instruction': row['instruction'],
            'target_id': row['target_id'],
            'pred_top1': row['pred_top1'],
            'target_cluster': row['target_cluster'],
            'pred_cluster': row['pred_cluster'],
            'variety': row['variety'],
            'country': row['country'],
            'price': row['price'],
        })

# Sample success cases
for _, row in tiger_df[tiger_df['Recall@1']==1].head(3).iterrows():
    samples.append({
        'type': 'success',
        'instruction': row['instruction'],
        'target_id': row['target_id'],
        'pred_top1': row['pred_top1'],
        'target_cluster': row['target_cluster'],
        'pred_cluster': row['pred_cluster'],
        'variety': row['variety'],
        'country': row['country'],
        'price': row['price'],
    })

output = {'stats': stats, 'samples': samples}
with open('demo/error_analysis_data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("Saved demo/error_analysis_data.json")
print(json.dumps(stats, indent=2, ensure_ascii=False))
