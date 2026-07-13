from customtkinter import *
import threading
import random
from socket import *

set_appearance_mode("system")
set_default_color_theme("green")

class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("820x450")
        self.minsize(500, 300)
        self.title("LogiTalk")
        self.username = None
        self.sidebar_visible = True

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(10, weight=1)

        CTkLabel(self.sidebar, text="LogiTalk", font=CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=16, pady=(20, 16), sticky="w")

        CTkLabel(self.sidebar, text="Ваше ім'я", font=CTkFont(size=12)).grid(row=1, column=0, padx=16, pady=(0, 4), sticky="w")
        self.name_entry = CTkEntry(self.sidebar, placeholder_text="Ім'я")
        self.name_entry.grid(row=2, column=0, padx=16, pady=(0, 6), sticky="ew")
        CTkButton(self.sidebar, text="Змінити ім'я", command=self.rename).grid(row=3, column=0, padx=16, pady=(0, 20), sticky="ew")

        CTkLabel(self.sidebar, text="Тема", font=CTkFont(size=12)).grid(row=4, column=0, padx=16, pady=(0, 4), sticky="w")
        self.theme_menu = CTkOptionMenu(self.sidebar, values=["Темна", "Світла", "Системна"], command=self.change_theme)
        self.theme_menu.grid(row=5, column=0, padx=16, pady=(0, 0), sticky="ew")

        self.sidebar.grid_columnconfigure(0, weight=1)

        self.main_frame = CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.topbar = CTkFrame(self.main_frame, height=36, corner_radius=0)
        self.topbar.grid(row=0, column=0, sticky="new")
        self.topbar.grid_propagate(False)

        self.toggle_btn = CTkButton(self.topbar, text="☰", width=36, height=28, command=self.toggle_sidebar, fg_color="transparent", hover_color=("gray80", "gray30"), text_color=("gray20", "gray90"))
        self.toggle_btn.pack(side="left", padx=4, pady=4)

        self.chat_wrap = CTkFrame(self.main_frame, fg_color="transparent")
        self.chat_wrap.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 0))
        self.chat_wrap.grid_rowconfigure(0, weight=1)
        self.chat_wrap.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.chat_inner = CTkFrame(self.chat_wrap)
        self.chat_inner.grid(row=0, column=0, sticky="nsew")
        self.chat_inner.grid_rowconfigure(0, weight=1)
        self.chat_inner.grid_columnconfigure(0, weight=1)

        self.chat_text = CTkTextbox(self.chat_inner, wrap="word", activate_scrollbars=False)
        self.chat_text.insert("0.0", "Тут буде історія повідомлень...\n")
        self.chat_text.configure(state="disabled")
        self.chat_text.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = CTkScrollbar(self.chat_inner, command=self.chat_text.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_text.configure(yscrollcommand=self.scrollbar.set)

        self.bottom_frame = CTkFrame(self.main_frame, fg_color="transparent")
        self.bottom_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=8)
        self.bottom_frame.grid_columnconfigure(0, weight=1)

        self.message_input = CTkEntry(self.bottom_frame, placeholder_text="Введіть повідомлення...")
        self.message_input.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.message_input.bind("<Return>", lambda e: self.send_message())

        self.send_button = CTkButton(self.bottom_frame, text=">", width=40, command=self.send_message)
        self.send_button.grid(row=0, column=1)

        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(("localhost", 8080))
            name = self.name_entry.get().strip()
            if name:
                self.username = name
            else:
                self.username = f"Ви_{random.randint(1000, 9999)}"
                self.name_entry.insert(0, self.username)
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.sendall(hello.encode("utf-8"))
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            self.username = f"Ви_{random.randint(1000, 9999)}"
            self.name_entry.insert(0, self.username)
            self.add_message(f"[Помилка] Не вдалося підключитися до сервера: {e}")

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.grid_remove()
            self.sidebar_visible = False
        else:
            self.sidebar.grid()
            self.sidebar_visible = True

    def change_theme(self, value):
        if value == "Темна":
            set_appearance_mode("dark")
        elif value == "Світла":
            set_appearance_mode("light")
        else:
            set_appearance_mode("system")

    def send_message(self):
        message = self.message_input.get().strip()
        if message:
            full_message = f"[{self.username}]: {message}"
            self.add_message(full_message)
            try:
                self.sock.sendall(f"TEXT@{self.username}@{message}\n".encode("utf-8"))
            except:
                self.add_message("[Помилка] Повідомлення не надіслано.")
            self.message_input.delete(0, "end")

    def add_message(self, message):
        self.chat_text.configure(state="normal")
        self.chat_text.insert("end", message + "\n")
        self.chat_text.configure(state="disabled")
        self.chat_text.see("end")

    def receive_messages(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_server_message(line.strip())
            except:
                break
        self.sock.close()

    def handle_server_message(self, line):
        if not line:
            return
        self.add_message(line)

    def rename(self):
        new_name = self.name_entry.get().strip()
        if new_name and new_name != self.username:
            old_name = self.username
            self.username = new_name
            notice = f"TEXT@{self.username}@[SYSTEM] {old_name} змінив(ла) ім'я на {new_name}\n"
            try:
                self.sock.sendall(notice.encode("utf-8"))
                self.add_message(f"[СИСТЕМА] Ви змінили ім'я на {new_name}")
            except:
                self.add_message("[Помилка] Не вдалося надіслати повідомлення про зміну імені.")

win = MainWindow()
win.mainloop()