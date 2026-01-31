"""
train_classifier.get_txt_from_db

简单的数据库读取和文本导出工具
"""
import sqlite3
import os


def check_database_tables(db_path):
    """
    检查数据库中有哪些表
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询所有表名
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table'
        ''')
        
        tables = cursor.fetchall()
        print("数据库中的表:")
        for table in tables:
            print(f"  - {table[0]}")
            
            # 查看每个表的记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"    记录数: {count}")
            
        conn.close()
        return [t[0] for t in tables]
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return []


def export_to_txt(db_path, output_file="output.txt"):
    """
    从数据库读取可执行文件名字和窗口名字，导出到txt
    """
    try:
        # 先检查有哪些表
        print("正在检查数据库...")
        tables = check_database_tables(db_path)
        
        if not tables:
            print("❌ 数据库为空，请先运行主程序收集数据")
            return False
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # SQL查询：获取进程名和窗口标题
        cursor.execute('''
            SELECT p.name, ws.window_title
            FROM window_sessions ws
            JOIN processes p ON ws.process_id = p.id
            ORDER BY ws.start_time
        ''')
        
        # 获取所有数据
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            print("⚠️ 数据库中没有数据")
            return False
        
        # 写入txt文件
        with open(output_file, 'w', encoding='utf-8') as f:
            for process_name, window_title in rows:
                f.write(f"{process_name} | {window_title}\n")
        
        print(f"✅ 导出成功！共{len(rows)}条记录")
        print(f"保存到: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


if __name__ == "__main__":
    # 尝试多个可能的路径
    possible_paths = [
        "D:/files_n_data/learning/activity-tracker/train_classifier/data/activity1.db"
    ]
    
    print("尝试查找数据库...")
    for db_path in possible_paths:
        print(f"\n尝试路径: {db_path}")
        if os.path.exists(db_path):
            print(f"✅ 找到数据库文件!")
            export_to_txt(db_path, "train_classifier/output.txt")
            break
        else:
            print(f"❌ 文件不存在")
    else:
        print("\n❌ 所有路径都找不到数据库文件")