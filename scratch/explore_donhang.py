import pandas as pd
import warnings, sys
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

# Don hang
df_don = pd.read_excel('Sapo/Danh sach don hang.xlsx')
print('=== DON HANG ===')
print(f'Shape: {df_don.shape}')
print('Columns:', list(df_don.columns))
print()
print('Sample row 0:')
for col in df_don.columns:
    print(f'  {repr(col)}: {repr(df_don[col].iloc[0])}')
print()
print('Unique orders:', df_don.shape[0])
print('Null counts:')
print(df_don.isnull().sum().to_string())
