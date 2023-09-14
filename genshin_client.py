import requests,time,msvcrt,math,os
import tkinter as tk
#from colorama import init, Fore, Back, Style
SERVER_IP = '127.0.0.1'

class App:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(self.master, width=800, height=600)
        self.canvas.pack()
        self.angle = 0
        self.x, self.y = 400, 300

        # 初始化主体文本和旋转文本
        self.hero_text = self.canvas.create_text(self.x, self.y, text="XiangLing")
        self.orbit_text = self.canvas.create_text(self.x, self.y, text="FireBall")

        # 绑定键盘事件
        self.master.bind("<Key>", self.key_pressed)

        self.canvas.create_text(50, 20, text="Press Q to exit")

        self.update_orbit()
        
    def key_pressed(self, event):
        if event.char == 'w':
            self.y -= 10
        elif event.char == 's':
            self.y += 10
        elif event.char == 'a':
            self.x -= 10
        elif event.char == 'd':
            self.x += 10
        elif event.char == 'q':  # 回车键
            self.master.destroy()
            
        # 更新主体文本位置
        self.canvas.coords(self.hero_text, self.x, self.y)

    def update_orbit(self):
        # 更新旋转文本的位置
        r = 100
        orbit_x = r * math.cos(math.radians(self.angle)) + self.x
        orbit_y = r * math.sin(math.radians(self.angle)) + self.y
        self.canvas.coords(self.orbit_text, orbit_x, orbit_y)
        
        self.angle += 1
        if self.angle >= 360:
            self.angle = 0

        self.master.after(20, self.update_orbit)  # 每50毫秒更新一次位置

class SplashScreen:
    
    def show(self):
        with open('genshin_ascii_art.txt', 'r') as f:
            genshin_ascii_art = f.read()

        frames = ['-', '\\', '|', '/', '⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        #color_codes = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE]
        color_codes = color_codes = ['\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m', '\033[97m','\033[96m', '\033[95m', '\033[94m', '\033[93m', '\033[92m']
        print('\033[2J\033[H', end='', flush=True)
        try:
            while True:
                for  i, frame in enumerate(frames):
                    color_code = color_codes[i % len(color_codes)]
                    #os.system("cls")

                    print('\033[H', end='', flush=True)
                    print(f'{genshin_ascii_art}\n{color_code}{frame} 按任意键启动\033[0m', end='', flush=True)

                    time.sleep(0.1)
                    if msvcrt.kbhit():
                        msvcrt.getch() 
                        print('\033[2J\033[H', end='', flush=True)
                        return
        except KeyboardInterrupt:
            print('\033[2J\033[H', end='', flush=True)

class LoginSystem:
    def __init__(self,server_ip):
        self.server_ip = server_ip
    def login(self):
        username = input("请输入用户名：")
        password = input("请输入密码：")
        response = requests.post(f'http://{self.server_ip}:5000/login', json={'username': username, 'password': password})
        if response.status_code == 200:
            token = response.json().get('token')
            self.ask_save_token(token)
            return True
        return False

    def try_token_login(self):
        if os.path.exists('token.txt'):
            with open('token.txt', 'r') as f:
                token = f.read().strip()
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(f'http://{self.server_ip}:5000/verify_token', headers=headers)
            return response.status_code == 200
        return False

    def ask_save_token(self, token):  # 添加这个函数来询问用户是否保存 token
        choice = input("是否保存token用于自动登录? (y/n): ")
        if choice.lower() == 'y':
            with open('token.txt', 'w') as f:
                f.write(token)    

class DrawCardSystem:
    def __init__(self,server_ip):
        self.server_ip = server_ip

    def draw_card(self):
        with open('token.txt', 'r') as f:
            token = f.read()

        headers = {'Authorization': f'Bearer {token}'}
        response = requests.post(f'http://{self.server_ip}:5000/draw_card', headers=headers)
        return response.json()

if __name__ == '__main__':
    splash = SplashScreen()
    splash.show()

    login_flag = 0
    login_system = LoginSystem(SERVER_IP)
    draw_card_system = DrawCardSystem(SERVER_IP)

    if os.path.exists('token.txt'):
        choice = input("是否自动登录? (y/n): ")
        while choice not in ['y', 'n']:
            choice = input("是否自动登录? (y/n): ")
        if choice == 'n':
            login_flag = login_system.login()
        if choice == 'y':
            login_flag = login_system.try_token_login()

            if not login_flag:
                print("Token 登录失败，需要手动登录")
                login_flag = login_system.login()

    else:
        login_flag = login_system.login()

    if login_flag:
        while 1:
            user_action = input("请输入你要进行的操作：1.单抽 2.十连 3.香菱:\n")
            if (user_action == '1'):
                result = draw_card_system.draw_card()
                print(f"抽卡结果: {result}")
            if (user_action == '2'):
                for i in range(10):
                    result = draw_card_system.draw_card()
                    print(f"抽卡结果{i}: {result}")
            if (user_action == '3'):
                    root = tk.Tk()
                    app = App(root)
                    root.mainloop()
    else:
        print("登陆失败")
