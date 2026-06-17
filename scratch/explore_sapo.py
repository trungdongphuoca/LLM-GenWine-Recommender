import pandas as pd
import warnings, sys
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

files = {
    'Don hang': 'Sapo/Danh sach don hang.xlsx',
    'Khach hang': 'Sapo/Danh sach khach hang.xlsx',
    'San pham': 'Sapo/Danh sach san pham.xlsx',
}
for name, path in files.items():
    df = pd.read_excel(path, nrows=5)
    print(f'=== {name} ===')
    print(f'Shape: {df.shape}')
    print('Columns:')
    for i, c in enumerate(df.columns):
        print(f'  [{i}] {repr(c)}')
    print('Sample row 0:')
    for col in df.columns:
        print(f'  {repr(col)}: {repr(df[col].iloc[0])}')
    print()
