import streamlit as st
import pandas as pd
from datetime import datetime

# --- 設定 ---
st.set_page_config(page_title="Coffee & Sweets Explorer", layout="wide")

# スイーツデータベースを拡充
COFFEE_DB = {
    "ブラック：浅煎り": {
        "reason": "フルーティーな酸味を引き立てる、フルーツ系や軽やかな甘みが合います。",
        "suggestions": {
            "さっぱり": ["レモンケーキ", "ドライフルーツ", "フルーツゼリー", "マカロン"],
            "しっかり": ["フルーツタルト", "アップルパイ", "ストロベリーショートケーキ", "レアチーズケーキ"]
        }
    },
    "ブラック：中煎り": {
        "reason": "酸味と苦味のバランスが良いので、バターやナッツを使った焼き菓子全般と相性抜群です。",
        "suggestions": {
            "さっぱり": ["フィナンシェ", "マドレーヌ", "カステラ", "ナッツクッキー"],
            "しっかり": ["パウンドケーキ", "パンケーキ", "バウムクーヘン", "キャラメルタルト"]
        }
    },
    "ブラック：深煎り": {
        "reason": "強い苦味に負けない、濃厚なチョコやクリーム、またはあんこがベストマッチです。",
        "suggestions": {
            "さっぱり": ["ビターチョコ", "羊羹", "かりんとう", "コーヒーゼリー"],
            "しっかり": ["ガトーショコラ", "ベイクドチーズケーキ", "ティラミス", "どら焼き", "ブラウニー"]
        }
    },
    "カフェラテ / カプチーノ": {
        "reason": "ミルクのまろやかさには、小麦の味がしっかりするお菓子や、少し油分のあるものが合います。",
        "suggestions": {
            "さっぱり": ["ビスコッティ", "バタークッキー", "プレッツェル"],
            "しっかり": ["シュガードーナツ", "クロワッサン", "スコーン", "ホットサンド"]
        }
    },
    "カフェモカ / フレーバーラテ": {
        "reason": "コーヒー自体に甘みや香りがあるので、シンプルなものや塩気のあるものが意外と合います。",
        "suggestions": {
            "さっぱり": ["バニラアイス", "塩ナッツ", "ポテトチップス（塩）"],
            "しっかり": ["ワッフル", "生クリームたっぷりのクレープ", "チョコチップクッキー"]
        }
    },
    "エスプレッソ": {
        "reason": "少量で濃厚な味わいには、一口で満足感のある甘いものや、本場の定番がおすすめです。",
        "suggestions": {
            "さっぱり": ["アマレッティ", "小さなダークチョコ"],
            "しっかり": ["ミニタルト", "フォンダンショコラ", "カスタードプリン"]
        }
    }
}

# セッション状態の初期化
if 'history' not in st.session_state:
    st.session_state.history = []

# --- サイドバー：入力 ---
st.sidebar.header("☕ コーヒーの選択")
selected_coffee = st.sidebar.selectbox("何を飲んでいますか？", list(COFFEE_DB.keys()))

st.sidebar.header("😋 今日の気分は？")
mood = st.sidebar.radio("食べたいボリューム感", ["さっぱり・軽め", "しっかり・濃厚"])
mood_key = "さっぱり" if mood == "さっぱり・軽め" else "しっかり"

st.sidebar.header("🍰 スイーツを記録")
suggestions = COFFEE_DB[selected_coffee]["suggestions"][mood_key]
chosen_sweet = st.sidebar.selectbox("おすすめから選ぶ", ["選択してください"] + suggestions)
custom_sweet = st.sidebar.text_input("リストにない場合はこちらに入力")

# 最終的なスイーツ名の決定
final_sweet = custom_sweet if custom_sweet else (chosen_sweet if chosen_sweet != "選択してください" else "")

# 感想と評価
comment = st.sidebar.text_area("感想・メモ")
rating = st.sidebar.slider("今回の相性（星評価）", 1, 5, 3)

if st.sidebar.button("このペアリングを記録！"):
    if final_sweet == "":
        st.sidebar.error("スイーツ名を入力するか選択してください")
    else:
        new_record = {
            "日付": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "コーヒー": selected_coffee,
            "スイーツ": final_sweet,
            "ボリューム": mood,
            "評価": "⭐" * rating,
            "感想": comment
        }
        st.session_state.history.insert(0, new_record)
        st.sidebar.success("ログに保存しました！")

# --- メイン画面 ---
st.title("☕ Coffee & Sweets Pairing Master")

# 提案セクション
st.subheader(f"💡 {selected_coffee} のペアリングのコツ")
st.info(COFFEE_DB[selected_coffee]["reason"])

st.markdown(f"#### 【{mood}】な気分にぴったりの候補")
cols = st.columns(len(suggestions))
for i, s in enumerate(suggestions):
    cols[i].success(f"**{s}**")

st.divider()

# 履歴表示セクション
st.subheader("📚 あなたのペアリング・ログ")

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    # テーブル表示
    st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    # 詳細カード表示
    for item in st.session_state.history:
        with st.expander(f"{item['日付']} | {item['コーヒー']} × {item['スイーツ']} ({item['評価']})"):
            st.write(f"**気分:** {item['ボリューム']}")
            st.write(f"**感想:** {item['感想'] if item['感想'] else '（未入力）'}")
else:
    st.info("まだ記録がありません。コーヒーとスイーツを楽しんだら記録してみましょう！")
