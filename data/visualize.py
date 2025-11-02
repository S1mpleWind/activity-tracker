# use matplotlib to visualize the time u spend on different
import matplotlib.pyplot as plt
class Visualize:
    def __init__(self):
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']  # 用来正常显示中文标签
        pass

    def visualize_daily(self,daily_data):
        total_hours = daily_data['total_hours']
        total_minutes = daily_data['total_minutes']
        if total_hours == 0 or total_minutes == 0: return
        if total_hours == 0: print("Total time: %f" % total_minutes)
        else:
            print(f"Total time: {total_hours} 小时 ，{total_minutes%60} 分钟")

        self.plot_pie(daily_data["app_usage"])



    def viualize_weekly(self):
        pass


    def visualize_monthly(self):
        pass

    def viualize_yearly(self):
        pass

    #=========

    #TODO: diffent charts: Pie/Bar for all Line for above a single day

    def plot_pie(self,data):

        """
        draw the pie chart

        :param data: list
        :return:
        """
        """从字典list绘制饼状图"""
        labels = [item['name'] for item in data]
        sizes = [item['minutes'] for item in data]

        plt.figure(figsize=(8, 6))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title('应用使用时间分布')
        plt.axis('equal')
        plt.show()


        pass