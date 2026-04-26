import threading
from socket import *
from customtkinter import *

set_appearance_mode("dark")
set_default_color_theme("blue")


class ChatClient(CTk):
    def __init__(self):
        super().__init__()

        self.geometry("500x400")
        self.title("Chat")

        self.username = "User1"

        # 🚫 запрещённые слова
        self.banned_words = [
            "67",
            "простофиля",
            "брейнот",
            "сикс севен"
        ]

        # ===== CHAT =====
        self.chat = CTkTextbox(self, state="disabled", wrap="word")
        self.chat.pack(fill="both", expand=True, padx=10, pady=10)

        # ===== INPUT =====
        self.entry = CTkEntry(self, placeholder_text="Введіть повідомлення")
        self.entry.pack(fill="x", padx=10, pady=(0, 10))
        self.entry.bind("<Return>", lambda e: self.send())

        self.btn = CTkButton(self, text="Відправити", command=self.send)
        self.btn.pack(pady=(0, 10))

        # ===== SOCKET =====
        self.connected = False

        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(("localhost", 1111))
            self.connected = True

            threading.Thread(target=self.receive, daemon=True).start()

        except Exception as e:
            self.add(f"[ERROR] {e}")

    # ================= FILTER =================

    def filter_text(self, text):
        for word in self.banned_words:
            text = text.replace(word, "######")
            text = text.replace(word.capitalize(), "######")
            text = text.replace(word.upper(), "######")
        return text

    # ================= UI =================

    def add(self, text):
        self.chat.configure(state="normal")
        self.chat.insert("end", text + "\n")
        self.chat.configure(state="disabled")
        self.chat.yview("end")

    # ================= SEND =================

    def send(self):
        msg = self.entry.get()
        if not msg:
            return

        msg = self.filter_text(msg)

        if not self.connected:
            self.add("[NOT CONNECTED]")
            return

        try:
            data = f"TEXT@{self.username}@{msg}\n"
            self.sock.sendall(data.encode())

            self.entry.delete(0, "end")

        except Exception as e:
            self.add(f"[SEND ERROR] {e}")

    # ================= RECEIVE =================

    def receive(self):
        buffer = ""

        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break

                buffer += data.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle(line.strip())

            except:
                break

    # ================= HANDLE =================

    def handle(self, line):
        if not line:
            return

        parts = line.split("@", 2)

        if parts[0] == "TEXT" and len(parts) == 3:
            author = parts[1]
            msg = parts[2]

            # 👉 только username, без "You"
            self.add(f"{author}: {msg}")
        else:
            self.add(line)


app = ChatClient()
app.mainloop()