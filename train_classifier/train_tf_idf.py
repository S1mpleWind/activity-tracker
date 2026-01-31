import json
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import pickle

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
# 第二步：文本预处理（中文分词）
# ═══════════════════════════════════
def preprocess(text):
    """文本预处理：分词 + 去除标点"""
    words = jieba.cut(text)
    words = [w for w in words if w.strip() and w not in ["-", "|", ".", "。"]]
    return " ".join(words)

print("⏳ 文本预处理...")
processed_texts = [preprocess(t) for t in texts]
print("✅ 预处理完成\n")

# ═══════════════════════════════════
# 第三步：TF-IDF 向量化
# ═══════════════════════════════════
print("⏳ TF-IDF 向量化...")
vectorizer = TfidfVectorizer(
    max_features=1000,      # 保留最重要的1000个词
    min_df=2,               # 至少在2个文档中出现
    max_df=0.8,             # 最多在80%文档中出现
    ngram_range=(1, 2)      # 使用1-gram和2-gram
)

X = vectorizer.fit_transform(processed_texts)
print(f"✅ 向量化完成: {X.shape[0]} 样本 × {X.shape[1]} 特征\n")

# ═══════════════════════════════════
# 第四步：划分训练集和测试集
# ═══════════════════════════════════
print("⏳ 划分训练集和测试集...")
X_train, X_test, y_train, y_test = train_test_split(
    X, labels, test_size=0.2, random_state=42, stratify=labels
)
print(f"✅ 训练集: {X_train.shape[0]}, 测试集: {X_test.shape[0]}\n")

# ═══════════════════════════════════
# 第五步：训练分类器
# ═══════════════════════════════════
print("⏳ 训练逻辑回归分类器...")
classifier = LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    random_state=42
)
classifier.fit(X_train, y_train)
print("✅ 训练完成\n")

# ═══════════════════════════════════
# 第六步：评估模型
# ═══════════════════════════════════
print("="*60)
print("📊 模型评估结果")
print("="*60)

# 训练集准确率
train_score = classifier.score(X_train, y_train)
print(f"训练集准确率: {train_score:.4f}")

# 测试集准确率
test_score = classifier.score(X_test, y_test)
print(f"测试集准确率: {test_score:.4f}")

# 详细分类报告
y_pred = classifier.predict(X_test)
print("\n详细分类报告:")
print(classification_report(y_test, y_pred))

# 混淆矩阵
print("混淆矩阵:")
cm = confusion_matrix(y_test, y_pred)
print(cm)
print("="*60 + "\n")

# ═══════════════════════════════════
# 第七步：保存模型
# ═══════════════════════════════════
print("💾 保存模型...")
with open("model/classifier_model.pkl", "wb") as f:
    pickle.dump((vectorizer, classifier), f)
print("✅ 模型已保存到 model/classifier_model.pkl\n")

# ═══════════════════════════════════
# 第八步：测试预测
# ═══════════════════════════════════
print("="*60)
print("🧪 测试预测")
print("="*60 + "\n")

test_cases = [
    "Code.exe Visual Studio Code",
    "Chrome 网页浏览",
    "Word 工作文档",
    "QQ 聊天工具",
    "It takes two.exe 双人成行",
    "League of Legends.exe 英雄联盟"
    "魔兽世界 魔兽"
]

for test_text in test_cases:
    processed = preprocess(test_text)
    vector = vectorizer.transform([processed])
    prediction = classifier.predict(vector)[0]
    probabilities = classifier.predict_proba(vector)[0]
    
    print(f"输入: {test_text}")
    print(f"预测分类: {prediction}")
    print(f"各类别概率:")
    
    for label, prob in sorted(
        zip(classifier.classes_, probabilities),
        key=lambda x: x[1],
        reverse=True
    ):
        print(f"  {label:15s} : {prob:.4f} ({prob*100:.2f}%)")
    print()

print("="*60)