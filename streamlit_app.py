import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
import uuid
import random

# --- Supabase接続設定 ---
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception:
    st.error("SupabaseのURLとKeyが設定されていません。Secretsを確認してください。")
    st.stop()

# --- 設定 ---
st.set_page_config(page_title="Coffee & Sweets Master Pro", layout="wide")

COFFEE_DB = {
    "ブラック：浅煎り": {"reason": "フルーティーな酸味を引き立てる、フルーツ系や軽やかな甘みが合います。", "suggestions": {"さっぱり": ["レモンケーキ", "ドライフルーツ", "フルーツゼリー", "マカロン"], "しっかり": ["フルーツタルト", "アップルパイ", "ストロベリーショートケーキ", "レアチーズケーキ"]}},
    "ブラック：中煎り": {"reason": "酸味と苦味のバランスが良いので、バターやナッツを使った焼き菓子全般と相性抜群です。", "suggestions": {"さっぱり": ["フィナンシェ", "マドレーヌ", "カステラ", "ナッツクッキー"], "しっかり": ["パウンドケーキ", "パンケーキ", "バウムクーヘン", "キャラメルタルト"]}},
    "ブラック：深煎り": {"reason": "強い苦味に負けない、濃厚なチョコやクリーム、またはあんこがベストマッチです。", "suggestions": {"さっぱり": ["ビターチョコ", "羊羹", "かりんとう", "コーヒーゼリー"], "しっかり": ["ガトーショコラ", "ベイクドチーズケーキ", "ティラミス", "どら焼き", "ブラウニー"]}},
    "カフェラテ / カプチーノ": {"reason": "ミルクのまろやかさには、小麦の味がしっかりするお菓子や、少し油分のあるものが合います。", "suggestions": {"さっぱり": ["ビスコッティ", "バタークッキー", "プレッツェル"], "しっかり": ["シュガードーナツ", "クロワッサン", "スコーン", "ホットサンド"]}},
    "カフェモカ / フレーバーラテ": {"reason": "コーヒー自体に甘みや香りがあるので、シンプルなものや塩気のあるものが意外と合います。", "suggestions": {"さっぱり": ["バニラアイス", "塩ナッツ", "ポテトチップス（塩）"], "しっかり": ["ワッフル", "生クリームたっぷりのクレープ", "チョコチップクッキー"]}},
    "エスプレッソ": {"reason": "少量で濃厚な味わいには、一口で満足感のある甘いものや、本場の定番がおすすめです。", "suggestions": {"さっぱり": ["アマレッティ", "小さなダークチョコ"], "しっかり": ["ミニタルト", "フォンダンショコラ", "カスタードプリン"]}}
}

# --- データの取得 ---
try:
    response = supabase.table("coffee_logs").select("*").order("created_at", desc=True).execute()
    history_data = response.data
    df_history = pd.DataFrame(history_data) if history_data else pd.DataFrame()
except Exception as e:
    st.error(f"データ取得エラー: {e}")
    df_history = pd.DataFrame()

# --- サイドバー：入力 ---
st.sidebar.header("☕ 今日のペアリングを記録")
selected_coffee = st.sidebar.selectbox("何を飲んでいますか？", list(COFFEE_DB.keys()))
mood = st.sidebar.radio("食べたいボリューム感", ["さっぱり・軽め", "しっかり・濃厚"])
mood_key = "さっぱり" if mood == "さっぱり・軽め" else "しっかり"

suggestions = COFFEE_DB[selected_coffee]["suggestions"][mood_key]
chosen_sweet = st.sidebar.selectbox("おすすめから選ぶ", ["選択してください"] + suggestions)
custom_sweet = st.sidebar.text_input("リストにない場合はこちらに入力")
final_sweet = custom_sweet if custom_sweet else (chosen_sweet if chosen_sweet != "選択してください" else "")

uploaded_file = st.sidebar.file_uploader("📷 スイーツの画像", type=["jpg", "png", "jpeg"])
comment = st.sidebar.text_area("感想・メモ")
rating = st.sidebar.slider("今回の相性評価", 1, 5, 3)

