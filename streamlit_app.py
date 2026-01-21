import streamlit as st
import pandas as pd
from datetime import datetime

# --- 設定とデータ ---
st.set_page_config(page_title="Coffee & Sweets Pairer", layout="wide")

# コーヒーの焙煎度に応じたおすすめスイーツのロジック
PAIRING_DB = {
    "浅煎り (Light Roast)": ["フルーツタルト", "レモンケーキ", "マカロン", "ベリー系のムース"],
    "中煎り (Medium Roast)": ["カステラ", "アップルパイ", "パウンドケーキ", "ナッツクッキー"],
    "深煎り (Dark Roast)": ["ガトーショコラ", "チーズケーキ", "ティラミス", "和菓子（あんこ系）"],
    "エスプレッソ / ラテ": ["クロワッサン", "ビスコッティ", "ドーナツ", "バニラアイス"]
}

# セッション状態（簡易的な保存先）の初期化
if 'history' not in st.session_state:
    st.session_state.history = []

# --- サイドバー：入力フォーム ---
st.sidebar.header("☕ 今日のコーヒー")
roast = st.sidebar.selectbox("コーヒーの焙煎度は？", list(PAIRING_DB.keys()))

st.sidebar.header("🍰 ペアリング提案")
suggested_sweets = PAIRING_DB[roast]
selected_sweet = st.sidebar.selectbox("おすすめから選ぶ、または入力", suggested_sweets)

st.sidebar.header("📝 感想")
comment = st.sidebar.text_area("味の相性はどうでしたか？", placeholder="例：苦味と甘さが絶妙！")

if st.sidebar.button("この組み合わせを記録する"):
    new_data = {
        "日付": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "コーヒー": roast,
        "スイーツ": selected_sweet,
        "感想": comment
    }
    st.session_state.history.insert(0, new_data) # 新しいものを上に
    st.sidebar.success("記録しました！")

# --- メイン画面 ---
st.title("☕ Coffee & Sweets Pairing Log")
st.write("コーヒーに合わせた最適なスイーツを提案し、あなたのペアリング体験を記録します。")

# 提案セクション
st.subheader(f"✨ {roast} におすすめのスイーツ")
cols = st.columns(len(suggested_sweets))
for i, sweet in enumerate(suggested_sweets):
    with cols[i]:
        st.info(f"**{sweet}**")

st.divider()

# 履歴表示セクション
st.subheader("📚 これまでのペアリング履歴")

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    
    # 履歴をカード形式で表示
    for index, row in df.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.write(f"**{row['日付']}**")
            with col2:
                st.write(f"**{row['コーヒー']}** × **{row['スイーツ']}**")
                if row['感想']:
                    st.caption(f"感想: {row['感想']}")
            st.divider()
            
    # CSVダウンロード機能
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="履歴をCSVで保存",
        data=csv,
        file_name='coffee_pairing_history.csv',
        mime='text/csv',
    )
else:
    st.info("まだ記録がありません。サイドバーから最初のペアリングを登録してみましょう！")
