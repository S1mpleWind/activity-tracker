import json
import requests
from tqdm import tqdm
import random
import traceback
import time
import os

# API配置
API_URL = 
API_KEY = 

def call_llm(prompt):
    """调用LLM API"""
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
        response = requests.post(API_URL, json=payload, headers=headers, timeout=600)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                return content
        
        print(f"⚠️ API响应异常: 状态码 {response.status_code}")
        return None
            
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时")
        return None
    except Exception as e:
        print(f"❌ API调用失败: {type(e).__name__} - {str(e)}")
        return None


def generate_single_batch(batch_num, num_samples=300):
    """
    生成单个批次的数据
    
    :param batch_num: 批次编号
    :param num_samples: 本批次要生成的数量
    :return: 数据列表
    """
    
    categories = ["learning", "coding", "entertainment", "documentation", "social", "other"]
    
    prompt = f"""
你是Windows活动追踪数据生成专家。生成 {num_samples} 条真实的活动日志。

分类标准（每类约占{100//len(categories)}%）：
1. learning: 学习资料、教程、课程视频、教学网站
2. coding: 编程软件、代码编辑、命令行、IDE（Code.exe, python.exe）
3. entertainment: 娱乐视频、游戏、音乐、社交媒体浏览
4. documentation: 文档编辑、报告、表格、PDF阅读（Word.exe, Excel.exe）
5. social: 即时通讯、邮件、视频会议（QQ.exe, WeChat.exe）
6. other: 系统工具、文件管理器、桌面

要求：
- 各分类基本均匀分布
- 浏览器窗口要覆盖不同领域
- 需要增加额外的丰富的游戏数据（比如it takes two.exe ， 魔兽世界等）
- 每行一条JSON，不要任何额外说明

格式：{{"process_name": "xxx.exe", "window_title": "xxx", "label": "xxx"}}
"""
    
    print(f"[批次 {batch_num}] 🤖 调用API生成 {num_samples} 条数据...")
    response = call_llm(prompt)
    
    if not response:
        print(f"[批次 {batch_num}] ❌ API调用失败")
        return []
    
    # 解析响应
    dataset = []
    lines = response.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('```') or line.startswith('#'):
            continue
        
        try:
            item = json.loads(line)
            if 'process_name' in item and 'window_title' in item and 'label' in item:
                if item['label'] not in categories:
                    item['label'] = 'other'
                item['text'] = f"{item['process_name']} | {item['window_title']}"
                dataset.append(item)
        except json.JSONDecodeError:
            continue
    
    print(f"[批次 {batch_num}] ✅ 成功解析 {len(dataset)} 条数据")
    return dataset


def generate_large_dataset_batched(total_batches=10, batch_size=300, output_file="dataset_large.jsonl"):
    """
    分批生成大量数据
    
    :param total_batches: 总批次数（默认10）
    :param batch_size: 每批生成数量（默认300）
    :param output_file: 最终输出文件
    """
    
    print("="*60)
    print(f"🚀 分批生成数据集")
    print(f"   总批次数: {total_batches}")
    print(f"   每批数量: {batch_size}")
    print(f"   目标总数: {total_batches * batch_size}")
    print("="*60 + "\n")
    
    all_data = []
    
    # 分批生成
    for batch_num in range(1, total_batches + 1):
        print(f"\n{'='*60}")
        print(f"开始批次 {batch_num}/{total_batches}")
        print(f"{'='*60}")
        
        batch_data = generate_single_batch(batch_num, batch_size)
        
        if batch_data:
            all_data.extend(batch_data)
            print(f"✅ 批次 {batch_num} 完成，累计: {len(all_data)} 条")
            
            # 保存临时文件（防止中途失败）
            temp_file = f"temp_batch_{batch_num}.jsonl"
            with open(temp_file, 'w', encoding='utf-8') as f:
                for item in batch_data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
            print(f"💾 已保存临时文件: {temp_file}")
        else:
            print(f"❌ 批次 {batch_num} 失败")
        
        # 批次之间暂停，避免API限流
        if batch_num < total_batches:
            print(f"⏸️ 暂停3秒...")
            time.sleep(3)
    
    print(f"\n{'='*60}")
    print("📊 数据处理")
    print(f"{'='*60}")
    
    # 去重
    print(f"📝 去重中...")
    seen = set()
    unique_data = []
    for item in all_data:
        key = (item['process_name'], item['window_title'], item['label'])
        if key not in seen:
            seen.add(key)
            unique_data.append(item)
    
    duplicate_count = len(all_data) - len(unique_data)
    print(f"✅ 去除 {duplicate_count} 条重复数据")
    
    # 保存最终文件
    print(f"\n💾 保存最终数据到 {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in unique_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"✅ 保存成功")
    
    # 统计
    print("\n" + "="*60)
    print("📊 最终数据集统计")
    print("="*60)
    print(f"原始数据: {len(all_data)}")
    print(f"去重后: {len(unique_data)}\n")
    
    categories = ["learning", "coding", "entertainment", "documentation", "social", "other"]
    label_counts = {cat: 0 for cat in categories}
    
    for item in unique_data:
        label = item.get('label', 'other')
        if label in label_counts:
            label_counts[label] += 1
        else:
            label_counts['other'] += 1
    
    for label, count in sorted(label_counts.items()):
        percentage = (count / len(unique_data) * 100) if unique_data else 0
        print(f"{label:15s} : {count:4d} ({percentage:.1f}%)")
    
    print("="*60)
    print(f"✅ 完成！总计 {len(unique_data)} 条数据")
    print(f"💾 保存位置: {output_file}")
    
    # 清理临时文件
    print(f"\n🗑️ 清理临时文件...")
    for i in range(1, total_batches + 1):
        temp_file = f"temp_batch_{i}.jsonl"
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"  删除: {temp_file}")
    
    print("\n✅ 所有任务完成！\n")
    
    return True


if __name__ == "__main__":
    print("="*60)
    print("🚀 分批数据集生成工具")
    print("="*60 + "\n")
    
    try:
        # 生成数据：10批次，每批300条
        generate_large_dataset_batched(
            total_batches=15,      # 总批次数
            batch_size=500,        # 每批数量
            output_file="dataset_large.jsonl"
        )
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
        print("💡 提示: 临时文件已保存，可以手动合并 temp_batch_*.jsonl 文件")
    except Exception as e:
        print(f"\n\n❌ 程序异常: {type(e).__name__}")
        print(f"   详细信息: {str(e)}")
        traceback.print_exc()