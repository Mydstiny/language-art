import re
import streamlit as st
from openai import OpenAI
from pathlib import Path

st.title('语言检测以及纠正')

# 从文件读取API密钥
def load_api_key():
    """从.streamlit/OPEN_AI_KEY文件读取API密钥"""
    # 向上查找项目根目录（包含.streamlit目录的目录）
    current_path = Path(__file__).resolve().parent
    project_root = None
    
    # 向上查找直到找到包含.streamlit目录的目录
    for parent in [current_path] + list(current_path.parents):
        streamlit_dir = parent / ".streamlit"
        if streamlit_dir.exists() and streamlit_dir.is_dir():
            project_root = parent
            break
    
    if project_root is None:
        # 如果找不到，尝试使用当前文件所在目录的父目录（项目根目录）
        project_root = current_path.parent
    
    key_file = project_root / ".streamlit" / "OPEN_AI_KEY"
    
    try:
        with open(key_file, 'r', encoding='utf-8') as f:
            api_key = f.read().strip()
            if not api_key:
                raise ValueError("API密钥文件为空")
            return api_key
    except FileNotFoundError:
        error_msg = f"未找到API密钥文件: {key_file}\n"
        error_msg += f"请确保在项目根目录下创建 .streamlit/OPEN_AI_KEY 文件"
        if hasattr(st, 'error'):
            st.error(error_msg)
            st.stop()
        else:
            raise FileNotFoundError(error_msg)
    except Exception as e:
        error_msg = f"读取API密钥文件时出错: {str(e)}\n文件路径: {key_file}"
        if hasattr(st, 'error'):
            st.error(error_msg)
            st.stop()
        else:
            raise Exception(error_msg)

# 初始化OpenAI客户端（延迟初始化，避免在非streamlit环境下出错）
@st.cache_resource
def get_openai_client():
    """获取OpenAI客户端（使用缓存避免重复初始化）"""
    api_key = load_api_key()
    if not api_key:
        st.error("无法加载API密钥")
        st.stop()
        return None
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# 延迟初始化客户端
client = None

def judge_level(text):
    """将歧视性语句换一种方法表述"""
    global client
    if client is None:
        client = get_openai_client()
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
          {"role": "system", "content": "### 定位：语言表述专家\n ### 任务：将歧视性语句换一种方法表述，使表述中不包含歧视语义。"},
          {"role": "user", "content": text},
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

def evaluate_text(text, is_original=True):
    """评价文本的歧视程度或改进程度"""
    global client
    if client is None:
        client = get_openai_client()
    if is_original:
        system_prompt = "### 定位：语言评价专家\n ### 任务：评价文本的歧视程度，给出0-100分的评分（0分表示完全没有歧视，100分表示严重歧视），并简要说明评分理由。请以以下格式输出：\n评分：XX分\n理由：XXX"
    else:
        system_prompt = "### 定位：语言评价专家\n ### 任务：评价文本的改进程度，给出0-100分的评分（0分表示完全没有改进，100分表示完全改进），并简要说明评分理由。请以以下格式输出：\n评分：XX分\n理由：XXX"
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
          {"role": "system", "content": system_prompt},
          {"role": "user", "content": text},
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

def extract_score(evaluation_text):
    """从评价文本中提取分数"""
    match = re.search(r'评分[：:]\s*(\d+)', evaluation_text)
    if match:
        return int(match.group(1))
    return None

# 用户输入
user_input = st.text_area("请输入需要检测和纠正的文本：", height=100)

if st.button("检测并纠正"):
    if user_input:
        with st.spinner('正在处理...'):
            try:
                # 评价原始文本
                st.subheader("📊 原始文本评价")
                original_evaluation = evaluate_text(user_input, is_original=True)
                original_score = extract_score(original_evaluation)
                
                if original_score is not None:
                    # 根据分数显示不同颜色
                    if original_score >= 70:
                        st.metric("歧视程度评分", f"{original_score}分", delta="严重", delta_color="inverse")
                    elif original_score >= 40:
                        st.metric("歧视程度评分", f"{original_score}分", delta="中等", delta_color="off")
                    else:
                        st.metric("歧视程度评分", f"{original_score}分", delta="轻微", delta_color="normal")
                
                st.write(original_evaluation)
                st.divider()
                
                # 纠正文本
                result = judge_level(user_input)
                st.success('处理完成！')
                
                # 显示纠正后的文本
                st.subheader("✅ 纠正后的文本：")
                st.write(result)
                st.divider()
                
                # 评价纠正后的文本
                st.subheader("📊 纠正后文本评价")
                corrected_evaluation = evaluate_text(result, is_original=False)
                corrected_score = extract_score(corrected_evaluation)
                
                if corrected_score is not None:
                    # 根据分数显示不同颜色
                    if corrected_score >= 70:
                        st.metric("改进程度评分", f"{corrected_score}分", delta="优秀", delta_color="normal")
                    elif corrected_score >= 40:
                        st.metric("改进程度评分", f"{corrected_score}分", delta="良好", delta_color="normal")
                    else:
                        st.metric("改进程度评分", f"{corrected_score}分", delta="一般", delta_color="off")
                
                st.write(corrected_evaluation)
                
            except Exception as e:
                st.error(f'错误: {str(e)}')
    else:
        st.warning('请输入文本')
