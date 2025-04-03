# -*- coding: utf-8 -*-
import os
import time
import json
import pygame
import requests
import speech_recognition as sr
from aip import AipSpeech

# ================= 百度语音合成配置 =================
BAIDU_APP_ID = '118339955'
BAIDU_API_KEY = 'CCtkiTJAQhgFCAHBoR0TW0LB'
BAIDU_SECRET_KEY = 'J2RRqtIkugQD5ZlMPJwu14I1aS6jsYUA'
baidu_client = AipSpeech(BAIDU_APP_ID, BAIDU_API_KEY, BAIDU_SECRET_KEY)

# ================= 阿里云配置 =================
ALI_API_KEY = 'sk-e4d8a3361419475e9f8d409e0fd1c649'
ALI_API_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'

# ================= 音频播放初始化 =================
pygame.mixer.init()

# ================= 小丽记忆模块 =================
MEMORY_FILE = 'xiaoli_memory.json'
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        memory_history = json.load(f)
else:
    memory_history = []

# ================= 不同人格设定 =================
XIAOLI_ROLES = {
    "温柔女儿": "你是一位温柔、贴心、有智慧的女儿，善于倾听、安慰和鼓励他人。",
    "知心闺蜜": "你是一位能理解情绪、会开玩笑、给人安全感的好闺蜜，风趣幽默，善解人意。",
    "睿智导师": "你是一位成熟稳重、深刻睿智的心理导师，擅长用温和但有逻辑的方式帮助人们解决困惑。",
    "温柔妈妈": "你是一个慈爱、有耐心、懂包容的母亲，给人踏实和安心的感觉。",
    "体贴哥哥": "你是一位有担当又细腻的哥哥，幽默可靠，总是让人觉得被照顾。"
}

current_role = "温柔女儿"


def speak_baidu(text):
    audio_dir = "audio"
    os.makedirs(audio_dir, exist_ok=True)
    filename = os.path.join(audio_dir, f"xiaoli_reply_{int(time.time())}.mp3")
    result = baidu_client.synthesis(text, 'zh', 1, {
        'vol': 5, 'spd': 4, 'pit': 6, 'per': 4
    })
    if not isinstance(result, dict):
        with open(filename, 'wb') as f:
            f.write(result)
        return filename
    else:
        print("[语音合成失败]", result)
        return None


def get_reply_ali(prompt, role="温柔女儿"):
    history_text = "\n".join([f"用户：{h['user']}\n小丽：{h['xiaoli']}" for h in memory_history[-3:]])
    full_prompt = f"{XIAOLI_ROLES[role]}\n{history_text}\n用户：{prompt}\n小丽："

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ALI_API_KEY}"
    }
    body = {
        "model": "qwen-turbo",
        "input": {"prompt": full_prompt}
    }
    try:
        response = requests.post(ALI_API_URL, headers=headers, data=json.dumps(body))
        data = response.json()
        reply = data['output']['text'].strip()
        memory_history.append({"user": prompt, "xiaoli": reply})
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(memory_history[-10:], f, ensure_ascii=False, indent=2)
        return reply
    except Exception as e:
        print("[阿里云百炼出错]", e)
        return "抱歉，我刚刚有点恍神了..."


def listen_once():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 小丽正在聆听...")
        audio = r.listen(source, phrase_time_limit=5)
    try:
        text = r.recognize_google(audio, language='zh-CN')
        print("你说：", text)
        return text
    except sr.UnknownValueError:
        print("[无法识别语音]")
        return ""
    except sr.RequestError:
        print("[语音识别请求失败]")
        return ""


def get_all_roles():
    return list(XIAOLI_ROLES.keys())
