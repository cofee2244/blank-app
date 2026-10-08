import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import os
import uuid
import random

# --- SQLite3 データベース接続・初期化 ---
DB_NAME = "coffee_app.db"
IMAGE_DIR = "uploaded_images"

# 画像保存用ディレクトリ作成
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS coffee_logs (
            id TEXT PRIMARY KEY,
            coffee_type TEXT,
            sweet_name TEXT,
            volume TEXT,
            rating INTEGER,
            comment TEXT,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

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
    conn = get_db_connection()
    df_history = pd.read_sql_query("SELECT * FROM coffee_logs ORDER BY created_at DESC", conn)
    conn.close()
except Exception as e:
    st.error(f"データ取得エラー: {e}")
    df_history = pd.DataFrame()

# --- サイドバー：入力 ---
st.sidebar.header("☕ 今日のペアリングを記録")

# 【追加】飲み物の選択肢に「その他」を追加
coffee_options = list(COFFEE_DB.keys()) + ["その他（自由入力）"]
selected_coffee_raw = st.sidebar.selectbox("何を飲んでいますか？", coffee_options)

# 【追加】「その他」が選ばれた時だけテキスト入力を表示
if selected_coffee_raw == "その他（自由入力）":
    custom_coffee = st.sidebar.text_input("飲み物名を入力してください")
    selected_coffee = custom_coffee
else:
    selected_coffee = selected_coffee_raw

mood = st.sidebar.radio("食べたいボリューム感", ["さっぱり・軽め", "しっかり・濃厚"])
mood_key = "さっぱり" if mood == "さっぱり・軽め" else "しっかり"

# 【修正】DBに存在するコーヒーの場合のみ提案リストを作成
if selected_coffee in COFFEE_DB:
    suggestions = COFFEE_DB[selected_coffee]["suggestions"][mood_key]
else:
    suggestions = [] # 自由入力の場合は空リスト

chosen_sweet = st.sidebar.selectbox("おすすめから選ぶ", ["選択してください"] + suggestions)
custom_sweet = st.sidebar.text_input("リストにない場合はこちらに入力")
final_sweet = custom_sweet if custom_sweet else (chosen_sweet if chosen_sweet != "選択してください" else "")

uploaded_file = st.sidebar.file_uploader("📷 スイーツの画像", type=["jpg", "png", "jpeg"])
comment = st.sidebar.text_area("感想・メモ")
rating = st.sidebar.slider("今回の相性評価", 1, 5, 3)

if st.sidebar.button("🚀 ペアリングを記録！"):
    if not selected_coffee:
        st.sidebar.error("飲み物名を入力してください")
    elif not final_sweet:
        st.sidebar.error("スイーツ名を入力してください")
    else:
        try:
            image_url = None
            if uploaded_file:
                file_ext = uploaded_file.name.split('.')[-1]
                file_name = f"{uuid.uuid4()}.{file_ext}"
                file_path = os.path.join(IMAGE_DIR, file_name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                image_url = file_path

            log_id = str(uuid.uuid4())
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO coffee_logs (id, coffee_type, sweet_name, volume, rating, comment, image_url, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (log_id, selected_coffee, final_sweet, mood, rating, comment, image_url, now_str))
            conn.commit()
            conn.close()

            st.sidebar.success("記録完了！")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"保存エラー: {e}")

# --- メイン画面 ---
st.title("☕ Coffee & Sweets Pairing Master Pro")

tab1, tab2, tab3 = st.tabs(["💡 ペアリング提案", "📊 傾向分析", "📚 全ログ表示"])

with tab1:
    st.subheader("🎲 今日は何を合わせる？")
    if not df_history.empty:
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
                    st.write(f"過去の評価: {'⭐' * int(pick['rating'])}")
                    st.write(f"過去のメモ: {pick['comment']}")
            else:
                st.warning("星4つ以上の記録がまだありません。まずは記録を増やしましょう！")
    else:
        st.info("データが溜まると、ここでおすすめの提案ができるようになります。")

    st.divider()

    # 【修正】自由入力された飲み物でもエラーが出ないように条件分岐
    if selected_coffee in COFFEE_DB:
        st.info(f"**現在の選択:** {selected_coffee}\n\n{COFFEE_DB[selected_coffee]['reason']}")
        if suggestions:
            cols = st.columns(len(suggestions))
            for i, s in enumerate(suggestions):
                cols[i].success(f"**{s}**")
    elif selected_coffee:
        st.info(f"**現在の選択:** {selected_coffee}\n\n自由な組み合わせで楽しみましょう！記録を残せば分析に反映されます。")
    else:
        st.info("左側のサイドバーから飲み物を選んでください。")

with tab2:
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
    st.subheader("📋 履歴一覧")
    if not df_history.empty:
        for index, item in df_history.iterrows():
            try:
                date_str = datetime.strptime(item['created_at'], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")
            except Exception:
                date_str = str(item['created_at'])
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                with st.expander(f"{date_str} | {item['coffee_type']} × {item['sweet_name']} ({'⭐' * int(item['rating'])})"):
                    if item['image_url'] and os.path.exists(item['image_url']):
                        st.image(item['image_url'], width=300)
                    st.write(f"**ボリューム:** {item['volume']} | **感想:** {item['comment'] if item['comment'] else 'なし'}")
            with col2:
                if st.button("🗑️", key=f"del_{item['id']}"):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM coffee_logs WHERE id = ?", (item['id'],))
                    conn.commit()
                    conn.close()
                    
                    # 保存されていた画像ファイルも削除
                    if item['image_url'] and os.path.exists(item['image_url']):
                        try:
                            os.remove(item['image_url'])
                        except Exception:
                            pass
                    st.rerun()
    else:
        st.info("ログがありません。")
