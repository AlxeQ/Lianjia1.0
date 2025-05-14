# 链家商圈经理提示词优化工具
# ✅ 保留所有原始需求功能：上传Excel、展示结构化提示、优化提示、查看历史

import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# 页面设置
st.set_page_config(page_title="链家提示词优化工具", layout="wide")
st.title("🏡 链家商圈经理提示词优化工具")
st.markdown("辅助商圈经理结构化表达问题，自动优化提示词")

# SessionState 初始化
if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar 设置
st.sidebar.header("配置")
api_key = st.sidebar.text_input("DeepSeek API Key", type="password")
model = st.sidebar.selectbox("选择模型", ["deepseek-chat"], index=0)

# 上传Excel文件（仅限主观题）
uploaded_file = st.file_uploader("📤 上传包含主观题的Excel文件（.xlsx）", type=["xlsx"])
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("文件上传成功！以下是主观题内容：")
        st.dataframe(df)
    except Exception as e:
        st.error(f"文件读取失败: {e}")
        df = None
else:
    df = None

# 用户输入原始提示词
st.subheader("✍️ 输入提示词")
initial_prompt = st.text_area("原始问题或需求描述：", height=100)

# 四要素结构输入
with st.expander("📦 补充结构化信息（可选）"):
    goal = st.text_input("🎯 目标：")
    background = st.text_area("📚 背景：", height=60)
    details = st.text_area("📌 关键细节：", height=60)
    expectation = st.text_area("🌟 你的期待：", height=60)

# 构造优化提示词的Prompt
if st.button("🚀 优化提示词"):
    if not api_key:
        st.warning("请填写 API Key")
    elif not initial_prompt.strip():
        st.warning("请输入原始提示词")
    else:
        system_prompt = "你是一个提示词优化专家，专门服务链家商圈经理，请使用通俗、实用的语言优化用户输入。"

        final_prompt = f"""
请基于以下内容优化提示词，使其适合用于AI生成清晰、结构化的回复。

原始输入：{initial_prompt}

结构化要素：
目标：{goal or "未提供"}
背景：{background or "未提供"}
关键细节：{details or "未提供"}
期待：{expectation or "未提供"}

请输出优化后的提示词，语言需贴近商圈经理的使用习惯。
"""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": final_prompt}
            ],
            "temperature": 0.7
        }

        try:
            response = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            optimized = result['choices'][0]['message']['content']

            st.subheader("✅ 优化后的提示词：")
            st.code(optimized, language="markdown")

            # 记录历史
            st.session_state.history.append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "original": initial_prompt,
                "optimized": optimized
            })

        except Exception as e:
            st.error(f"请求失败：{e}")

# 显示历史记录
with st.expander("🕘 查看提示词优化历史"):
    for record in reversed(st.session_state.history):
        st.markdown(f"**[{record['time']}]** 原始：{record['original']}")
        st.markdown(f"✅ 优化：{record['optimized']}")
        st.markdown("---")
