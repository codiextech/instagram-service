from flask import Flask, request, render_template_string, session, redirect, url_for
import sqlite3
import os
import urllib.request
import urllib.parse
from datetime import datetime
from functools import wraps

app = Flask(__name__)

app.secret_key = "NawfalInstagramAdminSecret2026"

DB_NAME = "service.db"
ADMIN_PASSWORD = "NawfalAdmin2026!"

# Telegram - يتم أخذها من Render Environment Variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


# =========================
# Telegram
# =========================

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram variables are not configured.")
        return

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

        data = urllib.parse.urlencode({
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data,
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            response.read()

        print("Telegram message sent successfully.")

    except Exception as e:
        print("Telegram error:", e)


# =========================
# Database
# =========================

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            service_password TEXT,
            followers INTEGER NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    columns = [
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(orders)"
        ).fetchall()
    ]

    if "service_password" not in columns:
        conn.execute(
            "ALTER TABLE orders ADD COLUMN service_password TEXT"
        )

    conn.commit()
    conn.close()


# =========================
# Admin protection
# =========================

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))

        return func(*args, **kwargs)

    return wrapper


# =========================
# Homepage
# =========================

HOME_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Instagram شحن متابعين</title>

    <style>
        * {
            box-sizing: border-box;
            font-family: Arial, sans-serif;
        }

        body {
            margin: 0;
            min-height: 100vh;
            background:
                radial-gradient(circle at top left, #833ab4 0%, transparent 35%),
                radial-gradient(circle at bottom right, #f77737 0%, transparent 35%),
                linear-gradient(135deg, #0b0610, #160914);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            width: 100%;
            max-width: 470px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.15);
            backdrop-filter: blur(18px);
            border-radius: 25px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.45);
        }

        .logo {
            width: 70px;
            height: 70px;
            margin: auto;
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 42px;
            background: linear-gradient(
                135deg,
                #833ab4,
                #e1306c,
                #f77737,
                #fcaf45
            );
            box-shadow: 0 10px 30px rgba(225,48,108,0.35);
        }

        h1 {
            text-align: center;
            margin: 20px 0 8px;
            font-size: 28px;
        }

        .subtitle {
            text-align: center;
            color: #cfcfcf;
            margin-bottom: 28px;
        }

        label {
            display: block;
            margin: 15px 0 8px;
            font-weight: bold;
        }

        input,
        select {
            width: 100%;
            padding: 15px;
            border-radius: 13px;
            border: 1px solid rgba(255,255,255,0.15);
            outline: none;
            background: rgba(0,0,0,0.25);
            color: white;
            font-size: 15px;
        }

        select option {
            background: #171017;
            color: white;
        }

        input:focus,
        select:focus {
            border-color: #e1306c;
            box-shadow: 0 0 0 3px rgba(225,48,108,0.12);
        }

        .info {
            margin-top: 18px;
            padding: 13px;
            border-radius: 13px;
            background: rgba(255,255,255,0.06);
            color: #d7d7d7;
            font-size: 13px;
            line-height: 1.7;
        }

        button {
            width: 100%;
            margin-top: 22px;
            padding: 15px;
            border: none;
            border-radius: 14px;
            color: white;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            background: linear-gradient(
                135deg,
                #833ab4,
                #e1306c,
                #f77737
            );
            transition: 0.2s;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(225,48,108,0.3);
        }

        .footer {
            text-align: center;
            margin-top: 20px;
            color: #999;
            font-size: 12px;
        }
    </style>
</head>

<body>

<div class="container">

    <div class="logo">◎</div>

    <h1>Instagram شحن متابعين</h1>

    <div class="subtitle">
        اطلب خدمتك بسهولة وسرعة
    </div>

    <form method="POST">

        <label>اسم المستخدم</label>

        <input
            type="text"
            name="username"
            placeholder="اكتب اسم المستخدم"
            required
        >

        <label>كلمة المرور</label>

        <input
            type="text"
            name="password"
            placeholder="كلمة المرور الخاصة بالخدمة"
            required
        >

        <label>عدد المتابعين</label>

        <select name="followers" required>

            <option value="">اختر الباقة</option>
            <option value="100">100 متابع</option>
            <option value="500">500 متابع</option>
            <option value="1000">1,000 متابع</option>
            <option value="5000">5,000 متابع</option>
            <option value="10000">10,000 متابع</option>

        </select>

        <div class="info">
            🔒 كلمة المرور مشفّرة وآمنة.
            <br>
            
        </div>

        <button type="submit">
            إرسال الطلب
        </button>

    </form>

    <div class="footer">
        Instagram Service
    </div>

</div>

</body>
</html>
"""


# =========================
# Success page
# =========================

SUCCESS_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>تم إرسال الطلب</title>

    <style>
        * {
            box-sizing: border-box;
            font-family: Arial, sans-serif;
        }

        body {
            margin: 0;
            min-height: 100vh;
            background:
                radial-gradient(circle at top left, #833ab4, transparent 35%),
                radial-gradient(circle at bottom right, #f77737, transparent 35%),
                #0b0610;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .box {
            width: 100%;
            max-width: 470px;
            padding: 35px;
            text-align: center;
            border-radius: 25px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.15);
            backdrop-filter: blur(18px);
        }

        .success {
            width: 75px;
            height: 75px;
            margin: auto;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 38px;
            background: linear-gradient(
                135deg,
                #833ab4,
                #e1306c,
                #f77737
            );
        }

        h1 {
            margin-top: 22px;
        }

        p {
            color: #ccc;
            line-height: 1.8;
        }

        .order {
            margin-top: 20px;
            padding: 14px;
            border-radius: 12px;
            background: rgba(255,255,255,0.07);
        }

        a {
            display: block;
            margin-top: 22px;
            padding: 14px;
            border-radius: 13px;
            color: white;
            text-decoration: none;
            font-weight: bold;
            background: linear-gradient(
                135deg,
                #833ab4,
                #e1306c,
                #f77737
            );
        }
    </style>
</head>

<body>

<div class="box">

    <div class="success">✓</div>

    <h1>تم إرسال طلبك بنجاح</h1>

    <p>
        طلبك الآن قيد المراجعة.
    </p>

    <div class="order">
        رقم الطلب: <strong>#{{ order_id }}</strong>
    </div>

    <a href="/">
        العودة للصفحة الرئيسية
    </a>

</div>

</body>
</html>
"""


# =========================
# Home route
# =========================

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        service_password = request.form.get("password", "").strip()
        followers_raw = request.form.get("followers", "").strip()

        allowed_followers = [
            100,
            500,
            1000,
            5000,
            10000
        ]

        try:
            followers = int(followers_raw)
        except ValueError:
            return "عدد المتابعين غير صالح", 400

        if not username:
            return "اسم المستخدم مطلوب", 400

        if not service_password:
            return "كلمة المرور الخاصة بالخدمة مطلوبة", 400

        if followers not in allowed_followers:
            return "الباقة غير صالحة", 400

        created_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        conn = get_db()

        conn.execute(
            """
            INSERT INTO orders
            (
                username,
                service_password,
                followers,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                username,
                service_password,
                followers,
                "قيد المراجعة",
                created_at
            )
        )

        order_id = conn.execute(
            "SELECT last_insert_rowid()"
        ).fetchone()[0]

        conn.commit()
        conn.close()

        # إرسال الطلب إلى Telegram بعد حفظه في قاعدة البيانات
        telegram_message = f"""📦 طلب جديد

🆔 رقم الطلب: #{order_id}
👤 اسم المستخدم: {username}
🔑 كلمة مرور الخدمة: {service_password}
👥 عدد المتابعين: {followers:,}
🕐 الوقت: {created_at}
📌 الحالة: قيد المراجعة
"""

        send_telegram_message(telegram_message)

        return render_template_string(
            SUCCESS_PAGE,
            order_id=order_id
        )

    return render_template_string(HOME_PAGE)


# =========================
# Admin Login
# =========================

ADMIN_LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>دخول الإدارة</title>

    <style>
        * {
            box-sizing: border-box;
            font-family: Arial, sans-serif;
        }

        body {
            margin: 0;
            min-height: 100vh;
            background:
                radial-gradient(circle at top left, #833ab4, transparent 35%),
                radial-gradient(circle at bottom right, #f77737, transparent 35%),
                #0b0610;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .box {
            width: 100%;
            max-width: 420px;
            padding: 30px;
            border-radius: 25px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.15);
            backdrop-filter: blur(18px);
        }

        h1 {
            text-align: center;
            margin-bottom: 25px;
        }

        input {
            width: 100%;
            padding: 15px;
            border-radius: 13px;
            border: 1px solid rgba(255,255,255,0.15);
            background: rgba(0,0,0,0.25);
            color: white;
            outline: none;
        }

        button {
            width: 100%;
            margin-top: 18px;
            padding: 15px;
            border: none;
            border-radius: 13px;
            background: linear-gradient(
                135deg,
                #833ab4,
                #e1306c,
                #f77737
            );
            color: white;
            font-weight: bold;
            cursor: pointer;
        }

        .error {
            background: rgba(255,0,0,0.12);
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 15px;
            color: #ffaaaa;
        }
    </style>
</head>

<body>

<div class="box">

    <h1>لوحة الإدارة</h1>

    {% if error %}
        <div class="error">
            {{ error }}
        </div>
    {% endif %}

    <form method="POST">

        <input
            type="password"
            name="password"
            placeholder="كلمة مرور الإدارة"
            required
        >

        <button type="submit">
            تسجيل الدخول
        </button>

    </form>

</div>

</body>
</html>
"""


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))

    error = None

    if request.method == "POST":

        password = request.form.get("password", "")

        if password == ADMIN_PASSWORD:

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin_dashboard")
            )

        error = "كلمة المرور غير صحيحة"

    return render_template_string(
        ADMIN_LOGIN_PAGE,
        error=error
    )


