import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- Supabase接続設定 ---
# StreamlitのSecretsから情報を取得
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception:
    st.error("SupabaseのURLとKeyが設定されていません。Secretsを確認してください。")
    st.stop()

# --- 設定 ---
st.set_page_config(page_title="Coffee & Sweets Explorer (Supabase版)", layout="wide")

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

final_sweet = custom_sweet if custom_sweet else (chosen_sweet if chosen_sweet != "選択してください" else "")
comment = st.sidebar.text_area("感想・メモ")
rating = st.sidebar.slider("今回の相性（星評価）", 1, 5, 3)

# データの保存（Insert）
if st.sidebar.button("このペアリングを記録！"):
    if final_sweet == "":
        st.sidebar.error("スイーツ名を入力するか選択してください")
    else:
        new_record = {
            "coffee_type": selected_coffee,
            "sweet_name": final_sweet,
            "volume": mood,
            "rating": rating,
            "comment": comment
        }
        # Supabaseへ送信
        try:
            supabase.table("coffee_logs").insert(new_record).execute()
            st.sidebar.success("Supabaseに保存しました！")
            st.rerun() # 画面を更新して最新データを表示
        except Exception as e:
            st.sidebar.error(f"保存に失敗しました: {e}")

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

# 履歴表示セクション（Select）
st.subheader("📚 あなたのペアリング・ログ (Supabaseから読み込み)")

try:
    # Supabaseから全データを取得（新しい順）
    response = supabase.table("coffee_logs").select("*").order("created_at", desc=True).execute()
    history_data = response.data

    if history_data:
        # 表示用にデータを整形
        display_df = pd.DataFrame(history_data)
        # カラム名を日本語に変換して見やすくする
        display_df = display_df.rename(columns={
            "created_at": "日付",
            "coffee_type": "コーヒー",
            "sweet_name": "スイーツ",
            "volume": "ボリューム",
            "rating": "評価",
            "comment": "感想"
        })
        # 評価の数字を星マークに変換
        display_df["評価"] = display_df["評価"].apply(lambda x: "⭐" * x)
        
        # IDなどの不要な列を除外して表示
        st.dataframe(display_df[["日付", "コーヒー", "スイーツ", "ボリューム", "評価", "感想"]], use_container_width=True)
        
        st.markdown("---")
        # 詳細表示
        for item in history_data:
            date_str = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M")
            with st.expander(f"{date_str} | {item['coffee_type']} × {item['sweet_name']} ({'⭐' * item['rating']})"):
                st.write(f"**気分:** {item['volume']}")
                st.write(f"**感想:** {item['comment'] if item['comment'] else '（未入力）'}")
    else:
        st.info("まだ記録がありません。")
except Exception as e:
    st.error(f"データの読み込みに失敗しました: {e}")
