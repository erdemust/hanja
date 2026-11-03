import json
import random
import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="Sino-Korean Word Bridge | TOPIK Prep",
    page_icon="🇰🇷",
    layout="wide",
)

# --- Load Data from data.json ---
@st.cache_data
def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("entries", []), data.get("metadata", {})
    except FileNotFoundError:
        st.error("⚠️ `data.json` not found in the current directory. Please make sure it is placed alongside `app.py`.")
        return [], {}

entries, metadata = load_data()

# --- Sidebar / Navigation ---
st.sidebar.title("🏮 TOPIK Prep")
st.sidebar.markdown("### Sino-Korean Word Bridge")

if metadata:
    st.sidebar.info(
        f"**Dataset Info:**\n"
        f"- Total Entries: {metadata.get('total_entries', len(entries))}\n"
        f"- Level 1: {metadata.get('level_counts', {}).get('1', 'N/A')}\n"
        f"- Level 2: {metadata.get('level_counts', {}).get('2', 'N/A')}"
    )

app_mode = st.sidebar.radio("Navigation", ["Vocabulary List", "Interactive Quiz"])

st.sidebar.markdown("---")
selected_level = st.sidebar.selectbox("Filter Level", ["All Levels", "Level 1", "Level 2"])

# --- Main App Logic ---
if app_mode == "Vocabulary List":
    st.title("Sino-Korean Word Bridge")
    st.markdown(
        "Explore TOPIK I & II Sino-Korean words with their hanja, Korean pronunciation, "
        "and readings you already know (Chinese Pinyin, Japanese On-yomi, and Hán-Việt)."
    )

    if not entries:
        st.warning("No vocabulary data loaded.")
    else:
        # Search bar
        search_query = st.text_input("🔍 Search by word, meaning, or hanja:", "")

        # Filter data
        filtered_data = entries
        if selected_level == "Level 1":
            filtered_data = [item for item in filtered_data if item.get("topik_level") == 1]
        elif selected_level == "Level 2":
            filtered_data = [item for item in filtered_data if item.get("topik_level") == 2]

        if search_query:
            query = search_query.lower()
            filtered_data = [
                item for item in filtered_data 
                if query in item.get("word", "").lower() 
                or query in item.get("meaning_en", "").lower() 
                or query in item.get("hanja", "").lower()
            ]

        st.markdown(f"**Showing {len(filtered_data)} words**")

        # Display as cards/table
        for item in filtered_data:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 1, 4])
                with col1:
                    st.markdown(f"### {item.get('word')}")
                with col2:
                    st.markdown(f"**Hanja:** `{item.get('hanja')}`")
                with col3:
                    st.markdown(f"`Level {item.get('topik_level')}`")
                with col4:
                    st.markdown(f"**Meaning:** {item.get('meaning_en')}")

                # Details expander for readings
                with st.expander("Character Readings (Pinyin / On-yomi / Hán-Việt)"):
                    r_col1, r_col2, r_col3 = st.columns(3)
                    with r_col1:
                        st.markdown(f"**🇨🇳 Pinyin:** {item.get('pinyin')}")
                    with r_col2:
                        st.markdown(f"**🇯🇵 On-yomi:** {item.get('on_yomi')}")
                    with r_col3:
                        st.markdown(f"**🇻🇳 Hán-Việt:** {item.get('han_viet')}")
                st.divider()

elif app_mode == "Interactive Quiz":
    st.title("🎯 20-Word Sino-Korean Quiz")
    st.markdown("Test your knowledge! Match the Hanja and readings to the correct Korean word.")

    if not entries:
        st.warning("No vocabulary data available for the quiz.")
    else:
        # Initialize Quiz State
        if "quiz_questions" not in st.session_state or st.button("🔄 Reset Quiz"):
            pool = entries
            if selected_level == "Level 1":
                pool = [i for i in entries if i.get("topik_level") == 1]
            elif selected_level == "Level 2":
                pool = [i for i in entries if i.get("topik_level") == 2]
            
            sample_size = min(20, len(pool))
            st.session_state.quiz_questions = random.sample(pool, sample_size)
            st.session_state.user_answers = {}
            st.session_state.submitted = False

        questions = st.session_state.quiz_questions

        if not questions:
            st.warning("No words available for the selected level filter.")
        else:
            with st.form("quiz_form"):
                for idx, q in enumerate(questions):
                    st.markdown(f"#### Question {idx + 1}")
                    st.markdown(
                        f"**Hanja:** `{q.get('hanja')}` | "
                        f"**Hán-Việt / Pinyin:** `{q.get('han_viet')} / {q.get('pinyin')}`"
                    )

                    # Generate 4 options (1 correct, 3 random distractors)
                    distractors = [item["word"] for item in entries if item["word"] != q["word"]]
                    options = random.sample(distractors, min(3, len(distractors))) + [q["word"]]
                    random.shuffle(options)

                    # Radio button for answer
                    st.session_state.user_answers[idx] = st.radio(
                        f"Select the correct Korean word for question {idx + 1}:",
                        options,
                        key=f"q_{idx}"
                    )
                    st.divider()

                submit_button = st.form_submit_button(label="Submit Quiz")

                if submit_button:
                    st.session_state.submitted = True

            if st.session_state.get("submitted", False):
                score = 0
                st.subheader("📊 Quiz Results")
                for idx, q in enumerate(questions):
                    user_ans = st.session_state.user_answers.get(idx)
                    correct_ans = q["word"]
                    if user_ans == correct_ans:
                        score += 1
                        st.success(f"Q{idx + 1}: Correct! ({correct_ans} - {q.get('meaning_en')})")
                    else:
                        st.error(f"Q{idx + 1}: Incorrect. Your answer: **{user_ans}** | Correct answer: **{correct_ans}** ({q.get('meaning_en')})")
                
                st.markdown(f"### Final Score: {score} / {len(questions)}")