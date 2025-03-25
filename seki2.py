import streamlit as st
from PIL import Image
import pandas as pd
import sqlite3
import altair as alt
import datetime
from streamlit.column_config import NumberColumn

#スタイルの読み込み カスタムCSS
#ロゴをよみこみ
st.markdown(
    """
    <style>
    .header {
        font-size: 30px;
        color: #3EBEA1;
        text-align: center;
        padding-top: 50px;
        padding-bottom: 50px;
    }
    </style>
    <img src="logo.jpg" height="50" width="120" style="vertical-align:left"></p>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .h1 {
        font-size: 30px;
        color: white;
        text-align: left;
        background-color: #3EBEA1;
    }
    .image {
        width: 200px;
        margin-top: 50px;
        margin-bottom: 50px; 
        }
    </style>
    """,
    unsafe_allow_html=True
)

# データベースに接続
conn = sqlite3.connect('famafinancial.db')
c = conn.cursor()

#アプリ名称を記載
st.markdown('<div class="header">金融資産管理アプリ</div>', unsafe_allow_html=True)

#h1を追記
st.markdown('<div class="h1">　収支入力と現在保有の金融資産</div>', unsafe_allow_html=True)

# Streamlitでカレンダーを表示
min_date = datetime.date(1900, 1, 1)
max_date = datetime.date(2100, 12, 31)
d = st.date_input('今日の日付を入力してください。', datetime.date(2025, 3, 22), min_value=min_date, max_value=max_date)

# データベースから前回までの残高を取得する
c.execute("SELECT item, amount FROM finance WHERE item IN ('預金', '財形貯蓄', '社内積立')")

# 結果を取得
results = c.fetchall()

# DBの結果を辞書に変換
balance_dict = {item: amount for item, amount in results}

# # DBに値がなかった場合のデフォルト値を設定（必要に応じて変更）
# default_balances = {"預金": 1000000, "財形貯蓄": 200000, "社内積立": 100000}
# # 取得した値があればそれを、なければデフォルト値を使用
# balance_dict = {key: balance_dict.get(key, default_balances[key]) for key in default_balances.keys()}

# データフレームを作成
data = {
    "資産": ["預金" , "財形貯蓄", "社内積立"],
    "前回までの残高": [
        balance_dict["預金"],
        balance_dict["財形貯蓄"],
        balance_dict["社内積立"]
    ],
    "支出入": [0, 0, 0],  # 初期値は0
    "現在の残高":  [
        balance_dict["預金"],
        balance_dict["財形貯蓄"],
        balance_dict["社内積立"]
    ]
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
        color="資産:#F9DA25"
    )
    .properties(width=50, height=400)
)

# Streamlitでグラフを表示
st.altair_chart(chart, use_container_width=True)

# データベースから過去ログ一覧を取得する関数
def fetch_datas():
    result = c.execute("SELECT * FROM finance").fetchall()
    return result

# 過去ログ一覧を表示
st.write("過去ログ一覧:")
users = fetch_datas()
for row in users:
    st.write(f"ID: {row[0]}, 資産/負債: {row[1]}, 金額: {row[3]}")

# データベース接続をクローズ
conn.close()