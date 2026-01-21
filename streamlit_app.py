import streamlit as st
import pandas as pd
from datetime import datetime

# --- 設定 ---
st.set_page_config(page_title="Coffee & Sweets Pairer", layout="wide")

# カテゴリ分けしたペアリングデータ
COFFEE_TYPES = {
    "ブラック：浅煎り": {
        "sweets": ["フルーツタルト", "レモンケーキ", "マカロン"],
        "reason": "華やかな酸味には、同じく酸味のあるフルーツ系が調和します。"
    },
    "ブラック：中煎り": {
        "sweets": ["カステラ", "アップルパイ", "パウンドケーキ"],
        "reason": "バランスの良い味わいには、優しい甘みの焼き菓子が最適です。"
    },
    "ブラック：深煎り": {
        "sweets": ["ガトーショコラ", "濃厚チーズケーキ", "どら焼き"],
        "reason": "強い苦味とコクには、油脂分や甘みの強い濃厚なスイーツが負けません。"
    },
    "カフェラテ / カプチーノ": {
        "sweets": ["クロワッサン", "ドーナツ", "スコーン"],
        "reason": "ミルクのまろやかさには、バターの香る生地や揚げたお菓子が合います。"
    },
    "カフェモカ": {
        "sweets": ["バニラアイス", "塩ナッツ", "ベリー系ゼリー"],
        "reason": "チョコの風味があるため、あえてシンプルなアイスや塩気で変化を。"
    },
    "エスプレッソ": {
        "sweets": ["ビスコッティ", "小さなチョコ", "ティラミス"],
        "reason": "凝縮された味わいには、少しずつかじれる硬いお菓子や本場の味が◎。"
    }
}

# セッション状態の初期化
if 'history' not in st.session_state:
    st.session_state.history = []

# --- サイドバー：入力 ---
st.sidebar.header("☕ コーヒーを選ぶ")
selected_type = st.sidebar.selectbox("今日の飲み方は？", list(COFFEE_TYPES.keys()))

st.sidebar.header("🍰 スイーツを記録")
suggestions = COFFEE_TYPES[selected_type]["sweets"]
chosen_sweet = st.sidebar.selectbox("おすすめの組み合わせ", suggestions)
custom_sweet = st.sidebar.text_input("その他に食べたものがあれば入力")

# 最終的に保存するスイーツ名
final_sweet = custom_sweet if custom_sweet else chosen_sweet

comment = st.sidebar.text_area("感想・メモ", placeholder="例：ラテのミルク感とドーナツの相性が最高！")

if st.sidebar.button("このペアを保存する"):
    new_record = {
        "日付": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "コーヒー": selected_type,
        "スイーツ": final_sweet,
        "感想": comment
    }
    st.session_state.history.insert(0, new_record)
    st.sidebar.success("記録しました！")

# --- メイン画面 ---
st.title("☕ Coffee & Sweets Pairing App")

# 提案セクション
st.subheader(f"✨ {selected_type} に合う理由")
st.info(COFFEE_TYPES[selected_type]["reason"])

st.markdown("#### おすすめのスイーツ例")
cols = st.columns(len(suggestions))
for i, s in enumerate(suggestions):
    cols[i].metric(label=f"Suggestion {i+1}", value=s)

st.divider()

# 履歴表示セクション
st.subheader("📚 あなたのペアリング・ログ")

if st.session_state.history:
    # 履歴をテーブル形式でも見やすく表示
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    # 個別のカード表示
    for item in st.session_state.history:
        with st.expander(f"{item['日付']} - {item['コーヒー']} × {item['スイーツ']}"):
            st.write(f"**感想:** {item['感想'] if item['感想'] else '（未入力）'}")
else:
    st.info("まだ記録がありません。左のメニューから記録を追加してください。")
