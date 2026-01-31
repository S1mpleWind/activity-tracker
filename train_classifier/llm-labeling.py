import json
import requests
from tqdm import tqdm
import re

# API配置
API_URL = 
API_KEY =   # 使用你的API密钥

def call_gpt(prompt):
    """调用GPT API"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": "gpt-5.2",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
    }
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        return None


def generate_labels_for_output(input_file="output.txt", output_file="dataset.jsonl"):
    """
    读取 output.txt，用GPT生成对应的标签
    格式: 进程名 | 窗口标题 -> 进程名 | 窗口标题 | 标签
    """
    print(f"📖 读取数据文件: {input_file}")
    
    # 读取数据
    texts = []
    with open(input_file, 'r', encoding='utf-8') as f:
        texts = [line.strip() for line in f if line.strip()]
    
    if not texts:
        print("❌ 数据文件为空")
        return
    
    print(f"📊 总共 {len(texts)} 条记录")
    
    # 定义标签类别
    categories = ["learning", "entertainment", "work", "social", "other"]
    
    # 提示词模板
    prompt_template = f"""
你是一个活动分类专家。根据给定的进程名和窗口标题，将其分类到以下类别之一：
{', '.join(categories)}

规则：
分类指南：
1. learning:代码编辑、学习资料、教程、课程视频，教学网站等
2. coding: 使用编程软件或者在命令行里执行命令，或者编辑代码（Code.exe, python.exe运行编程任务）
3. entertainment: 视频、游戏、音乐、娱乐网站等（视频播放器、游戏客户端）
4. documentation: 文档编辑、报告、表格、工作软件等（Word.exe, Excel.exe, PowerPoint.exe Pdf）
5. social: 社交通讯、即时消息、邮件等（QQ.exe, WeChat.exe, Outlook.exe）
6. other: 系统工具、浏览器闲置等

请直接返回分类结果，只返回一个类别名称，不要任何解释。

进程名: {{process_name}}
窗口标题: {{window_title}}

分类结果:
"""
    
    # 生成标签
    dataset = []
    print("🔄 正在生成标签...\n")
    
    for text in tqdm(texts, desc="生成标签"):
        # 解析文本
        if " | " not in text:
            continue
        
        process_name, window_title = text.split(" | ", 1)
        
        # 调用GPT生成标签
        prompt = prompt_template.replace("{{process_name}}", process_name).replace("{{window_title}}", window_title)
        label = call_gpt(prompt)
        
        if label:
            # 清理标签
            label = label.strip().lower()
            # 提取第一个有效的类别
            for cat in categories:
                if cat in label:
                    label = cat
                    break
            else:
                label = "other"
            
            # 保存到数据集
            dataset.append({
                "process_name": process_name,
                "window_title": window_title,
                "text": f"{process_name} {window_title}",
                "label": label
            })
    
    # 保存数据集
    print(f"\n💾 保存数据集到: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in dataset:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    # 统计结果
    print("\n" + "="*50)
    print("📊 标签统计:")
    print("="*50)
    label_counts = {}
    for item in dataset:
        label = item['label']
        label_counts[label] = label_counts.get(label, 0) + 1
    
    for label, count in sorted(label_counts.items()):
        print(f"{label:15s} : {count:4d} ({count/len(dataset)*100:.1f}%)")
    print("="*50 + f"\n✅ 成功生成 {len(dataset)} 条标记数据\n")


def generate_batch_labels(input_file="output.txt", output_file="dataset.jsonl", batch_size=5):
    """
    批量生成标签（为了效率，一次处理多条）
    """
    print(f"📖 读取数据文件: {input_file}")
    
    # 读取数据
    texts = []
    with open(input_file, 'r', encoding='utf-8') as f:
        texts = [line.strip() for line in f if line.strip()]
    
    if not texts:
        print("❌ 数据文件为空")
        return
    
    print(f"📊 总共 {len(texts)} 条记录")
    
    categories = ["learning", "entertainment", "work", "social", "other"]
    
    # 批量提示词
    batch_prompt_template = """
你是一个活动分类专家。对以下活动进行分类，每个分类到 {categories} 之一。

规则：
1. learning: 学习、编程、教程相关
2. entertainment: 娱乐、视频、游戏相关
3. work: 工作、文档、报告相关
4. social: 社交、通讯相关
5. other: 其他

请按照JSON格式返回结果，格式如下：
[
  {{"text": "进程名 窗口标题", "label": "分类结果"}},
  ...
]

需要分类的数据：
{data}

请直接返回JSON数组，不要任何其他内容。
"""
    
    dataset = []
    print("🔄 正在批量生成标签...\n")
    
    # 分批处理
    for i in tqdm(range(0, len(texts), batch_size), desc="批处理"):
        batch = texts[i:i+batch_size]
        batch_data = "\n".join([f"- {text}" for text in batch])
        
        prompt = batch_prompt_template.format(
            categories=", ".join(categories),
            data=batch_data
        )
        
        response = call_gpt(prompt)
        
        if response:
            try:
                # 提取JSON部分
                json_str = response[response.find('['):response.rfind(']')+1]
                results = json.loads(json_str)
                
                for result in results:
                    text = result.get('text', '')
                    label = result.get('label', 'other').lower()
                    
                    # 验证label
                    if label not in categories:
                        label = 'other'
                    
                    if " | " in text:
                        process_name, window_title = text.split(" | ", 1)
                    else:
                        process_name, window_title = text, ""
                    
                    dataset.append({
                        "process_name": process_name,
                        "window_title": window_title,
                        "text": text,
                        "label": label
                    })
            except json.JSONDecodeError:
                print(f"⚠️ 无法解析JSON: {response[:100]}")
                continue
    
    # 保存数据集
    print(f"\n💾 保存数据集到: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in dataset:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    # 统计结果
    print("\n" + "="*50)
    print("📊 标签统计:")
    print("="*50)
    label_counts = {}
    for item in dataset:
        label = item['label']
        label_counts[label] = label_counts.get(label, 0) + 1
    
    for label, count in sorted(label_counts.items()):
        print(f"{label:15s} : {count:4d} ({count/len(dataset)*100:.1f}%)")
    print("="*50 + f"\n✅ 成功生成 {len(dataset)} 条标记数据\n")


if __name__ == "__main__":
    # 选择一个方式运行
    
    # 方式1: 逐条生成标签（准确率高但速度慢）
    # generate_labels_for_output("output.txt", "dataset.jsonl")
    
    # 方式2: 批量生成标签（速度快但可能准确率稍低）
    generate_batch_labels("D:/files_n_data/learning/activity-tracker/train_classifier/output.txt", "dataset.jsonl", batch_size=5)