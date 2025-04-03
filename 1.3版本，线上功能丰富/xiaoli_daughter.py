# -*- coding: utf-8 -*-
import os
import time
import json
import pygame
import requests
import openai
import speech_recognition as sr
from aip import AipSpeech

# ================= 百度语音合成配置 =================
BAIDU_APP_ID = '118339955'
BAIDU_API_KEY = 'CCtkiTJAQhgFCAHBoR0TW0LB'
BAIDU_SECRET_KEY = 'J2RRqtIkugQD5ZlMPJwu14I1aS6jsYUA'
baidu_client = AipSpeech(BAIDU_APP_ID, BAIDU_API_KEY, BAIDU_SECRET_KEY)

# ================= 阿里云百炼配置（通义千问） =================
ALI_API_KEY = 'sk-e4d8a3361419475e9f8d409e0fd1c649'
ALI_API_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'

# ================= 音频播放初始化 =================
pygame.mixer.init()

# ================= 小丽性格与记忆模块 =================
MEMORY_FILE = 'xiaoli_memory.json'
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        memory_history = json.load(f)
else:
    memory_history = []

XIAOLI_PERSONALITY = (
    "你是一位温柔、贴心、有智慧的女儿，善于倾听、安慰和鼓励他人。"
    "你特别在意对话者的感受，会用体贴的方式回应，帮助他们更好地理解世界。"
)

def speak_baidu(text):
    audio_dir = "audio"
    os.makedirs(audio_dir, exist_ok=True)
    filename = os.path.join(audio_dir, f"xiaoli_reply_{int(time.time())}.mp3")
    result = baidu_client.synthesis(text, 'zh', 1, {
        'vol': 5, 'spd': 4, 'pit': 6, 'per': 4  # 可调参数
    })
    if not isinstance(result, dict):
        with open(filename, 'wb') as f:
            f.write(result)
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.3)
    else:
        print("[语音合成失败]", result)

def get_reply_ali(prompt):
    # 添加性格和记忆内容作为上下文
    history_text = "\n".join([f"用户：{h['user']}\n小丽：{h['xiaoli']}" for h in memory_history[-3:]])  # 限制为最近3轮对话
    full_prompt = f"{XIAOLI_PERSONALITY}\n{history_text}\n用户：{prompt}\n小丽："

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ALI_API_KEY}"
    }
    body = {
        "model": "qwen-turbo",
        "input": {
            "prompt": full_prompt
        }
    }
    try:
        response = requests.post(ALI_API_URL, headers=headers, data=json.dumps(body))
        data = response.json()
        reply = data['output']['text'].strip()
        # 存入记忆
        memory_history.append({"user": prompt, "xiaoli": reply})
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(memory_history[-10:], f, ensure_ascii=False, indent=2)  # 最多保留10轮
        return reply
    except Exception as e:
        print("[阿里云百炼出错]", e)
        return "抱歉，我的大脑短路了一下。"

def listen_once():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 小丽正在聆听...（请说话）")
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

if __name__ == '__main__':
    print("🤖 小丽已启动，随时听候召唤。说“退出”可关闭程序。")
    while True:
        user_input = listen_once()
        if not user_input:
            continue
        if user_input in ["退出", "关闭"]:
            speak_baidu("好的，我先休息啦~")
            break
        reply = get_reply_ali(user_input)
        print("小丽：", reply)
        speak_baidu(reply)