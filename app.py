from flask import Flask, render_template
import csv
import os

app = Flask(__name__)


def split_members(text):
    if not text:
        return []

    return [
        name.strip()
        for name in text.split("/")
        if name.strip()
    ]


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

        # 1行目は見出しなので飛ばす
        for row in rows[1:]:

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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin")
def admin():
    return "管理者画面はこれから作成します"


@app.route("/viewer")
def viewer():

    day1 = load_shift(
        "ACEDOGS_10-10_13人体制.csv"
    )

    day2 = load_shift(
        "ACEDOGS_10-11_13人体制2.csv"
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