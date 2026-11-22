"""
Bojnalay (भोजनालय) - Smart Meal Planner, Recipes & Nutrition Studio
Engineered by Raj Gautam | Jaunpur, Uttar Pradesh, India
Instagram: @linux.userraj | GitHub: github.com/Rg100152 | Email: graj13099@gmail.com

Flask + SQLite3 backend. No phone/contact number is stored or displayed anywhere.
"""

import csv
import io
import json
import os
import re
import sqlite3
from collections import defaultdict
from datetime import datetime
from flask import (
    Flask,
    Response,
    g,
    jsonify,
    render_template,
    request,
    send_from_directory,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "bojnalay.db")

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SLOTS = ["breakfast", "lunch", "snack", "dinner"]
TARGETS = {"calories": 2200, "protein": 110, "carbs": 260, "fats": 70}

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


def get_db():
    """Open a SQLite connection per request."""
    if "db" not in g:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        PRAGMA journal_mode = WAL;

        CREATE TABLE IF NOT EXISTS recipes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            category    TEXT NOT NULL DEFAULT 'Main Course',
            cuisine     TEXT NOT NULL DEFAULT 'Indian',
            description TEXT NOT NULL DEFAULT '',
            image       TEXT NOT NULL DEFAULT 'food-curry.jpg',
            prep_time   INTEGER NOT NULL DEFAULT 20,
            calories    REAL NOT NULL DEFAULT 0,
            protein     REAL NOT NULL DEFAULT 0,
            carbs       REAL NOT NULL DEFAULT 0,
            fats        REAL NOT NULL DEFAULT 0,
            ingredients TEXT NOT NULL DEFAULT '[]',
            steps       TEXT NOT NULL DEFAULT '[]',
            tags        TEXT NOT NULL DEFAULT '',
            is_custom   INTEGER NOT NULL DEFAULT 0,
            created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS weekly_plan (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            day       TEXT NOT NULL,
            slot      TEXT NOT NULL,
            recipe_id INTEGER NOT NULL,
            UNIQUE(day, slot),
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS shopping_list (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            item     TEXT NOT NULL UNIQUE COLLATE NOCASE,
            qty      TEXT NOT NULL DEFAULT '',
            category TEXT NOT NULL DEFAULT 'Other',
            sources  TEXT NOT NULL DEFAULT '',
            checked  INTEGER NOT NULL DEFAULT 0
        );
        """
    )
    conn.commit()
    conn.close()


init_db()


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def recipe_to_dict(row):
    data = dict(row)
    for key in ("ingredients", "steps"):
        try:
            data[key] = json.loads(data[key] or "[]")
        except (TypeError, ValueError):
            data[key] = []
    data["is_custom"] = bool(data.get("is_custom"))
    return data


def normalise_ingredient(value):
    """Accept either a string or {'item','qty','category'} and return dict."""
    if isinstance(value, dict):
        item = str(value.get("item", "")).strip()
        qty = str(value.get("qty", "")).strip()
        category = str(value.get("category", "")).strip() or guess_category(item)
    else:
        text = str(value).strip()
        if "—" in text:
            item, qty = text.split("—", 1)
            item, qty = item.strip(), qty.strip()
        elif " - " in text:
            item, qty = text.split(" - ", 1)
            item, qty = item.strip(), qty.strip()
        else:
            item, qty = text, ""
        category = guess_category(item)
    return {"item": item, "qty": qty, "category": category}


CATEGORY_HINTS = {
    "Dairy & Eggs": ("paneer", "milk", "curd", "yogurt", "ghee", "butter", "cheese", "egg", "raita", "buttermilk"),
    "Vegetables": ("tomato", "onion", "spinach", "palak", "potato", "brinjal", "baingan", "carrot", "cucumber", "coriander", "mint", "green chili", "ginger", "garlic", "capsicum", "peas", "lettuce", "sprout", "makhana"),
    "Grains & Flours": ("atta", "rice", "oat", "quinoa", "ragi", "sattu", "dal", "urad", "gram", "flour", "dosa", "bread", "roti", "vermicelli"),
    "Spices & Condiments": ("haldi", "turmeric", "cumin", "jeera", "coriander powder", "garam masala", "chili powder", "salt", "pepper", "cardamom", "saffron", "cinnamon", "mustard", "hing", "tempering", "tadka", "rose water", "sugar", "honey", "vinegar", "olive oil", "mustard oil", "oil"),
    "Fruits & Nuts": ("banana", "apple", "lemon", "lime", "almond", "cashew", "peanut", "coconut", "dates", "makhana"),
}


def guess_category(item):
    low = item.lower()
    for category, hints in CATEGORY_HINTS.items():
        if any(hint in low for hint in hints):
            return category
    return "Other"


def get_recipes():
    rows = get_db().execute("SELECT * FROM recipes ORDER BY is_custom DESC, id ASC").fetchall()
    return [recipe_to_dict(row) for row in rows]


def get_plan():
    rows = get_db().execute(
        """
        SELECT p.day, p.slot, p.recipe_id, r.name, r.image, r.calories,
               r.protein, r.carbs, r.fats, r.prep_time
        FROM weekly_plan p
        JOIN recipes r ON r.id = p.recipe_id
        """
    ).fetchall()
    plan = {}
    for row in rows:
        plan[f"{row['day']}|{row['slot']}"] = dict(row)
    return plan


def compute_totals(plan, day):
    totals = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fats": 0.0, "meals": 0}
    for slot in SLOTS:
        item = plan.get(f"{day}|{slot}")
        if not item:
            continue
        totals["meals"] += 1
        for key in totals:
            if key in ("calories", "protein", "carbs", "fats"):
                totals[key] += float(item[key] or 0)
    return {key: (round(value) if key != "meals" else value) for key, value in totals.items()}


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template(
        "index.html", days=DAYS, slots=SLOTS, targets=TARGETS,
        dev={
            "name": "Raj Gautam",
            "location": "Jaunpur, Uttar Pradesh, India",
            "email": "graj13099@gmail.com",
            "instagram": "@linux.userraj",
            "github": "https://github.com/Rg100152",
        },
    )


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static", "assets"),
        "logo-bojnalay.svg",
        mimetype="image/svg+xml",
    )


# --------------------------------------------------------------------------
# Recipe APIs
# --------------------------------------------------------------------------
@app.route("/api/recipes", methods=["GET"])
def list_recipes():
    recipes = get_recipes()
    search = (request.args.get("search") or "").strip().lower()
    category = (request.args.get("category") or "All").strip()
    if search:
        recipes = [
            r for r in recipes
            if search in r["name"].lower()
            or search in r["cuisine"].lower()
            or search in r["description"].lower()
            or search in " ".join(r["tags"].lower().split(","))
        ]
    if category and category != "All":
        recipes = [r for r in recipes if r["category"] == category]
    return jsonify({"recipes": recipes, "count": len(recipes)})


@app.route("/api/recipes", methods=["POST"])
def add_recipe():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Recipe name is required"}), 400

    def number(key, default=0):
        try:
            return max(0.0, float(payload.get(key) or default))
        except (TypeError, ValueError):
            return default

    ingredients_raw = payload.get("ingredients", [])
    if isinstance(ingredients_raw, str):
        ingredients_raw = [line for line in ingredients_raw.splitlines() if line.strip()]
    ingredients = [normalise_ingredient(i) for i in ingredients_raw if str(i).strip()]

    steps_raw = payload.get("steps", [])
    if isinstance(steps_raw, str):
        steps_raw = [line for line in steps_raw.splitlines() if line.strip()]
    steps = [str(s).strip() for s in steps_raw if str(s).strip()]

    conn = get_db()
    cur = conn.execute(
        """
        INSERT INTO recipes
          (name, category, cuisine, description, image, prep_time,
           calories, protein, carbs, fats, ingredients, steps, tags, is_custom)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,1)
        """,
        (
            name[:120],
            (payload.get("category") or "Main Course").strip()[:60],
            (payload.get("cuisine") or "Homemade").strip()[:60],
            (payload.get("description") or "A hand-added family favourite.").strip()[:600],
            (payload.get("image") or "food-bowl.jpg").strip()[:120],
            int(number("prep_time", 20)),
            number("calories"), number("protein"), number("carbs"), number("fats"),
            json.dumps(ingredients), json.dumps(steps),
            (payload.get("tags") or "custom").strip()[:200],
        ),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM recipes WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify({"message": "Recipe added to your vault", "recipe": recipe_to_dict(row)}), 201


# --------------------------------------------------------------------------
# Meal planner APIs
# --------------------------------------------------------------------------
@app.route("/api/plan", methods=["GET"])
def get_weekly_plan():
    plan = get_plan()
    totals = {day: compute_totals(plan, day) for day in DAYS}
    week = {
        key: round(sum(totals[day][key] for day in DAYS))
        for key in ("calories", "protein", "carbs", "fats")
    }
    return jsonify({"days": DAYS, "slots": SLOTS, "plan": plan, "totals": totals, "week": week})


@app.route("/api/plan", methods=["POST"])
def set_meal():
    payload = request.get_json(silent=True) or {}
    day = (payload.get("day") or "").strip()
    slot = (payload.get("slot") or "").strip().lower()
    if day not in DAYS or slot not in SLOTS:
        return jsonify({"error": "Invalid day or meal slot"}), 400

    conn = get_db()
    recipe_id = payload.get("recipe_id")
    if recipe_id in (None, "", 0, "0"):
        conn.execute("DELETE FROM weekly_plan WHERE day = ? AND slot = ?", (day, slot))
        conn.commit()
        return jsonify({"message": f"{slot.title()} cleared for {day}", "plan": get_plan()})

    try:
        recipe_id = int(recipe_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid recipe id"}), 400
    if not conn.execute("SELECT 1 FROM recipes WHERE id = ?", (recipe_id,)).fetchone():
        return jsonify({"error": "Recipe not found"}), 404

    conn.execute(
        """
        INSERT INTO weekly_plan (day, slot, recipe_id) VALUES (?,?,?)
        ON CONFLICT(day, slot) DO UPDATE SET recipe_id = excluded.recipe_id
        """,
        (day, slot, recipe_id),
    )
    conn.commit()
    return jsonify({"message": "Meal assigned", "plan": get_plan()})


@app.route("/api/plan", methods=["DELETE"])
def clear_plan():
    get_db().execute("DELETE FROM weekly_plan")
    get_db().commit()
    return jsonify({"message": "Weekly planner cleared"})


# --------------------------------------------------------------------------
# Nutrition APIs
# --------------------------------------------------------------------------
@app.route("/api/nutrition", methods=["GET"])
def nutrition():
    day = request.args.get("day") or DAYS[0]
    if day not in DAYS:
        day = DAYS[0]
    plan = get_plan()
    totals = compute_totals(plan, day)
    rings = {}
    for key, target in TARGETS.items():
        value = totals[key]
        rings[key] = {
            "value": value,
            "target": target,
            "percent": min(100, round(value / target * 100)) if target else 0,
            "unit": "kcal" if key == "calories" else "g",
        }
    return jsonify({"day": day, "totals": totals, "rings": rings, "targets": TARGETS})


# --------------------------------------------------------------------------
# Smart grocery list APIs
# --------------------------------------------------------------------------
def aggregate_ingredients():
    plan = get_plan()
    recipes = {r["id"]: r for r in get_recipes()}
    merged = {}
    for key, entry in plan.items():
        recipe = recipes.get(entry["recipe_id"])
        if not recipe:
            continue
        for raw in recipe["ingredients"]:
            ing = normalise_ingredient(raw)
            name = ing["item"].strip()
            if not name:
                continue
            norm = re.sub(r"\s+", " ", name.lower())
            if norm not in merged:
                merged[norm] = {
                    "item": name, "qty": ing["qty"],
                    "category": ing["category"], "sources": set(), "count": 0,
                }
            current = merged[norm]
            current["count"] += 1
            current["sources"].add(recipe["name"])
            if not current["qty"] and ing["qty"]:
                current["qty"] = ing["qty"]
            elif current["qty"] and ing["qty"] and current["qty"] != ing["qty"]:
                current["qty"] = f"{current['qty']} + {ing['qty']}"
    for value in merged.values():
        value["sources"] = ", ".join(sorted(value["sources"]))
    return merged


@app.route("/api/shopping", methods=["GET"])
def shopping_list():
    rows = get_db().execute(
        "SELECT id, item, qty, category, sources, checked FROM shopping_list ORDER BY category, item"
    ).fetchall()
    items = [dict(row) for row in rows]
    grouped = defaultdict(list)
    for item in items:
        grouped[item["category"]].append(item)
    return jsonify({
        "items": items,
        "grouped": grouped,
        "checked": sum(1 for i in items if i["checked"]),
        "total": len(items),
    })


@app.route("/api/shopping/generate", methods=["POST"])
def generate_shopping_list():
    conn = get_db()
    previous = {
        row["item"].lower(): row["checked"]
        for row in conn.execute("SELECT item, checked FROM shopping_list")
    }
    merged = aggregate_ingredients()
    conn.execute("DELETE FROM shopping_list")
    conn.executemany(
        """
        INSERT INTO shopping_list (item, qty, category, sources, checked)
        VALUES (?,?,?,?,?)
        """,
        [
            (
                v["item"], v["qty"], v["category"], v["sources"],
                previous.get(k, 0),
            )
            for k, v in merged.items()
        ],
    )
    conn.commit()
    return jsonify({
        "message": f"Grocery list ready with {len(merged)} items from your weekly thali",
        "count": len(merged),
    })


@app.route("/api/shopping/<int:item_id>", methods=["PATCH"])
def toggle_shopping_item(item_id):
    payload = request.get_json(silent=True) or {}
    checked = 1 if payload.get("checked") else 0
    conn = get_db()
    cur = conn.execute("UPDATE shopping_list SET checked = ? WHERE id = ?", (checked, item_id))
    conn.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "Item not found"}), 404
    return jsonify({"id": item_id, "checked": bool(checked)})


@app.route("/api/shopping/clear", methods=["POST"])
def clear_shopping_list():
    get_db().execute("DELETE FROM shopping_list")
    get_db().commit()
    return jsonify({"message": "Shopping list cleared"})


@app.route("/api/shopping/download", methods=["GET"])
def download_shopping_list():
    fmt = (request.args.get("format") or "txt").lower()
    rows = get_db().execute(
        "SELECT item, qty, category, checked FROM shopping_list ORDER BY category, item"
    ).fetchall()

    if fmt == "csv":
        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerow(["Item", "Quantity", "Category", "Status"])
        for row in rows:
            writer.writerow([
                row["item"], row["qty"], row["category"],
                "Bought" if row["checked"] else "Pending",
            ])
        return Response(
            stream.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=bojnalay-grocery-list.csv"},
        )

    lines = [
        "BOJNALAY • SMART GROCERY LIST",
        "Crafted in Jaunpur, Uttar Pradesh",
        "=" * 42,
        "",
    ]
    current_category = None
    for row in rows:
        if row["category"] != current_category:
            current_category = row["category"]
            lines.extend([f"[{current_category}]", "-" * len(current_category)])
        mark = "[x]" if row["checked"] else "[ ]"
        qty = f"  ({row['qty']})" if row["qty"] else ""
        lines.append(f"{mark} {row['item']}{qty}")
    lines.extend(["", "=" * 42, "Plan your thali. Track every calorie."])
    return Response(
        "\n".join(lines),
        mimetype="text/plain; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=bojnalay-grocery-list.txt"},
    )


@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "app": "Bojnalay",
        "recipes": get_db().execute("SELECT COUNT(*) FROM recipes").fetchone()[0],
        "meals": get_db().execute("SELECT COUNT(*) FROM weekly_plan").fetchone()[0],
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
