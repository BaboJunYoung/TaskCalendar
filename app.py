from flask import Flask, render_template, request, session, redirect, url_for
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24) # random.randint는 의사난수라네요

USERS = {
    "admin": {
        "password": "admin",
        # tasks의 키값은 날짜임!!
        "tasks": {
            1:[("가희 발싸하기", "red")],
            2:[("호빵 벌레하기", "red")],
            3:[("윤호현 벌레리나", "blue"), ("장한울 합성하기", "red")],
            4:[("퉁퉁퉁사후르", "red")]
        }
    }
}

# @app.route("/base")
# def base():
#     return render_template("base.html")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calendar")
def calendar():
    if "username" not in session: # 로그인 안되어있으면
        # return "로그인 후 사용해주세요"
        return render_template("please-login.html", current_page="calendar", title="Calendar")
    
    print(USERS)
    return render_template("calendar.html", tasks=USERS[session["username"]]["tasks"])

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET": return render_template("login.html")
    
    # 이 아래부턴 requset.method=="POST"

    username = request.form["username"]
    password = request.form["password"]
    

    if username in USERS.keys() and USERS[username]["password"] == password:
        # 로그인 성공
        session["username"] = username
        return redirect(url_for("calendar"))
    else:
        return render_template("login.html", error="유저이름 또는 비밀번호가 틀렸습니다.")
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "GET": return render_template("reset-password.html")

    username = request.form["username"]
    new_password = request.form["new-password"]
    
    # 보안이 많이 삐꾸지만 내 능력상 이게 한계임 ㅎㅋㅎㅋㅎㅋㅎㅋㅎ...
    if username in USERS.keys():
        USERS[username]["password"] = new_password
        return redirect(url_for("login"))
    else:
        return render_template("reset-password.html", error="유저를 찾을 수 없습니다.")
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET": return render_template("register.html")

    username = request.form["username"]
    password = request.form["password"]
    again_password = request.form["again-password"]

    if username in USERS:
        return render_template("register.html", error="이미 있는 유저이름입니다.")
    elif password != again_password:
        return render_template("register.html", error="비밀번호가 일치하지 않습니다.")
    
    # 계정 생성 성공
    USERS[username] = {"password": password, "tasks": {}}
    return redirect(url_for("login"))

@app.route("/today-tasks", methods=["GET", "POST"])
def today_tasks():
    if "username" not in session:
        return render_template("please-login.html", current_page="today-tasks", title="Today's tasks")
    
    now = datetime.now()
    if request.method == "POST":
        if 1 <= int(request.form["task-date"]) <= 30:
            now = now.replace(day=int(request.form["task-date"]))

    return render_template("today-tasks.html", \
        today_tasks=USERS[session["username"]]["tasks"].get(now.day, []),
        today=now.day
    )

@app.route("/today-tasks/<int:date>/<int:index>", methods=["POST"])
def delete_task(date, index):
    USERS[session["username"]]["tasks"][date].pop(index)
    return render_template("today-tasks.html", \
        today_tasks=USERS[session["username"]]["tasks"].get(date, []),
        today=date
    )
    #redirect(url_for("today_tasks"))
    

@app.route("/add-task", methods=["GET", "POST"])
def add_task():
    if "username" not in session: return render_template("please-login.html", current_page="add-task", title="Add task")
    if request.method == "GET": return render_template("add-task.html")

    task_date = int(request.form["task-date"])
    task_name = request.form["task-name"]
    color = request.form["color"]
    
    # 열심히 공부하기 green
    # print(task_name, color)
    
    if not(1 <= task_date <= 30):
        # 날짜가 나가버림!!
        return render_template("add-task.html", error="날짜를 다시 확인해주세요! (1일 ~ 30일)")

    if task_date not in USERS[session["username"]]["tasks"]:
        # 할일 목록에 이 날짜가 없음
        USERS[session["username"]]["tasks"][task_date] = [(task_name, color)]
    else:
        USERS[session["username"]]["tasks"][task_date].append((task_name, color))

    return render_template("add-task.html", complete="할 일 추가됨!!") #redirect(url_for("add_task"))
