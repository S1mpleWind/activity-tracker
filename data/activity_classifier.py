"""
活动分类器 - 用于对应用程序活动进行分类和统计
"""
import sqlite3
from typing import List, Dict, Any
from datetime import datetime

import pickle
import os
import jieba
import sys

import fasttext

class ActivityClassifier:
    """
    活动分类器
    将用户活动按类别进行分类（工作、学习、娱乐等）并统计时间占比
    """
    
    def __init__(self, db_path: str = "activity.db"):
        self.db_path = db_path
        
        # 定义分类关键词
        self.categories = {
            'documentation': {
                'keywords': [
                           'excel', 'word', 'feishu', '飞书', 'outlook', 'slack', '文献' , '论文',
                           'jira', 'confluence', 'notion', '钉钉', 'dingtalk'],
                'color': '#FF6B6B'
            },
            'coding':{
                'keywords': [
                    'code', 'visual studio', 'pycharm', 'github', 'gitlab',
                ],
                'color': '#D4CDC9'
            },
            'learning': {
                'keywords': ['jupyter', 'python', 'coursera', 'udemy', 'stackoverflow',
                           'documentation', 'tutorial', 'deepseek', 'edpuzzle', 'github pages',
                           '学习', '教程', '文档'],
                'color': '#4ECDC4'
            },
            'social': {
                'keywords': ['wechat', 'qq', 'outlook', 'gmail', 'telegram', 'discord', 'weixin', 'teams', 'meeting',
                           'slack', 'teams', 'whatsapp', 'messenger', '微信', 'QQ'],
                'color': '#45B7D1'
            },
            'entertainment': {
                'keywords': [
                    # 原有关键词
                    'youtube', 'netflix', 'steam', 'game', 'spotify', 'music',
                    'twitch', 'game' , '游戏', 'steam' , 'wegame'
                    
                    # ===== 热门3A游戏 =====
                    'cyberpunk', 'witcher', 'elden ring', 'dark souls', 'sekiro', 'bloodborne',
                    'god of war', 'horizon', 'spider-man', 'last of us', 'uncharted',
                    'red dead redemption', 'gta', 'grand theft auto', 'assassin', 'far cry',
                    'call of duty', 'cod', 'battlefield', 'apex legends', 'valorant', 'overwatch',
                    'destiny', 'halo', 'fortnite', 'pubg', 'warzone', 'counter-strike', 'csgo', 'cs2',
                    'resident evil', '生化危机', 'silent hill', 'dying light', 'dead space',
                    'fallout', 'skyrim', 'elder scrolls', 'starfield', 'fallout 4',
                    'monster hunter', '怪物猎人', 'mhw', 'mhr', 'dragons dogma',
                    'zelda', 'breath of the wild', 'tears of kingdom', 'mario', 'pokemon',
                    'final fantasy', 'ff14', 'ff16', 'kingdom hearts', 'nier', 'persona',
                    'yakuza', 'judgment', 'like a dragon', '如龙', 'it takes two' , 'starwar' ,
                    
                    # ===== MOBA/竞技 =====
                    'league of legends', 'lol', '英雄联盟', 'dota', 'dota2', 'smite',
                    'honor of kings', '王者荣耀', 'mobile legends', 'arena of valor',
                    
                    # ===== 射击游戏 =====
                    'rainbow six', 'r6', 'siege', 'payday', 'left 4 dead', 'l4d',
                    'borderlands', 'bioshock', 'metro', 'crysis', 'doom', 'quake',
                    'half-life', 'portal', 'team fortress', 'tf2', 'titanfall',
                    'halo infinite', 'gears of war', 'splitgate',
                    
                    # ===== MMO/网游 =====
                    'world of warcraft', 'wow', 'guild wars', 'new world', 'lost ark',
                    'black desert', '黑色沙漠', 'elder scrolls online', 'eso',
                    'final fantasy xiv', 'ff14', 'star wars', 'swtor',
                    '魔兽世界', '剑网3', '天涯明月刀', '逆水寒', '梦幻西游', '大话西游',
                    
                    # ===== 国产游戏 =====
                    '原神', 'genshin', '崩坏', 'honkai', '明日方舟', 'arknights',
                    '战双帕弥什', '碧蓝航线', 'azur lane', '少女前线', 'girls frontline',
                    '阴阳师', 'onmyoji', '第五人格', 'identity v', '蛋仔派对',
                    '黑神话', 'black myth', 'wukong', '悟空', '烟雨江湖',
                    '仙剑奇侠传', '古剑奇谭', '轩辕剑', '三国志', '三国杀',
                    
                    # ===== 策略/模拟 =====
                    'civilization', 'civ', '文明', 'total war', 'stellaris', 'crusader kings',
                    'europa universalis', 'hearts of iron', 'cities skylines', 'planet zoo',
                    'two point hospital', 'planet coaster', 'rimworld', 'oxygen not included',
                    'factorio', 'satisfactory', 'dyson sphere', '戴森球计划',
                    'terraria', '泰拉瑞亚', 'starbound', 'stardew valley', '星露谷',
                    'animal crossing', '动物森友会', 'sims', '模拟人生',
                    
                    # ===== 生存/沙盒 =====
                    'minecraft', '我的世界', 'rust', 'ark', '方舟', 'valheim', 'subnautica',
                    'dont starve', '饥荒', 'the forest', 'sons of the forest', 'green hell',
                    'raft', 'grounded', 'stranded deep', 'the long dark', '漫漫长夜',
                    '7 days to die', 'dayz', 'scum', 'conan exiles',
                    
                    # ===== 动作/冒险 =====
                    'tomb raider', '古墓丽影', 'batman', 'shadow of mordor', 'metal gear',
                    'devil may cry', 'dmc', 'bayonetta', 'astral chain', 'nier automata',
                    'hollow knight', '空洞骑士', 'ori', 'celeste', 'hades', 'dead cells',
                    'blasphemous', 'salt and sanctuary', 'hyper light drifter',
                    
                    # ===== 赛车游戏 =====
                    'forza', 'gran turismo', 'need for speed', 'nfs', 'assetto corsa',
                    'f1', 'dirt', 'wreckfest', 'trackmania', 'mario kart', 'kart',
                    
                    # ===== 格斗游戏 =====
                    'street fighter', '街霸', 'tekken', '铁拳', 'mortal kombat', 'mk',
                    'guilty gear', 'blazblue', 'dragon ball fighterz', '龙珠',
                    'super smash bros', '任天堂明星大乱斗', 'brawlhalla',
                    
                    # ===== 恐怖游戏 =====
                    'outlast', 'amnesia', 'layers of fear', 'little nightmares',
                    'phasmophobia', 'dead by daylight', 'dbd', 'friday the 13th',
                    'the quarry', 'until dawn', 'man of medan', 'soma',
                    
                    # ===== 独立游戏 =====
                    'undertale', 'deltarune', 'cuphead', 'binding of isaac', 'enter the gungeon',
                    'slay the spire', 'inscryption', 'loop hero', 'vampire survivors',
                    'brotato', 'among us', 'fall guys', 'human fall flat',
                    'getting over it', 'i am bread', 'goat simulator', 'untitled goose',
                    
                    # ===== 卡牌/桌游 =====
                    'hearthstone', '炉石传说', 'gwent', 'slay the spire', 'monster train',
                    'mtg arena', 'magic', 'yu-gi-oh', '游戏王', 'uno', '杀戮尖塔',
                    
                    # ===== 音游 =====
                    'beat saber', 'osu', 'cytus', 'deemo', 'phigros', 'arcaea',
                    'maimai', 'chunithm', 'project diva', 'taiko', '太鼓达人',
                    
                    # ===== 平台游戏商城 =====
                    'epic games', 'ubisoft connect', 'ea app', 'origin', 'gog galaxy',
                    'xbox app', 'playstation', 'battle.net', 'rockstar', 'riot client',
                    
                    # ===== 其他常见游戏术语 =====
                    'launcher', 'trainer', 'mod', 'cheat engine', 'rpg', 'fps', 'moba',
                    'mmo', 'mmorpg', 'roguelike', 'roguelite', 'metroidvania',
                ],
                'color': '#FFA07A'
            },
            'system': {
                'keywords': ['explorer', 'windows', 'settings', 'system', 'cmd',
                           'powershell', 'terminal', '文件', '设置', '资源管理器'],
                'color': '#95E1D3'
            },
        }
    
    def classify_activity(self, app_name: str, window_title: str) -> str:
        """
        根据应用名和窗口标题对活动进行分类
        
        Args:
            app_name: 应用程序名称
            window_title: 窗口标题
            
        Returns:
            str: 分类标签（'work', 'learning', 'communication', 'entertainment', 'system', 'other'）
        """
        # 对英文部分转小写，中文保持不变
        app_name_lower = app_name.lower()
        window_title_lower = window_title.lower()
        combined = f"{app_name_lower} {window_title_lower}"
        
        # 同时保留原始字符串用于中文匹配
        combined_original = f"{app_name} {window_title}"
        
        print(combined_original)
        
        for category, config in self.categories.items():
            for keyword in config['keywords']:
                keyword_lower = keyword.lower()
                
                # 检查小写匹配（主要用于英文关键词）
                if keyword_lower in combined:
                    return category
                
                # 检查原始大小写匹配（用于中文关键词）
                if keyword in combined_original:
                    return category
        
        ml_classify = ml_classify_activity(app_name,window_title)

        # TODO: this is a simpler classifier, need improve; for example, the browser and youtube/bilibili
        if ml_classify == None:
            return 'other'
        
        print (ml_classify)
        
        return ml_classify
    

    
    def get_classified_statistics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        获取指定日期范围内的分类统计
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            Dict: 包含分类统计信息
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取所有会话
            cursor.execute('''
                SELECT p.name, ws.window_title, ws.duration_seconds
                FROM window_sessions ws
                JOIN processes p ON ws.process_id = p.id
                WHERE DATE(ws.start_time) >= DATE(?) 
                  AND DATE(ws.start_time) <= DATE(?)
                  AND ws.end_time IS NOT NULL
                ORDER BY ws.start_time
            ''', (start_date, end_date))
            
            sessions = cursor.fetchall()
        
        # 分类和统计
        classified = {}
        for category in self.categories.keys():
            classified[category] = {
                'seconds': 0,  # 改为秒数统计，避免舍入误差
                'minutes': 0,
                'hours': 0.0,
                'percentage': 0.0,
                'session_count': 0,
                'color': self.categories[category]['color']
            }
        classified['other'] = {
            'seconds': 0,  # 改为秒数统计，避免舍入误差
            'minutes': 0,
            'hours': 0.0,
            'percentage': 0.0,
            'session_count': 0,
            'color': '#999999'
        }
        
        # 统计各类别
        total_seconds = 0
        for app_name, window_title, duration_seconds in sessions:
            category = self.classify_activity(app_name, window_title)
            classified[category]['seconds'] += duration_seconds  # 直接累加秒数
            classified[category]['session_count'] += 1
            total_seconds += duration_seconds
        
        # 计算小时和百分比
        if total_seconds > 0:
            for category in classified:
                seconds = classified[category]['seconds']
                classified[category]['minutes'] = seconds // 60  # 在最后转换
                classified[category]['hours'] = round(seconds / 3600, 2)
                classified[category]['percentage'] = round(
                    (seconds / total_seconds) * 100, 1
                )
                del classified[category]['seconds']  # 删除中间变量
        
        return {
            'statistics': classified,
            'total_minutes': total_seconds // 60,
            'total_hours': round(total_seconds / 3600, 2),
            'start_date': start_date,
            'end_date': end_date
        }
    

    def get_top_apps_by_category(self, start_date: str, end_date: str, 
                                  category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取指定分类中使用最频繁的应用
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            category: 分类标签
            limit: 返回结果数量限制
            
        Returns:
            List: 应用列表，按时长降序排列
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT p.name, ws.window_title, 
                       SUM(ws.duration_seconds) as total_seconds,
                       COUNT(*) as session_count
                FROM window_sessions ws
                JOIN processes p ON ws.process_id = p.id
                WHERE DATE(ws.start_time) >= DATE(?) 
                  AND DATE(ws.start_time) <= DATE(?)
                GROUP BY p.name, ws.window_title
                ORDER BY total_seconds DESC
                LIMIT ?
            ''', (start_date, end_date, limit))
            
            apps = []
            for app_name, window_title, total_seconds, count in cursor.fetchall():
                # 检查是否属于该分类
                if self.classify_activity(app_name, window_title) == category:
                    apps.append({
                        'app': app_name,
                        'window': window_title,
                        'minutes': total_seconds // 60,
                        'hours': round(total_seconds / 3600, 2),
                        'session_count': count
                    })
            
            return apps[:limit]
    

    def get_daily_classification(self, date: str) -> Dict[str, Any]:
        """
        获取单日的分类统计
        
        Args:
            date: 日期 (YYYY-MM-DD)
            
        Returns:
            Dict: 该日的分类统计
        """
        return self.get_classified_statistics(date, date)
    

    def get_weekly_classification(self, start_date: str) -> Dict[str, Any]:
        """
        获取周分类统计（从指定日期开始的7天）
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            
        Returns:
            Dict: 一周的分类统计
        """
        from datetime import datetime, timedelta
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = start + timedelta(days=6)
        return self.get_classified_statistics(
            start.strftime("%Y-%m-%d"),
            end.strftime("%Y-%m-%d")
        )


# ==============version of IDF ===========

# _MODEL_CACHE = {
#     "vectorizer": None,
#     "classifier": None
# }

# # def _load_model(model_path: str = "model/classifier_model.pkl"):
# #     if _MODEL_CACHE["vectorizer"] is None or _MODEL_CACHE["classifier"] is None:
# #         if not os.path.exists(model_path):
# #             print(f"⚠️ 模型文件不存在: {model_path}")
# #             return None, None
# #         with open(model_path, "rb") as f:
# #             vectorizer, classifier = pickle.load(f)
# #         _MODEL_CACHE["vectorizer"] = vectorizer
# #         _MODEL_CACHE["classifier"] = classifier
# #     return _MODEL_CACHE["vectorizer"], _MODEL_CACHE["classifier"]

# def _load_model(model_path: str = None):
#     """
#     加载模型 - 自动处理开发和生产环境的路径
#     """
#     if model_path is None:
#         # 获取程序基础目录（开发环境和 EXE 都适用）
#         if getattr(sys, 'frozen', False):
#             # PyInstaller 打包后的 EXE 环境
#             base_dir = sys._MEIPASS
#         else:
#             # 开发环境
#             base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
#         model_path = os.path.join(base_dir, "model", "classifier_model.pkl")

# def _preprocess(text: str) -> str:
#     words = jieba.cut(text)
#     words = [w for w in words if w.strip() and w not in ["-", "|", ".", "。"]]
#     return " ".join(words)

# def ml_classify_activity(app_name: str, window_title: str):
#     """
#     使用训练好的模型进行分类
#     """
#     vectorizer, classifier = _load_model()
#     if vectorizer is None or classifier is None:
#         return None

#     try:
#         text = f"{app_name} | {window_title}"
#         processed = _preprocess(text)
#         X = vectorizer.transform([processed])
#         pred = classifier.predict(X)[0]
#         return pred
#     except Exception as e:
#         print(f"⚠️ 模型预测失败: {e}")
#         return None


_MODEL_CACHE = {
    "fasttext_model": None
}

def _get_base_dir():
    """获取程序基础目录（开发和生产环境都适用）"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后的 EXE 环境
        return sys._MEIPASS
    else:
        # 开发环境：从 activity_classifier.py 往上两级找到项目根目录
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_fasttext_model(model_path: str = None):
    """加载 FastText 模型"""
    # if not HAS_FASTTEXT:
    #     return None
    
    if _MODEL_CACHE["fasttext_model"] is not None:
        return _MODEL_CACHE["fasttext_model"]
    
    if model_path is None:
        base_dir = _get_base_dir()
        # 优先使用压缩版本 (.ftz) 以减小打包大小
        model_path = os.path.join(base_dir, "model", "fasttext_model_compressed.ftz")
        # if not os.path.exists(model_path):
        #     # 降级到 .bin 版本
        #     model_path = os.path.join(base_dir, "model", "fasttext_model.bin")
    
    if not os.path.exists(model_path):
        print(f"⚠️ FastText 模型文件不存在: {model_path}")
        return None
    
    try:
        model = fasttext.load_model(model_path)
        _MODEL_CACHE["fasttext_model"] = model
        print(f"✅ 已加载 FastText 模型: {model_path}")
        return model
    except Exception as e:
        print(f"⚠️ 加载 FastText 模型失败: {e}")
        return None
    



def ml_classify_activity(app_name: str, window_title: str):
    """
    使用 FastText 模型进行分类
    
    Args:
        app_name: 应用名称
        window_title: 窗口标题
        
    Returns:
        str: 分类标签，如果失败返回 None
    """
    model = _load_fasttext_model()
    if model is None:
        return None
    
    try:
        text = f"{app_name} | {window_title}"
        prediction = model.predict(text, k=1)
        label = prediction[0][0].replace("__label__", "")
        return label
    except Exception as e:
        print(f"⚠️ FastText 预测失败: {e}")
        return None