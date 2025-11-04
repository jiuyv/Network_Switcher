from functions import login, logout

import threading
import tkinter as tk
from tkinter import ttk, messagebox
import time
import json
import sys
from pathlib import Path

def run_in_thread(fn, args, on_done):
    def target():
        try:
            res = fn(*args)
            on_done(result=res, error=None)
        except Exception as e:
            on_done(result=None, error=e)

    threading.Thread(target=target, daemon=True).start()

class NetworkSwitcherGUI:
    def __init__(self, root):
        self.root = root
        root.title("Network Switcher")
        root.geometry("300x160")

        main_frm = ttk.Frame(root, padding=12)
        main_frm.pack(fill=tk.BOTH, expand=True)

        creds_frm = ttk.Frame(main_frm)
        creds_frm.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(creds_frm, text="账   号:").grid(row=0, column=0, sticky=tk.E)
        self.entry_user = ttk.Entry(creds_frm, width=25)
        self.entry_user.grid(row=0, column=1, padx=6, pady=4)

        ttk.Label(creds_frm, text="密   码:").grid(row=1, column=0, sticky=tk.E)
        self.entry_pass = ttk.Entry(creds_frm, width=25, show="*")
        self.entry_pass.grid(row=1, column=1, padx=6, pady=4)

        isp_choices = [("校园网", "0"), ("中国电信", "1"), ("中国联通", "2"), ("中国移动", "3")]
        self.isp_menu = ttk.Combobox(creds_frm, values=[t[0] for t in isp_choices], state="readonly", width=10)
        self.isp_menu.current(0)
        ttk.Label(creds_frm, text="运营商:").grid(row=2, column=0, sticky=tk.E)
        self.isp_menu.grid(row=2, column=1, padx=6, pady=4, columnspan=3, sticky=tk.W)
        self._isp_map = {name: val for (name, val) in isp_choices}
        self._isp_rev_map = {val: name for (name, val) in isp_choices}

        if getattr(sys, 'frozen', False):
            base_dir = Path(sys.argv[0]).resolve().parent
        else:
            base_dir = Path(__file__).parent
        self._cred_file = base_dir / 'credentials.json'

        self.remember_var = tk.BooleanVar(value=True)
        self.remember_cb = ttk.Checkbutton(creds_frm, text='记住账号', variable=self.remember_var)
        self.remember_cb.grid(row=2, column=1, sticky=tk.E, padx=0, pady=4)

        self._load_saved_credentials()

        btn_frm = ttk.Frame(main_frm)
        btn_frm.pack(fill=tk.X)

        self.btn_login = ttk.Button(btn_frm, text="登录", command=self.on_login)
        self.btn_login.pack(side=tk.LEFT, padx=(0,8))
        self.btn_logout = ttk.Button(btn_frm, text="注销", command=self.on_logout)
        self.btn_logout.pack(side=tk.LEFT)
        self.btn_logout_login = ttk.Button(btn_frm, text="注销并登录", command=self.on_logout_then_login)
        self.btn_logout_login.pack(side=tk.LEFT, padx=(8,0))

        self._set_buttons_state(normal=True)

    def _set_buttons_state(self, normal=True):
        state = tk.NORMAL if normal else tk.DISABLED
        self.btn_login.config(state=state)
        self.btn_logout.config(state=state)
        self.btn_logout_login.config(state=state)

    def _save_credentials(self, username: str, password: str, way: str):
        data = {"username": username, "password": password, "way": str(way)}
        with open(self._cred_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)

    def _load_saved_credentials(self):
        if self._cred_file.exists():
            with open(self._cred_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            username = data.get('username')
            password = data.get('password')
            way = str(data.get('way', '0'))
            if username:
                self.entry_user.delete(0, tk.END)
                self.entry_user.insert(0, username)
            if password:
                self.entry_pass.delete(0, tk.END)
                self.entry_pass.insert(0, password)
            display = self._isp_rev_map.get(way)
            if display:
                vals = list(self._isp_map.keys())
                idx = vals.index(display)
                self.isp_menu.current(idx)

    def on_done(self, result, error, op):
        def ui_update():
            if error:
                messagebox.showerror("调用错误", "调用失败，请稍后重试。")
            else:
                if op == 'login':
                    if getattr(self, 'remember_var', None) and self.remember_var.get():
                        self._save_credentials(self.entry_user.get().strip(), self.entry_pass.get().strip(), self._isp_map.get(self.isp_menu.get(), '0'))
                    messagebox.showinfo("成功", "登录成功")
                elif op == 'logout':
                    messagebox.showinfo("成功", "注销成功")
                else:
                    messagebox.showinfo("完成", "操作完成")
            self._set_buttons_state(normal=True)

        self.root.after(0, ui_update)

    def on_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        isp_display = self.isp_menu.get()
        way = self._isp_map.get(isp_display, "0")

        self._set_buttons_state(normal=False)

        def done_cb(result, error):
            self.on_done(result, error, op='login')

        run_in_thread(login, (username, password, way), done_cb)

    def on_logout(self):
        self._set_buttons_state(normal=False)

        def done_cb(result, error):
            self.on_done(result, error, op='logout')

        run_in_thread(logout, (), done_cb)

    def on_logout_then_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        isp_display = self.isp_menu.get()
        way = self._isp_map.get(isp_display, "0")

        def seq(user, pwd, wayv):
            logout()
            time.sleep(2)
            return login(user, pwd, wayv, pre_refresh=True)

        self._set_buttons_state(normal=False)

        def done_cb(result, error):
            self.on_done(result, error, op='login')

        run_in_thread(seq, (username, password, way), done_cb)

def GUI():
    root = tk.Tk()
    app = NetworkSwitcherGUI(root)
    root.mainloop()

if __name__ == "__main__":

    GUI()
