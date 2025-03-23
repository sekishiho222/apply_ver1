import streamlit as st
import pandas as pd
import sqlite3
import altair as alt
import datetime
from streamlit.column_config import NumberColumn

#データベースファイル名
db_name = 'FAMA_financial.db'

#データベース接続関数
con = sqlite3.connect(db_name)

# 2.sqliteを操作するカーソルオブジェクトを作成
cur = con.cursor()

st.title('金融資産管理アプリ')

# Streamlitでカレンダーを表示
min_date = datetime.date(1900, 1, 1)
max_date = datetime.date(2100, 12, 31)
d = st.date_input('今日の日付を入力してください。', datetime.date(2025, 3, 22), min_value=min_date, max_value=max_date)

# 抽出したいレコードのIDリスト
record_ids = [1, 2, 3, 4, 5, 6, 7]  # 抽出したいレコードのID

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


# データフレームを作成
data = {
    "資産": ["預金" , "財形貯蓄", "社内積立"],
    "前回までの残高": [1000000, 200000, 100000],
    "支出入": [0, 0, 0],  # 初期値は0
    "現在の残高": [1000000, 200000, 100000]
}
df = pd.DataFrame(data)

# ユーザーが支出入を入力できるようにする
for i in range(len(df)):
    df.loc[i, "支出入"] = st.number_input(
        f"{df.loc[i, '資産']}の増加額または減少額",
        value=df.loc[i, "支出入"],
        step=1000,
        format="%d"
    )

# 前回までの残高 + 支出入 = 現在の残高
df["現在の残高"] = df["前回までの残高"] + df["支出入"]

# データフレームを表示
st.dataframe(df.style.format({"前回までの残高": "¥{:,.0f}", "支出入": "¥{:,.0f}", "現在の残高": "¥{:,.0f}"}))

# データフレームを積み上げ棒グラフ用に整形
chart_data = pd.melt(df, id_vars=["資産"], value_vars=["現在の残高"], var_name="カテゴリ", value_name="金額")

# Altairで積み上げ棒グラフを作成（軸の目盛りを10万円単位）
chart = (
    alt.Chart(chart_data)
    .mark_bar()
    .encode(
        x=alt.X("カテゴリ:N", title="金融資産"),
        y=alt.Y("金額:Q", title="金額（円）", scale=alt.Scale(domain=[0, max(df['現在の残高'].max() + 100000, 1500000)], nice=True)),
        color="資産:N"
    )
    .properties(width=50, height=400)
)

# Streamlitでグラフを表示
st.altair_chart(chart, use_container_width=True)

# 4.データベースに情報をコミット
con.commit()

# 5.データベースの接続を切断
cur.close()
con.close()