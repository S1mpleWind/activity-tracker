import json
import fasttext
import os
from pathlib import Path

# ═══════════════════════════════════
# 第一步：从 dataset.jsonl 读取数据
# ═══════════════════════════════════
def load_dataset(file_path=""):
    """读取JSONL格式的数据集"""
    texts = []
    labels = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            texts.append(item['text'])
            labels.append(item['label'])
    
    return texts, labels

print("📖 加载数据集...")
texts, labels = load_dataset("D:/files_n_data/learning/activity-tracker/dataset_large.jsonl")
print(f"✅ 成功加载 {len(texts)} 条数据\n")

# 统计标签分布
print("📊 标签分布:")
label_counts = {}
for label in labels:
    label_counts[label] = label_counts.get(label, 0) + 1

for label, count in sorted(label_counts.items()):
    print(f"  {label:15s} : {count:4d} ({count/len(labels)*100:.1f}%)")
print()

# ═══════════════════════════════════
# 第二步：生成 FastText 训练文件
# ═══════════════════════════════════
print("⏳ 生成 FastText 训练文件...")

# FastText 格式：__label__<category> <text>
train_file = "fasttext_train.txt"
with open(train_file, 'w', encoding='utf-8') as f:
    for text, label in zip(texts, labels):
        # 清理文本：去除换行符
        clean_text = text.replace('\n', ' ').replace('\r', ' ')
        f.write(f'__label__{label} {clean_text}\n')

print(f"✅ 训练文件已生成: {train_file}\n")

# ═══════════════════════════════════
# 第三步：训练 FastText 模型
# ═══════════════════════════════════
print("⏳ 训练 FastText 模型...")
print("  这可能需要几分钟...\n")

model = fasttext.train_supervised(
    input=train_file,
    epoch=200,                    # 训练轮数（更多轮数 = 更好但更慢）
    lr=0.2,                      # 学习率
    wordNgrams=3,                # 使用 word n-gram（1-2 gram）
    dim=150,                     # 词向量维度（越大越准但越慢）
    minn=3,                      # 最小 char n-gram
    maxn=6,                      # 最大 char n-gram（subword 特征）
    loss='softmax',              # 损失函数
    bucket=200000,               # hash bucket 数量
    thread=4,                    # 使用 4 个线程
    verbose=2                    # 显示训练进度
)

print("\n✅ 模型训练完成\n")

# ═══════════════════════════════════
# 第四步：评估模型
# ═══════════════════════════════════
print("="*60)
print("📊 模型评估结果")
print("="*60)

# 获取模型预测性能指标
N, precision, recall = model.test(train_file)

print(f"训练集样本数: {N}")
print(f"精确率 (Precision): {precision:.4f}")
print(f"召回率 (Recall): {recall:.4f}")
print(f"F1 得分: {2 * precision * recall / (precision + recall):.4f}")
print("="*60 + "\n")

# ═══════════════════════════════════
# 第五步：测试预测
# ═══════════════════════════════════
print("="*60)
print("🧪 模型预测测试")
print("="*60 + "\n")

test_cases = [
    "Code.exe Visual Studio Code",
    "Chrome 网页浏览",
    "Word 工作文档",
    "QQ 聊天工具",
    "It takes two.exe 双人成行",
    "League of Legends.exe 英雄联盟",
    "魔兽世界 魔兽世界",
    "Steam 游戏平台",
    "Python 教程学习",
    "Outlook 工作邮件"
]

for test_text in test_cases:
    # 预测（返回 label 和 confidence）
    prediction = model.predict(test_text, k=3)  # 获取前 3 个预测
    labels_pred = prediction[0]
    scores = prediction[1]
    
    print(f"输入: {test_text}")
    print(f"预测结果 (前 3 个):")
    
    for label, score in zip(labels_pred, scores):
        label_clean = label.replace('__label__', '')
        print(f"  {label_clean:15s} : {score:.4f} ({score*100:.2f}%)")
    
    print()

print("="*60)

# ═══════════════════════════════════
# 第六步：保存模型
# ═══════════════════════════════════
print("\n💾 保存模型...")

# 创建 model 目录
Path("model").mkdir(exist_ok=True)

# 保存模型（有两种格式）
model_path = "model/fasttext_model"

# 1. 保存为 .bin（包含所有信息，可以继续训练）
    # 先保存 .bin，然后量化压缩


model.save_model(f"{model_path}.bin")
print(f"✅ 模型已保存 (bin 格式): {model_path}.bin")

model.quantize(input=train_file, qnorm=True, retrain=False, cutoff=100000)
model.save_model(f"{model_path}_compressed.ftz")
print(f"✅ 模型已保存 (ftz 格式): {model_path}_compressed.ftz")

# 输出模型大小
bin_size = os.path.getsize(f"{model_path}.bin") / (1024 * 1024)
print(f"\n📊 模型大小:")
print(f"  .bin 格式: {bin_size:.2f} MB")
print(f"  .ftz 格式: 约 {bin_size * 0.3:.2f} MB (压缩后)\n")

# ═══════════════════════════════════
# 第七步：使用示例
# ═══════════════════════════════════
print("="*60)
print("💡 使用建议")
print("="*60)
print("""
1. 单个预测：
   prediction = model.predict("Code.exe Python")[0][0]
   # 返回: '__label__learning'

2. 批量预测：
   predictions = model.predict(["text1", "text2", "text3"])

3. 获取置信度：
   label, score = model.predict("text", k=1)
   confidence = score[0]

4. 获取词向量：
   vector = model.get_word_vector("学习")

5. 在生产环境中使用（推荐用 .ftz 格式）：
   model = fasttext.load_model('model/fasttext_model_compressed.ftz')
""")

print("="*60)

# ═══════════════════════════════════
# 第八步：超参数调优建议
# ═══════════════════════════════════
print("\n🔧 如果效果不好，尝试调整：\n")
print("准确率太低:")
print("  - 增加 epoch: 25 → 50-100")
print("  - 增加 dim: 100 → 150-200")
print("  - 增加 wordNgrams: 2 → 3")
print()
print("模型太大:")
print("  - 减小 dim: 100 → 50-75")
print("  - 减小 bucket: 200000 → 100000")
print("  - 使用 .ftz 压缩格式")
print()
print("推理太慢:")
print("  - 减小 dim: 100 → 50")
print("  - 使用 .ftz 压缩格式")
print()

# ═══════════════════════════════════
# 清理临时文件
# ═══════════════════════════════════
print("\n🗑️ 清理临时文件...")
if os.path.exists(train_file):
    os.remove(train_file)
    print(f"✅ 已删除: {train_file}")

print("\n✅ 训练完成！")