from flask import Flask, request, jsonify
import jwt, random, sqlite3, datetime
import random

def one_draw(draw_count, four_star_flag, five_star_flag):
    # 初始化
    is_up = False
    star = 0
    
    # 五星保底逻辑
    if draw_count - five_star_flag[0] >= 90:
        star = 5
        is_up = five_star_flag[1] or random.choice([True, False])
        five_star_flag = [draw_count, not is_up]  # 更新五星标志位
        four_star_flag = draw_count  # 更新四星标志位
        return star, is_up, four_star_flag, five_star_flag
    
    # 四星保底逻辑
    if draw_count - four_star_flag >= 10:
        star = 4
        four_star_flag = draw_count  # 更新四星标志位
        return star, is_up, four_star_flag, five_star_flag
    
    # 计算五星概率
    if draw_count - five_star_flag[0] > 73:
        five_star_prob = 0.006 + 0.00036 * (draw_count - 73)
    else:
        five_star_prob = 0.006
    
    # 抽卡
    rand_num = random.random()
    if rand_num < five_star_prob:
        star = 5
        is_up = five_star_flag[1] or random.choice([True, False])
        five_star_flag = [draw_count, not is_up]  # 更新五星标志位
    elif rand_num < five_star_prob + 0.036:  # 假设四星出率是0.036（因为没有具体给出）
        star = 4
    else:
        star = 3
    
    # 更新四星和五星的标志位
    if star == 4:
        four_star_flag = draw_count
    elif star == 5:
        four_star_flag = draw_count
        five_star_flag = [draw_count, not is_up]

    return star, is_up, four_star_flag, five_star_flag

app = Flask(__name__)
SECRET_KEY = 'GenShin'

# 初始化数据库，创建用户表并插入一个测试用户
def initialize_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT, draw_count INTEGER, four_star_flag INTEGER, five_star_flag TEXT)''')
    c.execute("INSERT INTO users (username, password, draw_count, four_star_flag, five_star_flag) VALUES ('pzy1s', 'password', 0, 0, '0,False')")
    conn.commit()
    conn.close()

# 处理登录请求
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()

    # 判断用户是否存在，存在则生成JWT token
    if user:
        token = jwt.encode({'user': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=300)}, SECRET_KEY)
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

# 验证token是否有效
@app.route('/verify_token', methods=['GET'])
def verify_token():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            # 从"Bearer "后开始获取实际的token
            token = auth_header.split(" ")[1]
            # 验证 token
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return jsonify({'message': 'Token is valid'}), 200
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return jsonify({'message': 'Token is invalid'}), 401
    else:
        return jsonify({'message': 'Token is missing'}), 401

# 处理抽卡请求
@app.route('/draw_card', methods=['POST'])
def draw_card():
    token = request.headers.get('Authorization').split(" ")[1]
    data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    username = data.get('user')

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT draw_count, four_star_flag, five_star_flag FROM users WHERE username = ?", (username,))
    draw_count, four_star_flag, five_star_flag_str = c.fetchone()
    five_star_flag = [int(x) if i == 0 else x == 'True' for i, x in enumerate(five_star_flag_str.split(','))]
    
    # 调用抽卡函数，获取结果
    star, is_up, four_star_flag, five_star_flag = one_draw(draw_count, four_star_flag, five_star_flag)
    
    # 更新数据库的抽卡次数和标志位
    new_five_star_flag_str = f"{five_star_flag[0]},{five_star_flag[1]}"
    c.execute("UPDATE users SET draw_count = ?, four_star_flag = ?, five_star_flag = ? WHERE username = ?", (draw_count + 1, four_star_flag, new_five_star_flag_str, username))
    conn.commit()
    conn.close()

    # 返回结果
    return jsonify({'username': username, 'star': star, 'is_up': is_up})

if __name__ == '__main__':
    #initialize_db()  # 初始化数据库
    print('原神服务器已启动，端口：5000\n')
    app.run(port=5000)  # 启动服务器

