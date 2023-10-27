import requests
import logging
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
# 设置日志级别和日志文件
# logging.basicConfig(filename='api_request.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# 从配置文件中读取API令牌
# config = configparser.ConfigParser()
# config.read('config.ini')
api_token = "dk-VVXW9U32KSTMJDFIGR4PCPEWTQWZUOW6"
# if not api_token:
#     raise ValueError("Token not found in config.ini!")
# 设置URL
api_url = "https://api.todaoke.com/souti/v2/getAnswer"
# 创建一个Session对象
session = requests.Session()
# 构建请求头
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_token}'
}
def extract_question_and_options(data_string):
    # 如果字符串中没有"A."，则整个字符串都是问题
    if "A." not in data_string:
        return data_string, ""
    # 使用正则表达式提取问题和选项
    parts = data_string.split("A.", 1)
    question_str = parts[0].strip()
    options_str = "A." + parts[1].strip() if len(parts) > 1 else ''
    return question_str, options_str
def show_tooltip(event, text):
    global tooltip
    if tooltip:
        tooltip.destroy()
    x, y, _, _ = root.winfo_geometry().split('+')
    tooltip = tk.Toplevel(root)
    tooltip.wm_overrideredirect(True)
    tooltip.wm_geometry(f"+{int(x) + event.x_root + 20}+{int(y) + event.y_root}")
    label = tk.Label(tooltip, text=text, background="yellow", relief="solid", borderwidth=1)
    label.pack(ipadx=1)
def hide_tooltip(event=None):
    global tooltip
    if tooltip:
        tooltip.destroy()
        tooltip = None
def fetch_answers():
    question = question_entry.get()
    payload = {
        'question': question,
        'num': 1
    }
    try:
        response = session.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        # 记录成功的请求
        logging.info(f"请求成功。响应: {data}")
        # 保存返回的内容到文件
        # with open("response_data.txt", "a", encoding="utf-8") as file:
        #     file.write(str(data) + "\n")
        # 从每个结果中删除tid键，并检查问题匹配
        original_question = payload['question']
        filtered_data = []
        for result in data.get('data', []):
            if 'tid' in result:
                del result['tid']
            if original_question in result.get('question', ''):
                filtered_data.append(result)
        # ... [之前的代码]
        # 插入新数据到表格
        for item in data.get('data', []):
            full_question = item.get('question', '')
            question, options = extract_question_and_options(full_question)
            correct_answer = item.get('answer', '')
            # 截断超长的内容
            question = question if len(question) < 1000 else question[:1000] + "..."
            options = options if len(options) < 1000 else options[:1000] + "..."
            correct_answer = correct_answer if len(correct_answer) < 1000 else correct_answer[:1000] + "..."
            iid = tree.insert("", "end", values=(question, options, correct_answer))
            # 为每个单元格添加工具提示
            column_to_item_key = {
                "问题": "question",
                "选项": "question",  # 这里我们使用"question"键，因为选项是从完整的问题字符串中提取的
                "正确答案": "answer"
            }
            for col in tree["columns"]:
                tree.tag_bind(iid, f"<Enter-{col}>", lambda e, text=item[column_to_item_key[col]]: show_tooltip(e, text))
                tree.tag_bind(iid, f"<Leave-{col}>", hide_tooltip)
        # ... [后续代码]
    except requests.exceptions.RequestException as e:
        # 记录请求错误
        logging.error(f"请求错误: {e}")
        messagebox.showerror("Error", f"请求错误: {e}")
    except ValueError as e:
        # 记录JSON解码错误
        logging.error(f"解码 JSON 响应时出错: {e}")
        messagebox.showerror("Error", f"解码 JSON 响应时出错: {e}")
# 创建主窗口
root = tk.Tk()
root.title("学习通题库答案查询")
# 设置窗口图标
# 设置窗口图标
if getattr(sys, 'frozen', False):
    # 如果是打包的版本
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)
icon_path = os.path.join(base_path, '原图_200x200.ico')
root.iconbitmap(icon_path)
# 添加组件
tk.Label(root, text="输入您的问题：").pack(pady=10)
question_entry = tk.Entry(root, width=50)
question_entry.pack(pady=10)
tk.Button(root, text="获取答案", command=fetch_answers).pack(pady=10)
# 创建Treeview组件
tree = ttk.Treeview(root, columns=("问题", "选项", "正确答案"),show="headings")
tree.heading("问题", text="问题")
tree.heading("选项", text="选项")
tree.heading("正确答案", text="正确答案")
tree.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
# 主循环
root.mainloop()