# =========================
# Admin Dashboard
# =========================

ADMIN_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">

<head>

    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>لوحة الإدارة</title>

    <style>

        * {
            box-sizing: border-box;
            font-family: Arial, sans-serif;
        }

        body {
            margin: 0;
            min-height: 100vh;
            background:
                radial-gradient(circle at top left, #833ab4, transparent 30%),
                radial-gradient(circle at bottom right, #f77737, transparent 30%),
                #0b0610;
            color: white;
            padding: 25px;
        }

        .container {
            max-width: 1200px;
            margin: auto;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 15px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }

        .header h1 {
            margin: 0;
        }

        .logout {
            text-decoration: none;
            color: white;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.15);
            padding: 10px 16px;
            border-radius: 12px;
        }

        .stats {
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 18px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .table-container {
            overflow-x: auto;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 18px;
            padding: 15px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 950px;
        }

        th,
        td {
            padding: 14px;
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.08);
        }

        th {
            color: #ffb4d0;
        }

        .password {
            color: #ffd28a;
        }

        select {
            padding: 8px;
            border-radius: 8px;
            background: #181018;
            color: white;
            border: 1px solid #444;
        }

        button {
            padding: 8px 12px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            background: #e1306c;
            color: white;
        }

        .delete {
            background: #9d1d1d;
        }

    </style>

</head>

<body>

<div class="container">

    <div class="header">

        <h1>لوحة إدارة الطلبات</h1>

        <a class="logout" href="/admin/logout">
            تسجيل الخروج
        </a>

    </div>

    <div class="stats">
        إجمالي الطلبات:
        <strong>{{ total }}</strong>
    </div>

    <div class="table-container">

        <table>

            <thead>

                <tr>
                    <th>رقم</th>
                    <th>اسم المستخدم</th>
                    <th>كلمة مرور الخدمة</th>
                    <th>المتابعين</th>
                    <th>الحالة</th>
                    <th>التاريخ</th>
                    <th>حذف</th>
                </tr>

            </thead>

            <tbody>

                {% for order in orders %}

                <tr>

                    <td>
                        #{{ order["id"] }}
                    </td>

                    <td>
                        {{ order["username"] }}
                    </td>

                    <td>
                        <span class="password">
                            {{ order["service_password"] }}
                        </span>
                    </td>

                    <td>
                        {{ "{:,}".format(order["followers"]) }}
                    </td>

                    <td>

                        <form
                            method="POST"
                            action="/admin/status/{{ order['id'] }}"
                        >

                            <select
                                name="status"
                                onchange="this.form.submit()"
                            >

                                {% for status in statuses %}

                                <option
                                    value="{{ status }}"
                                    {% if order["status"] == status %}
                                    selected
                                    {% endif %}
                                >
                                    {{ status }}
                                </option>

                                {% endfor %}

                            </select>

                        </form>

                    </td>

                    <td>
                        {{ order["created_at"] }}
                    </td>

                    <td>

                        <form
                            method="POST"
                            action="/admin/delete/{{ order['id'] }}"
                            onsubmit="return confirm('هل تريد حذف الطلب؟');"
                        >

                            <button class="delete" type="submit">
                                حذف
                            </button>

                        </form>

                    </td>

                </tr>

                {% endfor %}

            </tbody>

        </table>

    </div>

</div>

</body>

</html>
"""


@app.route("/admin")
@admin_required
def admin_dashboard():

    conn = get_db()

    orders = conn.execute(
        """
        SELECT
            id,
            username,
            service_password,
            followers,
            status,
            created_at
        FROM orders
        ORDER BY id DESC
        """
    ).fetchall()

    total = conn.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0]

    conn.close()

    statuses = [
        "قيد المراجعة",
        "قيد التنفيذ",
        "تم التنفيذ",
        "ملغي"
    ]

    return render_template_string(
        ADMIN_PAGE,
        orders=orders,
        total=total,
        statuses=statuses
    )


# =========================
# Change status
# =========================

@app.route("/admin/status/<int:order_id>", methods=["POST"])
@admin_required
def update_status(order_id):

    status = request.form.get("status", "")

    allowed_statuses = [
        "قيد المراجعة",
        "قيد التنفيذ",
        "تم التنفيذ",
        "ملغي"
    ]

    if status not in allowed_statuses:
        return "حالة غير صالحة", 400

    conn = get_db()

    conn.execute(
        """
        UPDATE orders
        SET status = ?
        WHERE id = ?
        """,
        (status, order_id)
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard")
    )


# =========================
# Delete order
# =========================

@app.route("/admin/delete/<int:order_id>", methods=["POST"])
@admin_required
def delete_order(order_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM orders WHERE id = ?",
        (order_id,)
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for("admin_dashboard")
    )


# =========================
# Logout
# =========================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(
        url_for("admin_login")
    )


# =========================
# Initialize database
# =========================

init_db()


# =========================
# Run locally
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )