import sqlite3
import pandas as pd

#データベース接続関数
conn = sqlite3.connect('famafinancial.db')

# 抽出したいレコードのIDリスト
record_ids = [1, 2, 3, 4, 5, 6, 7]  # 例: IDが1~7のレコードを抽出

# 1. 複数のIDに対応するレコードを抽出し、Pandas DataFrameに読み込む
query = "SELECT * FROM finance WHERE id IN ({})".format(','.join(['?'] * len(record_ids)))
df = pd.read_sql_query(query, conn, params=record_ids)

# 2. カラムが一致する別のテーブルにデータを挿入する
if not df.empty:
    # カラムが一致するか確認（例: source_tableとtarget_tableのカラムが同じ場合）
    target_table = 'target_table'
    
    # DataFrameをSQLiteのテーブルに挿入
    df.to_sql(target_table, conn, if_exists='append', index=False)
    print(f"データを {target_table} に挿入しました。")
else:
    print("指定したIDのレコードが見つかりませんでした。")

# 接続を閉じる
conn.close()