import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import time
import re
import os
import getpass
import ast

from cryptography.fernet import Fernet
from functools import partial
from rsa_dec import load_public,load_private,rsa_encrypt,rsa_decrypt,make_key,key_maker
from to_blockchain import set_user_memo
from dotenv import load_dotenv

load_dotenv()  # take environment variables
FOLD_TIME = float(os.getenv("FOLD_TIME"))
KEY_FILE = os.getenv("KEY_FILE")
ENC_METHOD = os.getenv("ENC_METHOD")
STRING_LENGTH = os.getenv("STRING_LENGTH")
TO_BLOCKCHAIN = os.getenv("TO_BLOCKCHAIN") == "True"

# --------------------------------------
# AES
# ----------------------------------------
# KEY_FILE = "mome.key"
if not ENC_METHOD == 'RSA':
    # 生成密钥（保存到本地，只需要生成一次）
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)

# -------------------------------
# 读取密钥
# -------------------------------
def load_key():
    with open(KEY_FILE, "rb") as f:
        return f.read()

# -------------------------------
# 3) 加解密
# -------------------------------
def encrypt_text(plaintext: str, fernet: Fernet) -> str:
    return fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

def decrypt_text(token: str, fernet: Fernet) -> str:
    return fernet.decrypt(token.encode("utf-8")).decode("utf-8")

# -----------------------------------
# RSA
# -------------------------------------
def enc(plaintext):
    if ENC_METHOD == 'RSA':
        public_key = load_public()
        ciphertext = rsa_encrypt(plaintext.encode(),public_key)
        return ciphertext
    else:
        key = load_key()
        cipher = Fernet(key)
        ciphertext = encrypt_text(plaintext,cipher)
        return ciphertext

def dec(ciphertext,password = None):
    if ENC_METHOD == 'RSA':
        if password == None:
            private_key = load_private()
        else:
            # password = getpass.getpass("输入私钥密码：").strip()
            private_key = load_private(password=password.encode())
        # 使用 ast.literal_eval 将字符串转换为字节串
        ciphertext = ast.literal_eval(ciphertext)
        # 现在 ciphertext 就是一个字节串类型的对象，可以传给加密解密函数了
        # print(type(ciphertext))  # <class 'bytes'>
        decrypted = rsa_decrypt(ciphertext,private_key)
        return decrypted
    else:
        key = load_key()
        cipher = Fernet(key)
        decrypted = decrypt_text(ciphertext,cipher)
        return decrypted

# 圆角矩形函数
def round_rect(x1, y1, x2, y2, r, canvas,bg = "#b4b2a4"):
    # 画四个圆角
    canvas.create_oval(x1, y1, x1 + 2*r, y1 + 2*r, outline=bg, fill=bg)
    canvas.create_oval(x2 - 2*r, y1, x2, y1 + 2*r, outline=bg, fill=bg)
    canvas.create_oval(x1, y2 - 2*r, x1 + 2*r, y2, outline=bg, fill=bg)
    canvas.create_oval(x2 - 2*r, y2 - 2*r, x2, y2, outline=bg, fill=bg)

    # # 画矩形部分
    canvas.create_rectangle(x1 + r, y1, x2 - r, y2, outline=bg, fill=bg)
    canvas.create_rectangle(x1, y1 + r, x2, y2 - r, outline=bg, fill=bg)


class PlaceholderText:
    def __init__(self, text_widget, placeholder):
        self.text_widget = text_widget
        self.placeholder = placeholder
        self.text_widget.insert("1.0", self.placeholder)
        self.text_widget.config(fg="gray")  # 设置提示文本颜色为灰色

        # 绑定焦点事件
        self.text_widget.bind("<FocusIn>", self.on_focus_in)
        self.text_widget.bind("<FocusOut>", self.on_focus_out)

    def on_focus_in(self, event):
        """当文本框获得焦点时，如果是占位符，清空文本框"""
        current_text = self.text_widget.get("1.0", "end-1c")  # 获取文本框的内容
        if current_text == self.placeholder:
            self.text_widget.delete("1.0", "end")  # 删除占位符文本
            self.text_widget.config(fg="black")  # 设置文本颜色为黑色

    def on_focus_out(self, event):
        """当文本框失去焦点时，如果文本框为空，则重新显示占位符"""
        current_text = self.text_widget.get("1.0", "end-1c")
        if not current_text:
            self.text_widget.insert("1.0", self.placeholder)
            self.text_widget.config(fg="gray")



