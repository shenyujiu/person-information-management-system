import sqlite3
from tkinter import *
from tkinter import ttk, messagebox


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("登录界面")
        self.setup_db()
        self.create_login_ui()
    
    def setup_db(self):
        self.conn = sqlite3.connect('users.db')
        self.c = self.conn.cursor()

        # 用户表
        self.c.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL)''')
        self.conn.commit()

    def create_login_ui(self):
        # 用户名和密码输入区域
        Label(self.root, text="用户名:").grid(row=0, column=0)
        self.username_entry = Entry(self.root)
        self.username_entry.grid(row=0, column=1)

        Label(self.root, text="密码:").grid(row=1, column=0)
        self.password_entry = Entry(self.root, show="*")
        self.password_entry.grid(row=1, column=1)
        
        # 登录和注册按钮
        Button(self.root, text="登录", command=self.login).grid(row=2, column=0, columnspan=2)
        Button(self.root, text="注册（按一下就注册）", command=self.register).grid(row=3, column=0, columnspan=2)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("登录失败", "用户名和密码不能为空。")
            return

        try:
            # 从数据库中查询用户信息
            self.c.execute("SELECT * FROM users WHERE username =? AND password =?", (username, password))
            user = self.c.fetchone()

            if user:
                self.root.destroy()
                main_root = Tk()
                app = InfoSystem(main_root)
                main_root.mainloop()
            else:
                messagebox.showerror("登录失败", "用户名或密码错误，请重试。")
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"登录时发生错误: {e}")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("注册失败", "用户名和密码不能为空。")
            return

        try:
            # 检查用户名是否已存在
            self.c.execute("SELECT * FROM users WHERE username = ?", (username,))
            if self.c.fetchone():
                messagebox.showerror("注册失败", "用户名已存在，请选择其他用户名。")
                return

            # 插入新用户到数据库
            self.c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            self.conn.commit()
            messagebox.showinfo("注册成功", "用户注册成功，请登录。")
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"注册时发生错误: {e}")
            self.conn.rollback()

    def __del__(self):
        # 关闭数据库连接
        if hasattr(self, 'conn'):
            self.conn.close()


class InfoSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("个人信息及成绩管理系统")
        self.setup_db()
        self.create_ui()
        
    def setup_db(self):
        self.conn = sqlite3.connect('person_info.db')
        self.cursor = self.conn.cursor()
        
        # 人员表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS persons (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                gender TEXT,
                phone TEXT,
                email TEXT
            )
        ''')
        
        # 成绩表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                student_id TEXT,
                subject TEXT,
                score REAL,
                PRIMARY KEY (student_id, subject),
                FOREIGN KEY(student_id) REFERENCES persons(id)
            )
        ''')
        self.conn.commit()

    def create_ui(self):
        self.notebook = ttk.Notebook(self.root)
        
        self.person_frame = Frame(self.notebook)
        self.create_person_ui()
        
        self.score_frame = Frame(self.notebook)
        self.create_score_ui()
        
        self.notebook.add(self.person_frame, text="个人信息")
        self.notebook.add(self.score_frame, text="成绩管理")
        self.notebook.pack(expand=1, fill="both")

    def create_person_ui(self):
        # 个人信息输入区域
        Label(self.person_frame, text="学号:").grid(row=0, column=0)
        self.id_entry = Entry(self.person_frame)
        self.id_entry.grid(row=0, column=1)

        Label(self.person_frame, text="姓名:").grid(row=1, column=0)
        self.name_entry = Entry(self.person_frame)
        self.name_entry.grid(row=1, column=1)

        Label(self.person_frame, text="性别:").grid(row=2, column=0)
        self.gender_entry = Entry(self.person_frame)
        self.gender_entry.grid(row=2, column=1)

        Label(self.person_frame, text="电话:").grid(row=3, column=0)
        self.phone_entry = Entry(self.person_frame)
        self.phone_entry.grid(row=3, column=1)

        Label(self.person_frame, text="邮箱:").grid(row=4, column=0)
        self.email_entry = Entry(self.person_frame)
        self.email_entry.grid(row=4, column=1)

        # 个人信息功能按钮
        Button(self.person_frame, text="添加", command=self.add_person).grid(row=5, column=0)
        Button(self.person_frame, text="查询", command=self.search_persons).grid(row=5, column=1)
        Button(self.person_frame, text="更新", command=self.update_person).grid(row=6, column=0)
        Button(self.person_frame, text="删除", command=self.delete_person).grid(row=6, column=1)

        # 个人信息显示区域
        self.person_tree = ttk.Treeview(self.person_frame, columns=("学号", "姓名", "性别", "电话", "邮箱"), show="headings")
        self.person_tree.grid(row=7, column=0, columnspan=2)
        for col in ["学号", "姓名", "性别", "电话", "邮箱"]:
            self.person_tree.heading(col, text=col)

    def create_score_ui(self):
        # 成绩输入区域
        Label(self.score_frame, text="学号:").grid(row=0, column=0)
        self.student_id_entry = Entry(self.score_frame)
        self.student_id_entry.grid(row=0, column=1)

        Label(self.score_frame, text="科目:").grid(row=1, column=0)
        self.subject_entry = Entry(self.score_frame)
        self.subject_entry.grid(row=1, column=1)

        Label(self.score_frame, text="分数:").grid(row=2, column=0)
        self.score_entry = Entry(self.score_frame)
        self.score_entry.grid(row=2, column=1)

        # 成绩功能按钮
        Button(self.score_frame, text="添加成绩", command=self.add_score).grid(row=3, column=0)
        Button(self.score_frame, text="查询成绩", command=self.search_scores).grid(row=3, column=1)
        Button(self.score_frame, text="更新成绩", command=self.update_scores).grid(row=4, column=0)
        Button(self.score_frame, text="删除成绩", command=self.delete_score).grid(row=4, column=1)

        # 成绩显示区域
        self.score_tree = ttk.Treeview(self.score_frame, columns=("学号", "科目", "分数"), show="headings")
        self.score_tree.grid(row=5, column=0, columnspan=2)
        for col in ["学号", "科目", "分数"]:
            self.score_tree.heading(col, text=col)

    # 个人信息操作方法
    def add_person(self):
        name = self.name_entry.get()
        id = self.id_entry.get()
        if not id:
            messagebox.showerror("错误", "学号不能为空")
            return
        if not name:
            messagebox.showerror("错误", "姓名不能为空")
            return
        self.cursor.execute(
            "INSERT INTO persons (id, name, gender, phone, email) VALUES (?, ?, ?, ?, ?)",
            (id,name, self.gender_entry.get(), self.phone_entry.get(), self.email_entry.get()))
        self.conn.commit()
        messagebox.showinfo("成功", "个人信息添加成功")
        self.clear_person_entries()
        self.search_persons()

    def search_persons(self):
        self.person_tree.delete(*self.person_tree.get_children())
        name = self.name_entry.get()
        query = "SELECT * FROM persons"
        params = ()

        if name:
            query += " WHERE name LIKE ?"
            params = (f"%{name}%",)

        self.cursor.execute(query, params)
        for row in self.cursor.fetchall():
            self.person_tree.insert("", END, values=row)

    def update_person(self):
        id = self.id_entry.get()
        if not id:
            messagebox.showerror("错误", "请输入要更新的学号")
            return

        self.cursor.execute("SELECT * FROM persons WHERE id=?", (id,))
        original_record = self.cursor.fetchone()
        if not original_record:
            messagebox.showerror("错误", "未找到匹配的记录")
            return

        name = self.name_entry.get()
        gender = self.gender_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()

        new_name = name if name else original_record[1]
        new_gender = gender if gender else original_record[2]
        new_phone = phone if phone else original_record[3]
        new_email = email if email else original_record[4]

        self.cursor.execute(
            "UPDATE persons SET name=?, gender=?, phone=?, email=? WHERE id=?",
            (new_name, new_gender, new_phone, new_email, id)
        )
        self.conn.commit()
        messagebox.showinfo("成功", "个人信息更新成功")
        self.clear_person_entries()
        self.search_persons()

    def delete_person(self):
        selected = self.person_tree.selection()
        if not selected:
            messagebox.showerror("错误", "请先选择要删除的记录")
            return

        person_id = self.person_tree.item(selected[0])['values'][0]
        self.cursor.execute("DELETE FROM persons WHERE id=?", (person_id,))
        self.cursor.execute("DELETE FROM scores WHERE student_id=?", (person_id,))
        self.conn.commit()
        messagebox.showinfo("成功", "个人信息及关联成绩已删除")
        self.search_persons()

    # 成绩操作方法
    def add_score(self):
        try:
            id = self.student_id_entry.get()
            subject = self.subject_entry.get()
            score = float(self.score_entry.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return

        self.cursor.execute(
            "INSERT INTO scores (student_id, subject, score) VALUES (?, ?, ?)",
            (id, subject, score)
        )
        self.conn.commit()
        messagebox.showinfo("成功", "成绩添加成功")
        self.clear_score_entries()
        self.search_scores()

    def search_scores(self):
        self.score_tree.delete(*self.score_tree.get_children())
        student_id = self.student_id_entry.get()
        query = "SELECT * FROM scores"
        params = ()

        if student_id:
            query += " WHERE student_id LIKE ?"
            params = (f"%{student_id}%",)

        self.cursor.execute(query, params)
        for row in self.cursor.fetchall():
            self.score_tree.insert("", END, values=row)
    
    def update_scores(self):
        student_id = self.student_id_entry.get()
        if not student_id:
            messagebox.showerror("错误", "请输入要更新的学号")
            return

        self.cursor.execute("SELECT * FROM scores WHERE student_id=?", (student_id,))
        original_record = self.cursor.fetchone()
        if not original_record:
            messagebox.showerror("错误", "未找到匹配的记录")
            return

        student_id = self.student_id_entry.get()
        subject = self.subject_entry.get()
        score = self.score_entry.get()

        new_subject = subject if subject else original_record[1]
        new_score = score if score else original_record[2]

        self.cursor.execute(
            "UPDATE scores SET subject=?, score=? WHERE student_id=?",
            (new_subject, new_score, student_id)
        )
        self.conn.commit()
        messagebox.showinfo("成功", "成绩信息更新成功")
        self.clear_score_entries()
        self.search_scores()


    def delete_score(self):
        selected = self.score_tree.selection()
        if not selected:
            messagebox.showerror("错误", "请先选择要删除的记录")
            return

        score_id = self.score_tree.item(selected[0])['values'][0]
        self.cursor.execute("DELETE FROM scores WHERE student_id=?", (score_id,))
        self.conn.commit()
        messagebox.showinfo("成功", "成绩记录已删除")
        self.search_scores()

    def clear_person_entries(self):
        self.id_entry.delete(0, END)
        self.name_entry.delete(0, END)
        self.gender_entry.delete(0, END)
        self.phone_entry.delete(0, END)
        self.email_entry.delete(0, END)

    def clear_score_entries(self):
        self.student_id_entry.delete(0, END)
        self.subject_entry.delete(0, END)
        self.score_entry.delete(0, END)

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = Tk()
    login_app = LoginWindow(root)
    root.mainloop()