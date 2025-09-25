import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import time
import threading

from tkinter import PhotoImage



# 后续控件放置在这个标签上面

class MemoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Memo")
        self.root.geometry("450x450")
        self.root.configure(bg="#f0f0f0")  # 背景颜色
        # self.root.attributes('-alpha', 0.5)  # 设置窗口透明度（0.0 到 1.0，0.0 为完全透明）
        # self.root.wm_attributes('-transparentcolor', 'white')  # 将白色设为透明



        # 历史备忘录显示区域
        self.memo_list_frame = tk.Frame(self.root)#, bg="#f0f0f0"
        # self.memo_list_frame.attributes('-alpha', 0.8)  # 设置窗口透明度（0.0 到 1.0，0.0 为完全透明）

        self.memo_list_frame.grid(row=0, column=0, pady=1, padx=3)

        # 输入框
        self.memo_content = tk.Text(self.root, height=30, width=40, font=("Arial", 18))
        self.memo_content.grid(row=1, column=0, pady=1, padx=1)

        # self.save_button = tk.Button(self.root, text="保存", command=self.save_memo, font=("Arial", 12), bg="#4CAF50", fg="white", relief="solid")
        # self.save_button.grid(row=2, column=0, pady=10, padx=10)

        # 搜索框和按钮
        # self.search_label = tk.Label(self.root, text="搜索备忘录", font=("Arial", 12), bg="#f0f0f0")
        # self.search_label.grid(row=3, column=0, pady=5)
        # self.search_entry = tk.Entry(self.root, width=40, font=("Arial", 12))
        # self.search_entry.grid(row=4, column=0, pady=5, padx=10)

        # self.search_button = tk.Button(self.root, text="搜索", command=self.search_memo, font=("Arial", 12), bg="#2196F3", fg="white", relief="solid")
        # self.search_button.grid(row=5, column=0, pady=10, padx=10)

        # 添加快捷键支持
        self.root.bind("<Control-s>", lambda event: self.save_memo())
        self.root.bind("<Control-f>", lambda event: self.show_search_popup())
        self.root.bind("<Control-l>", lambda event: self.show_all_memos())


        # 定时折叠时间（分钟）
        self.fold_time_minutes = 10
        self.new_memo_interval = 60 * 60  # 每小时生成新备忘录（默认1小时）

        self.init_db()  # 初始化数据库
        self.load_memos()  # 加载历史备忘录

        # 自动保存用户输入
        # self.memo_content.bind("<KeyRelease>", self.auto_save)

    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect('memo.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS memos
                     (timestamp REAL, title TEXT, content TEXT)''')
        conn.commit()
        conn.close()


    def save_memo(self):
        """保存备忘录内容到数据库"""
        content = self.memo_content.get("1.0", tk.END).strip()
        if content:
            timestamp = time.time()
            title = content[:10]  # 简略标题

            # 检查数据库是否已有相同内容，若有则更新时间戳
            conn = sqlite3.connect('memo.db')
            c = conn.cursor()
            c.execute("SELECT * FROM memos WHERE content = ?", (content,))
            existing_memo = c.fetchone()

            if existing_memo:
                c.execute("UPDATE memos SET timestamp = ? WHERE content = ?", (timestamp, content))
            else:
                c.execute("INSERT INTO memos (timestamp, title, content) VALUES (?, ?, ?)",
                          (timestamp, title, content))

            conn.commit()
            conn.close()


            # 加载最近10分钟内的备忘录
            self.load_memos()

            # 清空输入框并通知保存成功
            self.memo_content.delete("1.0", tk.END)
            # messagebox.showinfo("提示", "备忘录保存成功！")
            self.schedule_fold(title, content, timestamp)  # 安排折叠任务

        else:
            messagebox.showwarning("警告", "备忘录内容不能为空！")

    def auto_save(self, event=None):
        """自动保存输入的内容"""
        content = self.memo_content.get("1.0", tk.END).strip()
        if content:
            timestamp = time.time()
            title = content[:10]  # 简略标题

            # 检查数据库是否已有相同内容，若有则更新时间戳
            conn = sqlite3.connect('memo.db')
            c = conn.cursor()
            c.execute("SELECT * FROM memos WHERE content = ?", (content,))
            existing_memo = c.fetchone()

            if existing_memo:
                c.execute("UPDATE memos SET timestamp = ? WHERE content = ?", (timestamp, content))
            else:
                c.execute("INSERT INTO memos (timestamp, title, content) VALUES (?, ?, ?)",
                          (timestamp, title, content))

            conn.commit()
            conn.close()

            # 加载最近10分钟内的备忘录
            self.load_memos()

    def load_memos(self):
        """从数据库加载近10分钟内的备忘录"""
        self.clear_memos()

        # 获取当前时间的时间戳
        current_time = time.time()
        # 只加载近10分钟内的记录
        time_threshold = current_time - (2 * 60)  # 10分钟

        conn = sqlite3.connect('memo.db')
        c = conn.cursor()
        c.execute("SELECT * FROM memos WHERE timestamp > ?", (time_threshold,))
        results = c.fetchall()
        conn.close()

        for memo in results:
            title = memo[1]
            timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(memo[0]))
            self.display_memo(title, timestamp_str, memo)

    def display_memo(self, title, timestamp_str, memo):
        """在主界面显示历史备忘录"""
        memo_label = tk.Label(self.memo_list_frame, text=f"{timestamp_str} - {title}", font=("Arial", 12), bg="#fffae6", relief="solid", anchor="w", padx=1)
        memo_label.grid(sticky="w", padx=1, pady=1)

        # 点击折叠的备忘录展示完整内容
        def on_memo_click(event, memo=memo):
            self.show_full_memo(memo)

        memo_label.bind("<Button-1>", on_memo_click)

    def show_full_memo(self, memo):
        """显示完整的备忘录内容"""
        full_memo_window = tk.Toplevel(self.root)
        full_memo_window.title("view memo")
        full_memo_window.geometry("450x300")

        timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(memo[0]))
        text_widget = tk.Text(full_memo_window, width=50, height=20, font=("Arial", 12))
        text_widget.insert(tk.END, f"标题：{memo[1]}\n保存时间：{timestamp_str}\n\n内容：\n{memo[2]}")
        text_widget.pack(padx=1, pady=1)
        text_widget.config(state=tk.DISABLED)

    # def search_memo(self):
    #     """根据搜索框的内容查找备忘录"""
    #     keyword = self.search_entry.get().strip()
    #     if keyword:
    #         conn = sqlite3.connect('memo.db')
    #         c = conn.cursor()
    #         c.execute("SELECT * FROM memos WHERE title LIKE ?", ('%' + keyword + '%',))
    #         results = c.fetchall()
    #         conn.close()

    #         if results:
    #             self.show_search_results(results)
    #         else:
    #             messagebox.showinfo("搜索结果", "未找到匹配的备忘录。")
    #     else:
    #         messagebox.showwarning("警告", "请输入搜索关键词！")

    def search_memo(self, keyword):
        """根据输入框的内容进行全文搜索备忘录"""
        conn = sqlite3.connect('memo.db')
        c = conn.cursor()

        # 使用LIKE进行全文搜索，匹配标题和内容
        c.execute("SELECT * FROM memos WHERE title LIKE ? OR content LIKE ?", ('%' + keyword + '%', '%' + keyword + '%'))
        results = c.fetchall()
        conn.close()

        if results:
            self.show_search_results(results)
        else:
            messagebox.showinfo("搜索结果", "未找到匹配的备忘录。")


    def show_search_results(self, results):
        """显示搜索结果"""
        search_window = tk.Toplevel(self.root)
        search_window.title("搜索结果")
        search_window.geometry("450x300")

        listbox = tk.Listbox(search_window, width=50, height=15, font=("Arial", 12))
        listbox.pack(padx=5, pady=5)

        for memo in results:
            timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(memo[0]))
            listbox.insert(tk.END, f"{timestamp_str} ------------------------------- {memo[1]}")  # 显示标题和时间戳

        def on_select(event):
            """点击列表项后查看完整内容"""
            selected_index = listbox.curselection()
            if selected_index:
                memo = results[selected_index[0]]
                self.show_full_memo(memo)

        listbox.bind("<Double-1>", on_select)

    def clear_memos(self):
        """清空历史记录"""
        for widget in self.memo_list_frame.winfo_children():
            widget.destroy()


    def show_all_memos(self):
        """展示所有备忘录数据"""
        conn = sqlite3.connect('memo.db')
        c = conn.cursor()
        c.execute("SELECT * FROM memos ORDER BY timestamp DESC")
        results = c.fetchall()
        conn.close()

        all_memos_window = tk.Toplevel(self.root)
        all_memos_window.title("所有备忘录")
        all_memos_window.geometry("450x300")

        listbox = tk.Listbox(all_memos_window, width=50, height=15, font=("Arial", 12))
        listbox.pack(padx=5, pady=5)

        for memo in results:
            timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(memo[0]))
            listbox.insert(tk.END, f"{timestamp_str} ------------------------------- {memo[1]}")  # 显示标题和时间戳


        def on_select(event):
            """点击列表项后查看完整内容"""
            selected_index = listbox.curselection()
            if selected_index:
                memo = results[selected_index[0]]
                self.show_full_memo(memo)

        listbox.bind("<Double-1>", on_select)



    def show_search_popup(self):
        """弹出搜索框"""
        search_popup = tk.Toplevel(self.root)
        search_popup.title("搜索备忘录")
        search_popup.geometry("400x70")

        # search_label = tk.Label(search_popup, text="请输入搜索内容：", font=("Arial", 12))
        # search_label.pack(padx=1,pady=1)

        search_entry = tk.Entry(search_popup, width=40, font=("Arial", 12))
        search_entry.pack(padx=5,pady=1)

        def on_search(event=None):
            """回车进行搜索"""
            keyword = search_entry.get().strip()
            if keyword:
                self.search_memo(keyword)
                search_popup.destroy()  # 关闭搜索框

        search_entry.bind("<Return>", on_search)

        search_button = tk.Button(search_popup, text="搜索", command=on_search, font=("Arial", 12), bg="#868E94", fg="white")
        search_button.pack(pady=5)

        search_entry.focus_set()  # 聚焦到搜索框

if __name__ == "__main__":
    root = tk.Tk()
    # bg_image = PhotoImage(file="2.png")

    # # 创建一个标签并放置图片作为背景
    # bg_label = tk.Label(root, image=bg_image)
    # bg_label.place(relwidth=1, relheight=1)
    app = MemoApp(root)
    root.mainloop()
