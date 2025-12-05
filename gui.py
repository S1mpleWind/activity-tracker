import customtkinter
import tkinter as tk
from tkinter import messagebox
import threading
import time
import sys
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from tracker.windows.windows_tracker import WindowsTracker
from config import Config
from data.database import ActivityDatabase
from data.data_analysis import DataAnalyzer
from data.visualize import Visualize

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Activity Tracker")
        self.geometry(f"{1000}x{600}")

        # configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # create sidebar frame
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Activity Tracker", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, command=self.show_dashboard, text="Dashboard")
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, command=self.show_analysis, text="Analysis")
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20))

        # Create Frames
        self.dashboard_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.analysis_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # Initialize Dashboard
        self.setup_dashboard()
        
        # Initialize Analysis
        self.setup_analysis()

        # Select default frame
        self.select_frame_by_name("dashboard")

        # Tracker & Data Setup
        self.config = Config()
        self.tracker = None
        if sys.platform == "win32":
            self.tracker = WindowsTracker(self.config)
        
        self.db = ActivityDatabase()
        self.analyzer = DataAnalyzer()
        
        self.is_tracking = False
        self.tracking_thread = None
        self.stop_event = threading.Event()

        # 快捷键：Ctrl+T 触发今日分析
        try:
            self.bind_all('<Control-t>', lambda e: self.load_today())
        except Exception:
            pass

    def setup_dashboard(self):
        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        self.dashboard_frame.grid_rowconfigure(1, weight=1)

        # Header
        self.status_label = customtkinter.CTkLabel(self.dashboard_frame, text="Status: Stopped", font=customtkinter.CTkFont(size=16, weight="bold"))
        self.status_label.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")

        self.toggle_button = customtkinter.CTkButton(self.dashboard_frame, text="Start Tracking", command=self.toggle_tracking, fg_color="green", hover_color="darkgreen")
        self.toggle_button.grid(row=0, column=1, padx=20, pady=(20, 0), sticky="e")

        # Log Area
        self.activity_textbox = customtkinter.CTkTextbox(self.dashboard_frame, width=400)
        self.activity_textbox.grid(row=1, column=0, columnspan=2, padx=20, pady=(20, 20), sticky="nsew")
        self.activity_textbox.insert("0.0", "Activity Log:\n\n")

        # Clearing controls
        self.clear_controls_frame = customtkinter.CTkFrame(self.dashboard_frame)
        self.clear_controls_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="nsew")
        self.clear_controls_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)  # 7列布局

        # Clear Today 按钮靠右，占 1/7 宽度
        self.clear_today_btn = customtkinter.CTkButton(self.clear_controls_frame, text="Clear Today", command=self.clear_today, fg_color="#d9534f")
        self.clear_today_btn.grid(row=0, column=5, columnspan=2, padx=5, pady=(0, 10), sticky="ew")

        # Clear Range 输入框和按钮靠右，占 1/7 宽度
        self.clear_range_start = customtkinter.CTkEntry(self.clear_controls_frame, placeholder_text="Start YYYY-MM-DD")
        self.clear_range_start.grid(row=1, column=3, padx=5, pady=(0, 5), sticky="ew")
        self.clear_range_end = customtkinter.CTkEntry(self.clear_controls_frame, placeholder_text="End YYYY-MM-DD")
        self.clear_range_end.grid(row=1, column=4, padx=5, pady=(0, 5), sticky="ew")

        self.clear_range_btn = customtkinter.CTkButton(self.clear_controls_frame, text="Clear Range", command=self.clear_range, fg_color="#d9534f")
        self.clear_range_btn.grid(row=1, column=5, columnspan=2, padx=5, pady=(0, 5), sticky="ew")

    def setup_analysis(self):
        self.analysis_frame.grid_columnconfigure(0, weight=1)
        self.analysis_frame.grid_rowconfigure(0, weight=0)  # 按钮区域
        self.analysis_frame.grid_rowconfigure(1, weight=1)  # 图表区域

        # 按钮区域
        self.button_frame = customtkinter.CTkFrame(self.analysis_frame)
        self.button_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        self.button_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)  # 按钮水平分布

        self.refresh_btn = customtkinter.CTkButton(self.button_frame, text="Refresh Data", command=self.refresh_charts)
        self.refresh_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.range_start_entry = customtkinter.CTkEntry(self.button_frame, placeholder_text="Start YYYY-MM-DD")
        self.range_start_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.range_end_entry = customtkinter.CTkEntry(self.button_frame, placeholder_text="End YYYY-MM-DD")
        self.range_end_entry.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.load_range_btn = customtkinter.CTkButton(self.button_frame, text="Load Range", command=self.load_range)
        self.load_range_btn.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.load_today_btn = customtkinter.CTkButton(self.button_frame, text="Today (Ctrl+T)", command=self.load_today)
        self.load_today_btn.grid(row=0, column=4, padx=5, pady=5, sticky="ew")

        # 图表区域
        self.chart_frame = None

        # Placeholder shown before user loads a range
        self.analysis_placeholder = customtkinter.CTkLabel(self.analysis_frame, text="Use 'Load Range' to display charts and tables.")
        self.analysis_placeholder.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.sidebar_button_1.configure(fg_color=("gray75", "gray25") if name == "dashboard" else "transparent")
        self.sidebar_button_2.configure(fg_color=("gray75", "gray25") if name == "analysis" else "transparent")

        # show selected frame
        if name == "dashboard":
            self.dashboard_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.dashboard_frame.grid_forget()
        
        if name == "analysis":
            self.analysis_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.analysis_frame.grid_forget()

    def show_dashboard(self):
        self.select_frame_by_name("dashboard")

    def show_analysis(self):
        self.select_frame_by_name("analysis")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def toggle_tracking(self):
        if not self.is_tracking:
            self.start_tracking()
        else:
            self.stop_tracking()

    def start_tracking(self):
        if self.tracker:
            self.is_tracking = True
            self.stop_event.clear()
            self.status_label.configure(text="Status: Tracking", text_color="green")
            self.toggle_button.configure(text="Stop Tracking", fg_color="red", hover_color="darkred")
            
            self.tracking_thread = threading.Thread(target=self.tracking_loop)
            self.tracking_thread.daemon = True
            self.tracking_thread.start()
            self.log_message("Tracking started...")

    def stop_tracking(self):
        self.is_tracking = False
        self.stop_event.set()
        
        # Stop DB session
        try:
            self.db.stop_current_session()
        except Exception as e:
            print(f"Error stopping session: {e}")

        self.status_label.configure(text="Status: Stopped", text_color="gray")
        self.toggle_button.configure(text="Start Tracking", fg_color="green", hover_color="darkgreen")
        self.log_message("Tracking stopped.")

    def tracking_loop(self):
        while not self.stop_event.is_set():
            try:
                # Foreground
                process_name, window_title = self.tracker.get_foreground_info()
                
                if process_name:
                    # Record to DB
                    # Check if session changed (simple check: just call record, it handles logic)
                    # Optimization: Only call if changed, but db.record_window_switch handles it?
                    # Let's check current session to avoid spamming DB calls if not needed, 
                    # but record_window_switch logic seems to handle "if changed".
                    # Actually, looking at combine_test.py, it checks manually.
                    
                    current_session = self.db.get_current_session_info()
                    should_record = False
                    
                    if current_session is None:
                        should_record = True
                    else:
                        session_process, session_title, _, _ = current_session
                        if process_name != session_process or window_title != session_title:
                            should_record = True
                    
                    if should_record:
                        if self.db.record_window_switch(process_name, window_title):
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            msg = f"[{timestamp}] Switched to: {process_name} - {window_title}\n"
                            self.update_log(msg)

                time.sleep(1) # Check every second
            except Exception as e:
                self.update_log(f"Error: {e}\n")
                time.sleep(5)

    def update_log(self, message):
        self.after(0, lambda: self._append_log(message))

    def _append_log(self, message):
        self.activity_textbox.insert("end", message)
        self.activity_textbox.see("end")

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.update_log(f"[{timestamp}] {message}\n")

    def refresh_charts(self):
        # Only refresh if chart_frame exists (we allocate it only on Load Range)
        if self.chart_frame is None:
            messagebox.showinfo("Info", "Use 'Load Range' to display charts.")
            return

        # Clear previous charts
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        try:
            # Get Data
            summary = self.analyzer.get_today_summary()
            app_usage = summary.get('app_usage', [])
            
            if not app_usage:
                label = customtkinter.CTkLabel(self.chart_frame, text="No data for today yet.")
                label.pack(pady=20)
                return

            # Prepare Data for chart using Visualize helper (choose pie or bar)
            viz = Visualize()
            # if many apps or long names, prefer bar chart
            choose_data = app_usage[:10]
            if len(choose_data) > 8 or any(len(item.get('name', '')) > 18 for item in choose_data):
                fig = viz.plot_bar_figure(choose_data, figsize=(7, None))
            else:
                fig = viz.plot_pie_figure(choose_data, figsize=(6, 5))

            # Embed in Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

            # Add a simple aggregated table showing today's usage per application
            aggregated = app_usage  # already aggregated by DataAnalyzer.get_today_summary()
            if aggregated:
                table_txt = customtkinter.CTkTextbox(self.chart_frame, height=160)
                table_txt.pack(fill="x", pady=(10, 0))
                table_txt.insert("0.0", "Process | Duration(min) | Duration(hours)\n")
                table_txt.insert("1.0", "" + ("-" * 80) + "\n")

                # sort by minutes desc
                for item in sorted(aggregated, key=lambda x: x.get('minutes', 0), reverse=True):
                    name = item.get('name')
                    minutes = item.get('minutes', 0)
                    hours = item.get('hours', 0)
                    line = f"{name} | {minutes} | {hours}\n"
                    table_txt.insert("end", line)

                table_txt.configure(state="disabled")
            else:
                info = customtkinter.CTkLabel(self.chart_frame, text="No aggregated app usage for today.")
                info.pack(pady=(10, 0))

        except Exception as e:
            label = customtkinter.CTkLabel(self.chart_frame, text=f"Error loading charts: {e}")
            label.pack(pady=20)
            

    def load_range(self):
        start = self.range_start_entry.get().strip()
        end = self.range_end_entry.get().strip()
        if not start or not end:
            messagebox.showwarning("Input required", "Please provide both start and end dates in YYYY-MM-DD format.")
            return

        try:
            usage = self.analyzer.get_usage_between(start, end)

            # create chart_frame if not exists
            if self.chart_frame is None:
                # hide placeholder
                try:
                    if getattr(self, 'analysis_placeholder', None):
                        self.analysis_placeholder.grid_forget()
                except Exception:
                    pass

                self.chart_frame = customtkinter.CTkFrame(self.analysis_frame)
                self.chart_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
                self.chart_frame.grid_rowconfigure(0, weight=1)
                self.chart_frame.grid_columnconfigure(0, weight=1)

            # Clear previous
            for widget in self.chart_frame.winfo_children():
                widget.destroy()

            if not usage:
                label = customtkinter.CTkLabel(self.chart_frame, text="No data in selected range.")
                label.pack(pady=20)
                return

            viz = Visualize()
            choose_data = usage[:20]
            if len(choose_data) > 8 or any(len(item.get('name', '')) > 18 for item in choose_data):
                fig = viz.plot_bar_figure(choose_data, figsize=(8, None))
            else:
                fig = viz.plot_pie_figure(choose_data, figsize=(6, 5))
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

            # show aggregated table
            table_txt = customtkinter.CTkTextbox(self.chart_frame, height=160)
            table_txt.pack(fill="x", pady=(10, 0))
            table_txt.insert("0.0", "Process | Duration(min) | Duration(hours)\n")
            table_txt.insert("1.0", "" + ("-" * 80) + "\n")
            for item in sorted(usage, key=lambda x: x.get('minutes', 0), reverse=True):
                name = item.get('name')
                minutes = item.get('minutes', 0)
                hours = item.get('hours', 0)
                line = f"{name} | {minutes} | {hours}\n"
                table_txt.insert("end", line)

            table_txt.configure(state="disabled")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load usage for range: {e}")

    def load_today(self):
        """快捷加载今日分析（可通过 Ctrl+T 触发）"""
        try:
            print("🔍 DEBUG: 开始 load_today")
            summary = self.analyzer.get_today_summary()
            usage = summary.get('app_usage', [])

            # 🎯 关键修复：确保数据有效
            # 1. 过滤掉分钟数为0的数据
            valid_usage = []
            for item in usage:
                minutes = item.get('minutes', 0)
                hours = item.get('hours', 0)

                # 只包含有实际使用时间的数据
                if minutes > 0 or hours > 0:
                    valid_usage.append(item)

            usage = valid_usage

            # 2. 如果没有有效数据，显示提示
            if not usage:
                # 显示无数据界面
                if self.chart_frame is None:
                    self.chart_frame = customtkinter.CTkFrame(self.analysis_frame)
                    self.chart_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

                # 清除之前的部件
                for widget in self.chart_frame.winfo_children():
                    widget.destroy()

                label = customtkinter.CTkLabel(
                    self.chart_frame,
                    text="📊 Today's usage data is too small to visualize\n\nTry using the computer for a few minutes first.",
                    font=("Arial", 14)
                )
                label.pack(pady=40)
                return

            # create chart_frame if not exists
            if self.chart_frame is None:
                # hide placeholder
                try:
                    if getattr(self, 'analysis_placeholder', None):
                        self.analysis_placeholder.grid_forget()
                except Exception:
                    pass

                self.chart_frame = customtkinter.CTkFrame(self.analysis_frame)
                self.chart_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
                self.chart_frame.grid_rowconfigure(0, weight=1)
                self.chart_frame.grid_columnconfigure(0, weight=1)

            # Clear previous
            for widget in self.chart_frame.winfo_children():
                widget.destroy()

            viz = Visualize()
            choose_data = usage[:10]

            # 🎯 再次验证数据
            if not choose_data or all(item.get('minutes', 0) == 0 for item in choose_data):
                label = customtkinter.CTkLabel(
                    self.chart_frame,
                    text="📊 Insufficient data for visualization\n(minutes values are all zero)",
                    font=("Arial", 12)
                )
                label.pack(pady=20)
                return

            # 🎯 修复：确保数据中有正值
            # 如果所有值都是0或很小，matplotlib会出错
            max_minutes = max(item.get('minutes', 0) for item in choose_data)
            if max_minutes <= 0:
                label = customtkinter.CTkLabel(
                    self.chart_frame,
                    text="No significant activity to display",
                    font=("Arial", 12)
                )
                label.pack(pady=20)
                return

            if len(choose_data) > 8 or any(len(item.get('name', '')) > 18 for item in choose_data):
                fig = viz.plot_bar_figure(choose_data, figsize=(8, None))
            else:
                fig = viz.plot_pie_figure(choose_data, figsize=(6, 5))

            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

            # show aggregated table
            table_txt = customtkinter.CTkTextbox(self.chart_frame, height=160)
            table_txt.pack(fill="x", pady=(10, 0))
            table_txt.insert("0.0", "Process | Duration(min) | Duration(hours)\n")
            table_txt.insert("1.0", "" + ("-" * 80) + "\n")

            # 对数据进行排序，确保有正值
            sorted_usage = sorted(usage, key=lambda x: x.get('minutes', 0), reverse=True)

            for item in sorted_usage:
                name = item.get('name', 'Unknown')
                minutes = item.get('minutes', 0)
                hours = item.get('hours', 0)

                # 格式化显示
                line = f"{name[:30]:30} | {minutes:10.2f} | {hours:12.4f}\n"
                table_txt.insert("end", line)

            table_txt.configure(state="disabled")

            # log
            self.log_message("Loaded today's analysis via shortcut")

        except Exception as e:
            print(f"❌ ERROR in load_today: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to load today's usage: {str(e)[:100]}...")

    def clear_today(self):
        if messagebox.askyesno("Confirm", "Delete all records for today? This cannot be undone."):
            deleted = self.db.delete_today_data()
            messagebox.showinfo("Deleted", f"Deleted {deleted} records for today.")
            self.log_message(f"Deleted {deleted} records for today.")
            # refresh GUI
            # destroy chart area if present and show placeholder
            try:
                if self.chart_frame is not None:
                    self.chart_frame.destroy()
                    self.chart_frame = None
                if getattr(self, 'analysis_placeholder', None):
                    self.analysis_placeholder.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
            except Exception:
                pass

    def clear_range(self):
        start = self.clear_range_start.get().strip()
        end = self.clear_range_end.get().strip()
        if not start or not end:
            messagebox.showwarning("Input required", "Please provide both start and end dates in YYYY-MM-DD format.")
            return
        if not messagebox.askyesno("Confirm", f"Delete records from {start} to {end}? This cannot be undone."):
            return
        try:
            deleted = self.db.delete_range(start, end)
            messagebox.showinfo("Deleted", f"Deleted {deleted} records from {start} to {end}.")
            self.log_message(f"Deleted {deleted} records from {start} to {end}.")
            # destroy chart area if present and show placeholder
            try:
                if self.chart_frame is not None:
                    self.chart_frame.destroy()
                    self.chart_frame = None
                if getattr(self, 'analysis_placeholder', None):
                    self.analysis_placeholder.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete range: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