if st.sidebar.button("🚀 ペアリングを記録！"):
    if not final_sweet:
        st.sidebar.error("スイーツ名を入力してください")
    else:
        try:
            image_url = None
            if uploaded_file:
                file_name = f"{uuid.uuid4()}.{uploaded_file.name.split('.')[-1]}"
                supabase.storage.from_("sweets_images").upload(file_name, uploaded_file.getvalue())
                image_url = supabase.storage.from_("sweets_images").get_public_url(file_name)

            new_record = {
                "coffee_type": selected_coffee, "sweet_name": final_sweet,
                "volume": mood, "rating": rating, "comment": comment, "image_url": image_url
            }
            supabase.table("coffee_logs").insert(new_record).execute()
            st.sidebar.success("記録完了！")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"保存エラー: {e}")

# --- メイン画面 ---
st.title("☕ Coffee & Sweets Pairing Master Pro")

# --- タブ機能で画面を整理 ---
tab1, tab2, tab3 = st.tabs(["💡 ペアリング提案", "📊 傾向分析", "📚 全ログ表示"])

with tab1:
    # 3. 「今日のおすすめ」提案機能
    st.subheader("🎲 今日は何を合わせる？")
    if not df_history.empty:
        # 星4つ以上の高評価データからランダムに選ぶ
        high_rated = df_history[df_history['rating'] >= 4]
        if st.button("🌟 過去の高評価ペアから提案を受ける"):
            if not high_rated.empty:
                pick = high_rated.sample(n=1).iloc[0]
                st.balloons()
                c1, c2 = st.columns([1, 2])
                with c1:
                    if pick['image_url']:
                        st.image(pick['image_url'], use_container_width=True)
                with c2:
                    st.success(f"おすすめは **{pick['coffee_type']}** × **{pick['sweet_name']}** です！")
                    st.write(f"過去の評価: {'⭐' * pick['rating']}")
                    st.write(f"過去のメモ: {pick['comment']}")
            else:
                st.warning("星4つ以上の記録がまだありません。まずは記録を増やしましょう！")
    else:
        st.info("データが溜まると、ここでおすすめの提案ができるようになります。")

    st.divider()
    st.info(f"**現在の選択:** {selected_coffee}\n\n{COFFEE_DB[selected_coffee]['reason']}")
    cols = st.columns(len(suggestions))
    for i, s in enumerate(suggestions):
        cols[i].success(f"**{s}**")

with tab2:
    # 2. 「人気の組み合わせ」ランキング表示
    st.subheader("📈 あなたのペアリング傾向")
    if not df_history.empty:
        col_stat1, col_stat2 = st.columns(2)
        
        with col_stat1:
            st.write("🏆 **よく飲むコーヒー TOP3**")
            top_coffee = df_history['coffee_type'].value_counts().head(3)
            st.bar_chart(top_coffee)
        
        with col_stat2:
            st.write("⭐ **平均評価が高いコーヒー**")
            avg_rating = df_history.groupby('coffee_type')['rating'].mean().sort_values(ascending=False)
            st.dataframe(avg_rating.rename("平均評価"))
        
        st.write("🥐 **よく食べているスイーツ**")
        st.write(", ".join(df_history['sweet_name'].value_counts().head(5).index.tolist()))
    else:
        st.info("分析するデータがまだありません。")

with tab3:
    # 履歴表示セクション
    st.subheader("📋 履歴一覧")
    if not df_history.empty:
        for index, item in df_history.iterrows():
            date_str = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M")
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                with st.expander(f"{date_str} | {item['coffee_type']} × {item['sweet_name']} ({'⭐' * item['rating']})"):
                    if item['image_url']:
                        st.image(item['image_url'], width=300)
                    st.write(f"**ボリューム:** {item['volume']} | **感想:** {item['comment'] if item['comment'] else 'なし'}")
            with col2:
                if st.button("🗑️", key=f"del_{item['id']}"):
                    supabase.table("coffee_logs").delete().eq("id", item['id']).execute()
                    st.rerun()
    else:
        st.info("ログがありません。")
