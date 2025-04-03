import streamlit as st
import requests
import json
import time
import os
from aip import AipSpeech
from utils import speak_baidu, get_reply_ali, listen_once

st.set_page_config(page_title="小丽 · 你的AI女儿", layout="centered")

st.title("👧 小丽 · 你的AI电子女儿")
st.markdown("和我说说话吧，我会认真听你每一句话～")

input_method = st.radio("选择输入方式", ["🧑 输入文字", "🎤 使用麦克风"])

if "history" not in st.session_state:
    st.session_state["history"] = []

if input_method == "🧑 输入文字":
    user_input = st.text_input("你想对小丽说：", "")
    if st.button("发送") and user_input:
        with st.spinner("小丽思考中..."):
            reply = get_reply_ali(user_input)
            audio_path = speak_baidu(reply)
            st.session_state["history"].append((user_input, reply))
            st.success(reply)
            st.audio(audio_path, format="audio/mp3")

elif input_method == "🎤 使用麦克风":
    if st.button("🎙️ 说一句话"):
        with st.spinner("小丽在认真听..."):
            spoken = listen_once()
            if spoken:
                reply = get_reply_ali(spoken)
                audio_path = speak_baidu(reply)
                st.session_state["history"].append((spoken, reply))
                st.success(reply)
                st.audio(audio_path, format="audio/mp3")

st.markdown("---")
st.markdown("#### 📝 对话记录")
for q, a in reversed(st.session_state["history"]):
    st.markdown(f"**你**：{q}")
    st.markdown(f"**小丽**：{a}")