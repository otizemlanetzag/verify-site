import os
import requests
from flask import Flask, render_template_string, request

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>בודק מחרוזת באתרים</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; text-align: center; background-color: #f4f4f9; }
        .container { max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        input[type="text"] { width: 80%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        .result { margin-top: 20px; padding: 15px; border-radius: 4px; font-weight: bold; }
        .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .fail { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <h2>בודק מחרוזת בקוד האתר</h2>
        <p>האפליקציה תחפש את המחרוזת מתוך הקובץ <strong>napo.txt</strong></p>
        
        <form method="POST">
            <input type="text" name="url" placeholder="הכנס כתובת URL (למשל https://example.com)" required>
            <br>
            <button type="submit">בדוק אתר</button>
        </form>

        {% if result %}
            <div class="result {{ 'success' if result.success else 'fail' }}">
                {{ result.message }}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        url = request.form.get("url")

        # הגדרת נתיב אבסולוטי לקובץ napo.txt שנמצא בתיקיית השורש של הפרויקט
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filename = os.path.join(base_dir, "napo.txt")

        if not os.path.exists(filename):
            result = {
                "success": False,
                "message": f"שגיאה: הקובץ 'napo.txt' לא נמצא בשרת.",
            }
        else:
            with open(filename, "r", encoding="utf-8") as file:
                search_string = file.read().strip()

            if not search_string:
                result = {
                    "success": False,
                    "message": "הקובץ 'napo.txt' ריק. אין מה לחפש.",
                }
            else:
                try:
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()

                    html_content_lower = response.text.lower()
                    search_string_lower = search_string.lower()

                    if search_string_lower in html_content_lower:
                        result = {
                            "success": True,
                            "message": f"✅ המחרוזת '{search_string}' נמצאה בקוד המקור של האתר!",
                        }
                    else:
                        result = {
                            "success": False,
                            "message": f"❌ המחרוזת '{search_string}' לא נמצאה בקוד המקור.",
                        }

                except requests.exceptions.RequestException as e:
                    result = {
                        "success": False,
                        "message": f"שגיאה בגישה לאתר: {str(e)}",
                    }

    return render_template_string(HTML_TEMPLATE, result=result)


# שים לב: הסרנו את app.run() כי Vercel מנהלת את ההרצה בעצמה
