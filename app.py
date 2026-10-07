from flask import Flask, render_template, request, redirect, url_for
import csv
import io
import os
import base64
import requests

app = Flask(__name__)


# =========================================
# SETTINGS
# =========================================

DAY1_FILE = "ACEDOGS_10-10_13人体制.csv"
DAY2_FILE = "ACEDOGS_10-11_13人体制2.csv"

GITHUB_OWNER = "atsuki0426"
GITHUB_REPO = "festival"
GITHUB_BRANCH = "main"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")


# =========================================
# CSV
# =========================================

def split_members(text):
    if not text:
        return []

    return [
        name.strip()
        for name in text.split("/")
        if name.strip()
    ]


def get_csv_path(filename):
    return os.path.join(
        app.root_path,
        "data",
        filename
    )


def load_shift(filename):
    file_path = get_csv_path(filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"CSVファイルが見つかりません: {file_path}"
        )

    shifts = []

    with open(
        file_path,
        "r",
        encoding="utf-8-sig"
    ) as f:

        reader = csv.reader(f)

        rows = list(reader)

        for row in rows[1:]:

            if not row:
                continue

            if len(row) < 5:
                continue

            shifts.append({
                "time": row[0],
                "cooking": split_members(row[1]),
                "register": split_members(row[2]),
                "service": split_members(row[3]),
                "calling": split_members(row[4])
            })

    return shifts


# =========================================
# FORM → CSV
# =========================================

def create_csv_text(form_data):
    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "時間",
        "調理（4）",
        "レジ＋カウント（2）",
        "提供＋調味料補充（3）",
        "呼び込み（4）"
    ])

    index = 0

    while True:

        time_key = f"time_{index}"

        if time_key not in form_data:
            break

        time = form_data.get(
            time_key,
            ""
        ).strip()

        cooking = form_data.get(
            f"cooking_{index}",
            ""
        ).strip()

        register = form_data.get(
            f"register_{index}",
            ""
        ).strip()

        service = form_data.get(
            f"service_{index}",
            ""
        ).strip()

        calling = form_data.get(
            f"calling_{index}",
            ""
        ).strip()

        writer.writerow([
            time,
            cooking,
            register,
            service,
            calling
        ])

        index += 1

    return output.getvalue()


# =========================================
# GITHUB API
# =========================================

def update_github_csv(filename, csv_text):

    if not GITHUB_TOKEN:
        raise RuntimeError(
            "GITHUB_TOKEN が設定されていません"
        )

    github_path = f"data/{filename}"

    api_url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_OWNER}/"
        f"{GITHUB_REPO}/contents/"
        f"{github_path}"
    )

    headers = {
        "Accept":
            "application/vnd.github+json",

        "Authorization":
            f"Bearer {GITHUB_TOKEN}",

        "X-GitHub-Api-Version":
            "2026-03-10"
    }

    # -------------------------------------
    # 現在のファイルSHAを取得
    # -------------------------------------

    response = requests.get(
        api_url,
        headers=headers,
        params={
            "ref": GITHUB_BRANCH
        },
        timeout=20
    )

    response.raise_for_status()

    file_info = response.json()

    current_sha = file_info["sha"]


    # -------------------------------------
    # CSVをBase64化
    # -------------------------------------

    csv_bytes = (
        "\ufeff" + csv_text
    ).encode("utf-8")

    encoded_content = (
        base64.b64encode(
            csv_bytes
        )
        .decode("utf-8")
    )


    # -------------------------------------
    # GitHub上のCSVを更新
    # -------------------------------------

    data = {
        "message":
            f"update {filename} from ACEDOGS admin",

        "content":
            encoded_content,

        "sha":
            current_sha,

        "branch":
            GITHUB_BRANCH
    }

    response = requests.put(
        api_url,
        headers=headers,
        json=data,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


# =========================================
# ROUTES
# =========================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


@app.route("/viewer")
def viewer():

    day1 = load_shift(
        DAY1_FILE
    )

    day2 = load_shift(
        DAY2_FILE
    )

    return render_template(
        "viewer.html",
        day1=day1,
        day2=day2
    )


@app.route("/admin")
def admin():

    day1 = load_shift(
        DAY1_FILE
    )

    day2 = load_shift(
        DAY2_FILE
    )

    return render_template(
        "admin.html",
        day1=day1,
        day2=day2
    )


# =========================================
# SAVE DAY 1
# =========================================

@app.route(
    "/admin/save/day1",
    methods=["POST"]
)
def save_day1():

    csv_text = create_csv_text(
        request.form
    )

    update_github_csv(
        DAY1_FILE,
        csv_text
    )

    return redirect(
        url_for("admin")
    )


# =========================================
# SAVE DAY 2
# =========================================

@app.route(
    "/admin/save/day2",
    methods=["POST"]
)
def save_day2():

    csv_text = create_csv_text(
        request.form
    )

    update_github_csv(
        DAY2_FILE,
        csv_text
    )

    return redirect(
        url_for("admin")
    )


# =========================================
# LOCAL
# =========================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=8081
    )