import streamlit as st
from utils import speak_baidu, get_reply_ali, listen_once, get_all_roles
import time

st.set_page_config(page_title="小丽 · AI电子家人", layout="centered")

st.title("👧 小丽 · 你的AI电子家人")
st.markdown("和我聊聊天吧～我可以是女儿、闺蜜、妈妈、哥哥，也可以是你最信任的心理导师✨")

# 初始化 session_state
if "history" not in st.session_state:
    st.session_state["history"] = []
if "role" not in st.session_state:
    st.session_state["role"] = "温柔女儿"

# 选择人格角色
st.sidebar.header("🧠 小丽的身份")
st.session_state["role"] = st.sidebar.radio("选择你希望的小丽是谁：", get_all_roles(), index=get_all_roles().index(st.session_state["role"]))

# 选择输入方式
input_method = st.radio("你想怎么和小丽说话？", ["💬 输入文字", "🎙️ 使用语音"])

# 文本输入
if input_method == "💬 输入文字":
    user_input = st.text_input("你：", "")
    if st.button("发送") and user_input:
        with st.spinner("小丽正在思考..."):
            reply = get_reply_ali(user_input, role=st.session_state["role"])
            audio_path = speak_baidu(reply)
            st.session_state["history"].append((user_input, reply))
            st.success("小丽：" + reply)
            if audio_path:
                st.audio(audio_path, format="audio/mp3")

# 语音输入
elif input_method == "🎙️ 使用语音":
    if st.button("🎧 开始说话"):
        with st.spinner("小丽在认真聆听..."):
            text = listen_once()
            if text:
                reply = get_reply_ali(text, role=st.session_state["role"])
                audio_path = speak_baidu(reply)
                st.session_state["history"].append((text, reply))
                st.success("小丽：" + reply)
                if audio_path:
                    st.audio(audio_path, format="audio/mp3")

# 对话历史
st.markdown("---")
st.markdown("#### 📜 对话记录")
for q, a in reversed(st.session_state["history"]):
    st.markdown(f"**你**：{q}")
    st.markdown(f"**小丽（{st.session_state['role']}）**：{a}")