def check_thread_status(thread):
    if thread.is_alive():
        print("Thread is still running...")
        # 继续检查
        threading.Timer(1, check_thread_status, args=[thread]).start()
    else:
        print("Thread has finished.")

# 后续控件放置在这个标签上面

class MemoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Memo")
        self.font = 'Leelawadee UI'
        self.bg = "#ECF0F1"
        self.root.geometry("300x480+950+0")
        self.root.configure(bg=self.bg)  # 背景颜色
        self.root.overrideredirect(True)
        

        # self.root.iconify()  # 最小化窗口，保留在任务栏中
        # root.attributes('-transparentcolor', '#f5f5f5')  # 设置透明背景颜色
        # root.attributes('-transparentcolor', '#ECF0F1')  # 设置透明背景颜色

        # self.root.attributes('-alpha', 1)  # 设置窗口透明度（0.0 到 1.0，0.0 为完全透明）
        # self.root.wm_attributes('-transparentcolor', '#ECF0F1')  # 将白色设为透明'#fc0000'
        # self.root.call("wm", "attributes", ".", "-alpha", "0.6") # Window Opacity 0.0-1.0

        # # 创建Canvas，用来绘制圆角矩形
        # canvas = tk.Canvas(self.root, width=300, height=470)
        # canvas.grid()
        # # 设置圆角的半径
        # round_radius = 20
        # # 绘制圆角矩形
        # round_rect(10, 10, 300, 470, round_radius, canvas)


        # 历史备忘录显示区域
        self.memo_list_frame = tk.Frame(self.root,bg=self.bg)#, bg="#f0f0f0"
        self.memo_list_frame.grid(row=0, column=0, pady=0, padx=0)


        # # 输入框
        self.memo_content = tk.Text(self.root, height=30, width=33, font=(self.font, 12),bg=self.bg)
        self.memo_content.grid(row=1, column=0, pady=0, padx=0)
        # 设置占位符文本

        placeholder = """请输入您的内容...
        Control + S         保存
        Control + F         搜索
        Control + L         列出所有
        Control + B         退出
        Control + R         加密
        Alt + M               最小化"""
        placeholder_text = PlaceholderText(self.memo_content, placeholder)
        # 输入框
        # self.memo_content = tk.Text(self.root, height=20, width=28, font=(self.font, 12),bg="#c2b351")
        # self.memo_content.place(x=28,y=30)
        #保存按钮
        # self.save_button = tk.Button(self.root, text="保存", command=self.save_memo, font=(self.font, 12), bg="#4CAF50", fg="white", relief="solid")
        # self.save_button.grid(row=2, column=0, pady=10, padx=10)

        # 搜索框和按钮
        # self.search_label = tk.Label(self.root, text="搜索备忘录", font=(self.font, 12), bg="#f0f0f0")
        # self.search_label.grid(row=3, column=0, pady=5)
        # self.search_entry = tk.Entry(self.root, width=40, font=(self.font, 12))
        # self.search_entry.grid(row=4, column=0, pady=5, padx=10)

        # self.search_button = tk.Button(self.root, text="搜索", command=self.search_memo, font=(self.font, 12), bg="#2196F3", fg="white", relief="solid")
        # self.search_button.grid(row=5, column=0, pady=10, padx=10)

        # 添加快捷键支持
        self.root.bind("<Control-s>", lambda event: self.save_memo())
        self.root.bind("<Control-f>", lambda event: self.show_search_popup())
        self.root.bind("<Control-l>", lambda event: self.show_all_memos())
        self.root.bind("<Control-b>", lambda event: self.on_close())
        self.root.bind("<Control-r>", lambda event: self.insert_text_angle_brackets())
        self.root.bind("<Alt-m>", lambda event: self.minimize())  # Alt + M 最小化

        self.root.bind("<Control-S>", lambda event: self.save_memo())
        self.root.bind("<Control-F>", lambda event: self.show_search_popup())
        self.root.bind("<Control-L>", lambda event: self.show_all_memos())
        self.root.bind("<Control-B>", lambda event: self.on_close())
        self.root.bind("<Control-R>", lambda event: self.insert_text_angle_brackets())
        self.root.bind("<Alt-M>", lambda event: self.minimize())  # Alt + M 最小化
        # self.root.bind("<Alt-n>", lambda event: self.get_key())  # Alt + M 最小化


        # 当窗口获得焦点时恢复透明度
        self.root.bind("<FocusIn>", self.on_focus_in)
        
        # 当窗口失去焦点时设置为几乎透明
        self.root.bind("<FocusOut>", self.on_focus_out)

        # 定时折叠时间（分钟）
        self.fold_time_minutes = FOLD_TIME
        self.new_memo_interval = 60 * 60  # 每小时生成新备忘录（默认1小时）

        self.init_db()  # 初始化数据库
        self.load_memos()  # 加载历史备忘录
        self.memos = []  # 储存备忘录

        # 自动保存用户输入
        # self.memo_content.bind("<KeyRelease>", self.auto_save)
        #加密
        public_file="public.pem"
        if not os.path.exists(public_file) and ENC_METHOD == 'RSA':
            self.get_key()


    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect('memo.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS memos
                     (timestamp REAL, title TEXT, content TEXT)''')
        conn.commit()
        conn.close()

    def minimize(self, event=None):
        """最小化窗口"""
        self.root.withdraw()

    def maximize(self, event=None):
        """恢复窗口至原始大小"""
        if hasattr(self, 'saved_geometry'):
            self.root.geometry(self.saved_geometry)  # 恢复最小化前的窗口大小
        self.root.deiconify()  # 恢复窗口显示

    def insert_text_angle_brackets(self, event=None):
        """插入字符 '<>'，并将光标放在 <> 中间"""
        # 获取当前输入框的光标位置
        # 获取当前光标位置
        cursor_position = self.memo_content.index(tk.INSERT)
        
        # 插入 '《》'
        self.memo_content.insert(cursor_position, '<ENC><DEC>')

        # 将光标移动到《》的中间
        self.memo_content.mark_set(tk.INSERT, f"{cursor_position}+5c")  # 光标移到《后面
    
    def replace_in_brackets(self,text, replacements):
        """
        匹配括号内的内容，并逐个替换为给定的替换文本。

        Args:
        text (str): 输入文本。
        replacements (list): 替换的内容列表。

        Returns:
        str: 替换后的文本。
        """
        # 正则表达式匹配括号内的内容
        pattern = r'\<ENC\>(.*?)\<DEC\>'  # 匹配圆括号内的内容

        # 替换函数，逐个替换括号内的内容
        def replacer(match):
            # 从替换列表中依次取出替换内容
            nonlocal replacements
            replacement = replacements.pop(0)  # 获取并移除列表中的第一个元素
            return f'<ENC>{replacement}<DEC>'

        # 使用re.sub并传入替换函数
        return re.sub(pattern, replacer, text)

    def replace_same_in_brackets(self,text, replacement):
        """
        匹配括号内的内容，并替换为给定的替换文本。

        Args:
        text (str): 输入文本。
        replacement (str): 替换文本。

        Returns:
        str: 替换后的文本。
        """
        # 正则表达式匹配括号内的内容
        pattern = r'\<ENC\>(.*?)\<DEC\>'  # 匹配圆括号内的内容
        # 使用re.sub替换括号内的内容
        return re.sub(pattern, f'<ENC>{replacement}<DEC>', text)

    def re_and_enc(self,text):
        replacements =[]
        # 使用正则匹配括号内的内容
        matches = re.findall(r'\<ENC\>(.*?)\<DEC\>', text)
        # 输出匹配结果
        # print(matches)
        for plaintext in matches:
            
            # encrypted = encrypt_text(plaintext,self.cipher)
            encrypted = enc(plaintext)

            # print("加密后：", encrypted)
            replacements.append(encrypted)
        # print(replacements)
        result = self.replace_in_brackets(text, replacements)
        return result
    
    def on_chain(self,title, content):
        try:
            # 执行任务的代码
            set_user_memo(title, content)
        except Exception as e:
            # 将异常信息传递给主线程
            # error_queue.put(str(e))
            messagebox.showinfo("提示",f"上链失败！{str(e)}")

    def save_memo(self):
        """保存备忘录内容到数据库"""
        content = self.memo_content.get("1.0", tk.END).strip()
        # print(content)
        content = self.re_and_enc(content)
        # print(content)
        if content:
            timestamp = time.time()
            title = content[:8]  # 简略标题

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
            # self.schedule_fold(title, content, timestamp)  # 安排折叠任务
            # set_user_memo(title,content)

            if TO_BLOCKCHAIN:
                if len(content) < int(STRING_LENGTH):#字符串小于1200才上链
                    # threading.Thread(target=set_user_memo,args=(title,content,), daemon=True).start()

                    thread = threading.Thread(target=self.on_chain, args=(title,content), daemon=True)
                    thread.start()
                    # 在主线程中检查错误
                    # check_thread_status(thread)

                else:
                    messagebox.showinfo("提示","字符串太长，已存入本地数据库，不进行上链操作！")

        else:
            # messagebox.showwarning("警告", "备忘录内容不能为空！")
            print("警告", "备忘录内容不能为空！")


    def schedule_fold(self, title, content, timestamp):
        """设置定时折叠任务"""
        fold_time = self.fold_time_minutes * 60  # 将分钟转换为秒
        # threading.Timer(fold_time, self.fold_memo, [title, content, timestamp]).start()
        self.after(fold_time,self.schedule_fold)

    def fold_memo(self, title, content, timestamp):
        """折叠备忘录"""
        simplified_content = content[:10]  # 简略显示前10个字符
        timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        
        # 创建折叠后的备忘录显示
        memo_label = tk.Label(self.memo_list_frame, text=f"{simplified_content} - {timestamp_str}", font=(self.font, 12), bg="#fffae6", relief="solid", anchor="w", padx=10)
        # memo_label.grid(sticky="w", padx=5, pady=5)
        memo_label.pack(fill=tk.X)  # 填充水平方向


        # 保存备忘录
        self.memos.append({"title": simplified_content, "content": content, "timestamp": timestamp_str})
        # self.load_memos()


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
        time_threshold = current_time - (self.fold_time_minutes * 60)  # 10分钟

        conn = sqlite3.connect('memo.db')
        c = conn.cursor()
        c.execute("SELECT * FROM memos WHERE timestamp > ?", (time_threshold,))
        results = c.fetchall()
        conn.close()

        for memo in results:
            title = memo[1]
            timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(memo[0]))
            self.display_memo(title, timestamp_str, memo)

        if results == []:
            self.clear_memos()

        self.root.after(1000,self.load_memos)

    def clear_memos(self):
        """清空历史记录"""
    # 如果 memo_list_frame 已经存在，先销毁它
        if hasattr(self, 'memo_list_frame') and self.memo_list_frame:
            self.memo_list_frame.destroy()

        self.memo_list_frame = tk.Frame(self.root)#, bg="#f0f0f0"
        
        self.memo_list_frame.grid(row=0, column=0, pady=0, padx=0)

        
    def display_memo(self, title, timestamp_str, memo):
        """在主界面显示历史备忘录"""
        memo_label = tk.Label(self.memo_list_frame, text=f"{timestamp_str} - {title}", font=(self.font, 12), bg="#fcea52", relief="solid", anchor="w")#, padx=1
        memo_label.grid(sticky="w", padx=0, pady=1)
        # memo_label.grid(row=0, column=0, columnspan=2, sticky="nsew")  # 使标签跨越两列并居中
        # memo_label.pack(fill=tk.X)  # 填充水平方向
        # memo_label.pack(expand=True)  # 设置expand=True会使标签垂直和水平方向上都居中
        # 点击折叠的备忘录展示完整内容
        def on_memo_click(event, memo=memo):
            self.show_full_memo(memo)

        memo_label.bind("<Button-1>", on_memo_click)


    def show_dec(self,text):
        """弹出解码框"""
        show_dec = tk.Toplevel(self.root)
        show_dec.title("解密")
        show_dec.geometry("400x50")
        text_widget = tk.Text(show_dec, width=50, height=20, font=(self.font, 12))
        text_widget.insert(tk.END, f"解密：\n{text}")
        text_widget.pack(padx=1, pady=1)
        text_widget.config(state=tk.DISABLED)


    def on_click(self,event,index,test_original):
        """
        处理点击事件，区分点击的是哪一部分 `<ENC>***********<DEC>`
        :param event: 事件对象
        :param index: 区分点击区域的索引
        """
        # print(f"点击了第 {index + 1} 段加密内容")
        matches = re.findall(r'\<ENC\>(.*?)\<DEC\>', test_original)
        # 输出匹配结果
        # print(matches)
        try:
            # decrypted = decrypt_text(matches[index],self.cipher)
            try:
                decrypted = dec(matches[index])
                # print("解密后：", decrypted)
                self.show_dec(decrypted)
            except:
                self.input_secret(matches[index])
                
        except Exception as e:
            messagebox.showwarning("警告", f"解密失败，密钥/密码错误！{str(e)}")


    def make_clickable_text(self,text_widget, text, test_original,target_string="<ENC>***********<DEC>"):
        """
        在指定的 Text 小部件中，将所有的 target_string 标记为可点击的文本。
        
        :param text_widget: 需要添加点击功能的 Text 小部件
        :param text: 需要插入的文本
        :param target_string: 需要添加点击事件的目标字符串（默认为 <ENC>***********<DEC>）
        """
        # 在 Text 小部件中插入文本
        text_widget.insert(tk.END, text)

        start_pos = "1.0"  # 从文本的开始位置开始搜索
        index = 0  # 用于标记每个目标字符串的位置（如第1段，第2段等）

        # 利用 search 的迭代方式，避免使用 while True
        # while True:
        for _ in range(text.count(target_string)):
            start_pos = text_widget.search(target_string, start_pos, stopindex=tk.END)
            if not start_pos:  # 如果没有找到更多的 target_string
                break
            end_pos = text_widget.index(f"{start_pos}+{len(target_string)}c")
            
            # 创建标签，使得 target_string 部分可以点击
            text_widget.tag_add(f"clickable_{index}", start_pos, end_pos)

            # 配置标签属性（例如：显示为蓝色，带下划线）
            text_widget.tag_config(f"clickable_{index}", foreground="blue", underline=True)

            # 使用 partial 将索引传递给 on_click 函数
            text_widget.tag_bind(f"clickable_{index}", "<Button-1>", partial(self.on_click, index=index,test_original=test_original))

            # 更新start_pos，继续查找下一个 target_string
            start_pos = end_pos
            index += 1  # 增加索引，标记下一个 <***********> 的位置
            
    def show_full_memo(self, memo):
        """显示完整的备忘录内容"""
        #展示前替换加密字符
        memo_show = self.replace_same_in_brackets(memo[2],'***********')
        #

        full_memo_window = tk.Toplevel(self.root)
        full_memo_window.title("view memo")
        full_memo_window.geometry("450x300")

        timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(memo[0]))
        text_widget = tk.Text(full_memo_window, width=50, height=20, font=(self.font, 12))
        text_widget.insert(tk.END, f"标题：{memo[1]}\n保存时间：{timestamp_str}\n\n内容：\n{memo_show}")
        text_widget.pack(padx=1, pady=1)
        text_widget.config(state=tk.DISABLED)

        self.make_clickable_text(text_widget, memo_show,memo[2])

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

        listbox = tk.Listbox(search_window, width=50, height=15, font=(self.font, 12))
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

        listbox = tk.Listbox(all_memos_window, width=50, height=15, font=(self.font, 12))
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

        # search_label = tk.Label(search_popup, text="请输入搜索内容：", font=(self.font, 12))
        # search_label.pack(padx=1,pady=1)

        search_entry = tk.Entry(search_popup, width=40, font=(self.font, 12))
        search_entry.pack(padx=5,pady=1)

        def on_search(event=None):
            """回车进行搜索"""
            keyword = search_entry.get().strip()
            if keyword:
                self.search_memo(keyword)
                search_popup.destroy()  # 关闭搜索框

        search_entry.bind("<Return>", on_search)

        search_button = tk.Button(search_popup, text="搜索", command=on_search, font=(self.font, 12), bg="#868E94", fg="white")
        search_button.pack(pady=5)

        search_entry.focus_set()  # 聚焦到搜索框

    def input_secret(self,ciphertext):
        """输入密码"""
        input_secret = tk.Toplevel(self.root)
        input_secret.title("输入密码")
        input_secret.geometry("400x70")

        # search_label = tk.Label(search_popup, text="请输入搜索内容：", font=(self.font, 12))
        # search_label.pack(padx=1,pady=1)

        input_entry = tk.Entry(input_secret, width=40, font=(self.font, 12), show="*")
        input_entry.pack(padx=5,pady=1)

        def on_search(event=None):
            """回车进行搜索"""
            keyword = input_entry.get().strip()
            try:
                decrypted = dec(ciphertext,keyword)
                self.show_dec(decrypted)
            except TypeError as e:
                messagebox.showwarning("警告", f"解密失败，密钥/密码错误！{str(e)}")
            except ValueError as e:
                messagebox.showwarning("警告", f"解密失败，密钥/密码错误！{str(e)}")
            except:
                messagebox.showwarning("警告", f"解密失败，密钥/密码错误！")
        input_entry.bind("<Return>", on_search)

        search_button = tk.Button(input_secret, text="确定", command=on_search, font=(self.font, 12), bg="#868E94", fg="white")
        search_button.pack(pady=5)

        input_entry.focus_set()  # 聚焦到搜索框

    def get_key(self):
        """创建密钥"""
        get_key = tk.Toplevel(self.root)
        get_key.title("创建密钥")
        get_key.geometry("400x70")

        input_entry = tk.Entry(get_key, width=40, font=(self.font, 12), show="*")
        input_entry.pack(padx=5,pady=1)

        def on_search(event=None):
            """回车进行搜索"""
            keyword = input_entry.get().strip()

            try:
                if keyword:
                    key_maker(keyword.encode())
                else:
                    key_maker(password=None)
                get_key.destroy()  # 关闭搜索框
                messagebox.showwarning("提示", f"密钥对已生成注意保存！")

            except TypeError as e:
                messagebox.showwarning("提示", f"密钥对已生成出错了！{str(e)}")
        input_entry.bind("<Return>", on_search)

        save_button = tk.Button(get_key, text="确定", command=on_search, font=(self.font, 12), bg="#868E94", fg="white")
        save_button.pack(pady=5)

        input_entry.focus_set()  # 聚焦到搜索框

    def on_close(self):
        # 在这里可以添加一些自定义的关闭行为，例如确认框
        self.root.destroy()



    def on_focus_in(self, event):
        self.root.attributes('-alpha', 1.0)  # 恢复正常透明度

    def on_focus_out(self, event):
        self.root.attributes('-alpha', 0.1)  # 设置窗口几乎透明

import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image

def tray():
    file_path = os.path.join(os.getcwd(),'static\\favicon.png')

    root = tk.Tk()
    root.iconphoto(True, tk.PhotoImage(file=file_path))

    app = MemoApp(root)
    
    image = Image.open(file_path)
    menu = Menu(
        MenuItem("最小化", app.minimize),
        MenuItem("最大化", app.maximize),
        MenuItem("退出服务", app.on_close)
    )
    icon = Icon("Memo", image, "备忘录", menu)
    threading.Thread(target=icon.run, daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    tray()

