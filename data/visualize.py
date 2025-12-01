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

    def plot_pie_figure(self, data, figsize=(6, 5)):
        """返回一个 matplotlib Figure，用于在 GUI 中嵌入或在其他上下文中显示。

        :param data: list of dicts with keys 'name' and 'minutes' (or 'minutes'-like)
        :param figsize: figure size tuple
        :return: matplotlib.figure.Figure
        """
        import textwrap

        labels = [item['name'] for item in data]
        sizes = [int(item.get('minutes', item.get('total_minutes', 0))) for item in data]

        # decide whether to place labels on wedges or use a legend
        use_legend = False
        if len(labels) > 8 or any(len(l) > 18 for l in labels):
            use_legend = True

        # shorten labels for display on chart
        def _shorten(s, width=18):
            return textwrap.shorten(s, width=width, placeholder='...')

        short_labels = [_shorten(l) for l in labels]

        # dynamic figsize: more items -> taller figure
        if figsize is None:
            figsize = (6, max(5, len(labels) * 0.5))
        else:
            figsize = (figsize[0], max(figsize[1], len(labels) * 0.5))

        fig = plt.Figure(figsize=figsize)
        ax = fig.add_subplot(111)

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=(None if use_legend else short_labels),
            autopct='%1.1f%%' if not use_legend else None,
            startangle=90,
            pctdistance=0.75,
            labeldistance=1.05,
            wedgeprops={'linewidth': 0.5, 'edgecolor': 'white'}
        )

        ax.set_title('应用使用时间分布')
        ax.axis('equal')

        if use_legend:
            # show legend to the right to avoid overlapping labels
            ax.legend(wedges, labels, title='应用', bbox_to_anchor=(1.02, 0.5), loc='center left')

        fig.tight_layout()
        return fig

    def plot_bar_figure(self, data, figsize=(7, None)):
        """绘制水平条形图，适合标签较多或标签较长的情况。

        data: list of dicts with 'name' and 'minutes' (or 'total_minutes')
        """
        import textwrap

        labels = [item['name'] for item in data]
        values = [int(item.get('minutes', item.get('total_minutes', 0))) for item in data]

        # sort by value desc
        pairs = sorted(zip(labels, values), key=lambda x: x[1], reverse=True)
        labels_sorted, values_sorted = zip(*pairs) if pairs else ([], [])

        # shorten long labels for display
        labels_display = [textwrap.shorten(l, width=30, placeholder='...') for l in labels_sorted]

        # dynamic height based on number of items
        height = max(4, len(labels_display) * 0.4)
        fig_height = height if figsize[1] is None else max(height, figsize[1])
        fig = plt.Figure(figsize=(figsize[0], fig_height))
        ax = fig.add_subplot(111)

        y_positions = range(len(labels_display))
        ax.barh(y_positions, values_sorted, color='tab:blue')
        ax.set_yticks(y_positions)
        ax.set_yticklabels(labels_display)
        ax.invert_yaxis()
        ax.set_xlabel('Minutes')
        ax.set_title('按应用使用时间（分钟）')

        fig.tight_layout()
        return fig