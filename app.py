from flask import Flask, render_template
import csv
import os

app = Flask(__name__)


def load_shift(filename):
    file_path = os.path.join(
        app.root_path,
        "data",
        filename
    )

    shifts = []

    with open(
        file_path,
        "r",
        encoding="utf-8-sig"
    ) as f:

        reader = csv.reader(f)

        rows = list(reader)

        # 1行目：タイトル
        # 2行目：見出し
        # 3行目以降：シフト
        for row in rows[2:]:

            if len(row) < 5:
                continue

            shift = {
                "time": row[0],

                "cooking": split_members(row[1]),

                "register": split_members(row[2]),

                "service": split_members(row[3]),

                "calling": split_members(row[4])
            }

            shifts.append(shift)

    return shifts


def split_members(text):
    if not text:
        return []

    return [
        name.strip()
        for name in text.split("/")
        if name.strip()
    ]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin")
def admin():
    return "管理者画面はこれから作成します"


@app.route("/viewer")
def viewer():

    day1 = load_shift(
        "ACEDOGS_10-10.csv"
    )

    day2 = load_shift(
        "ACEDOGS_10-11.csv"
    )

    return render_template(
        "viewer.html",
        day1=day1,
        day2=day2
    )


if __name__ == "__main__":
    app.run(
        debug=True,
        port=8081
    )