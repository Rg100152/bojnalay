"""
Seed Bojnalay with 10 Indian & healthy recipes + a sample weekly thali plan.
Jaunpur / Purvanchal specials included with love.
Run: python3 seed_recipes.py
"""

import json
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "bojnalay.db")

RECIPES = [
    {
        "name": "Jaunpuri Imarti",
        "category": "Dessert",
        "cuisine": "Jaunpur Special",
        "description": "जौनपुर की मीठी इमरती — कुरकुरी, केसर-रंगी और त्योहारों की जान। एक छोटा सा उपहार अपने थाली के लिए।",
        "image": "food-chaat.jpg",
        "prep_time": 35,
        "calories": 290, "protein": 4, "carbs": 48, "fats": 9,
        "tags": "jaunpur,festive,sweet,imarti,local",
        "ingredients": [
            {"item": "Urad dal batter", "qty": "200 g", "category": "Grains & Flours"},
            {"item": "Sugar", "qty": "180 g", "category": "Spices & Condiments"},
            {"item": "Ghee", "qty": "3 tbsp", "category": "Dairy & Eggs"},
            {"item": "Saffron", "qty": "a pinch", "category": "Spices & Condiments"},
            {"item": "Cardamom powder", "qty": "1/2 tsp", "category": "Spices & Condiments"},
            {"item": "Rose water", "qty": "1 tsp", "category": "Spices & Condiments"},
        ],
        "steps": [
            "Urad dal को 4 घंटे भिगोकर बारीक पीस लें और फेंट लें।",
            "चीनी, केसर और गुलाबजल की हल्की चाशनी तैयार करें।",
            "बैटर को गरम घी में गोलाकार इमरती के रूप में डालकर सुनहरा तलें।",
            "तली हुई इमरती को चाशनी में 2 मिनट डुबाकर निकालें।",
            "इलायची पाउडर से सजाकर गरम परोसें।",
        ],
    },
    {
        "name": "Purvanchal Sattu Litti Chokha",
        "category": "Main Course",
        "cuisine": "Purvanchal",
        "description": "भुना हुआ सत्तू, धुआँदार चोखा और सरसों का तड़का — पूर्वांचल की मिट्टी की खुशबू हर कौर में।",
        "image": "food-curry.jpg",
        "prep_time": 45,
        "calories": 520, "protein": 22, "carbs": 68, "fats": 17,
        "tags": "purvanchal,litti,sattu,high-protein,local",
        "ingredients": [
            {"item": "Sattu flour", "qty": "250 g", "category": "Grains & Flours"},
            {"item": "Whole wheat atta", "qty": "150 g", "category": "Grains & Flours"},
            {"item": "Brinjal", "qty": "2 medium", "category": "Vegetables"},
            {"item": "Tomatoes", "qty": "3 medium", "category": "Vegetables"},
            {"item": "Potatoes", "qty": "2 medium", "category": "Vegetables"},
            {"item": "Mustard oil", "qty": "2 tbsp", "category": "Spices & Condiments"},
            {"item": "Garlic", "qty": "5 cloves", "category": "Vegetables"},
            {"item": "Green chili", "qty": "2", "category": "Vegetables"},
            {"item": "Coriander leaves", "qty": "1 handful", "category": "Vegetables"},
        ],
        "steps": [
            "सत्तू में प्याज़, लहसुन, हरी मिर्च, नींबू और सरसों का तेल मिलाकर भरावन तैयार करें।",
            "आटे के बने खोल में भरावन भरकर लिट्टी बनाएँ।",
            "लिट्टियों को कोयले या तवे पर धीरे-धीरे भून लें।",
            "बैंगन, टमाटर और आलू को आग पर सेंककर छीलें और मैश करें।",
            "चोखे में लहसुन-मिर्च-सरसों के तेल का तड़का लगाएँ।",
            "गरम लिट्टी को चोखे के साथ परोसें।",
        ],
    },
    {
        "name": "Shahi Paneer & Tandoori Roti Thali",
        "category": "Main Course",
        "cuisine": "North Indian",
        "description": "शाही पनीर, तंदूरी रोटी और रायते के साथ वो शाही थाली जो हर दिन को त्योहार बना दे।",
        "image": "food-paneer.jpg",
        "prep_time": 40,
        "calories": 610, "protein": 28, "carbs": 62, "fats": 26,
        "tags": "thali,paneer,shahi,royal,north-indian",
        "ingredients": [
            {"item": "Paneer", "qty": "250 g", "category": "Dairy & Eggs"},
            {"item": "Tomatoes", "qty": "4 medium", "category": "Vegetables"},
            {"item": "Onions", "qty": "2 medium", "category": "Vegetables"},
            {"item": "Cashews", "qty": "12", "category": "Fruits & Nuts"},
            {"item": "Whole wheat atta", "qty": "200 g", "category": "Grains & Flours"},
            {"item": "Curd", "qty": "100 g", "category": "Dairy & Eggs"},
            {"item": "Garam masala", "qty": "1 tsp", "category": "Spices & Condiments"},
            {"item": "Butter", "qty": "1 tbsp", "category": "Dairy & Eggs"},
        ],
        "steps": [
            "काजू और टमाटर को उबालकर मुलायम प्यूरी बना लें।",
            "प्याज़ को सुनहरा भूनें, उसमें टमाटर-काजू प्यूरी और मसाले डालें।",
            "ग्रेवी में पनीर के टुकड़े डालकर 8 मिनट पकाएँ, ऊपर से बटर डालें।",
            "आटे को दही से सानकर तंदूरी रोटी सेंक लें।",
            "शाही पनीर, रोटी और रायते के साथ शाही थाली सजाएँ।",
        ],
    },
    {
        "name": "Dal Tadka, Jeera Rice & Boondi Raita",
        "category": "Main Course",
        "cuisine": "North Indian",
        "description": "सुनहरा दाल तड़का, खुशबूदार जीरा राइस और ठंडा बूंदी रायता — रोज़मर्रा की परफेक्ट थाली।",
        "image": "food-curry.jpg",
        "prep_time": 30,
        "calories": 480, "protein": 18, "carbs": 72, "fats": 12,
        "tags": "dal,rice,thali,comfort,balanced",
        "ingredients": [
            {"item": "Toor dal", "qty": "200 g", "category": "Grains & Flours"},
            {"item": "Basmati rice", "qty": "200 g", "category": "Grains & Flours"},
            {"item": "Cumin seeds", "qty": "1 tsp", "category": "Spices & Condiments"},
            {"item": "Tomatoes", "qty": "2 medium", "category": "Vegetables"},
            {"item": "Onions", "qty": "1 medium", "category": "Vegetables"},
            {"item": "Curd", "qty": "150 g", "category": "Dairy & Eggs"},
            {"item": "Boondi", "qty": "50 g", "category": "Other"},
            {"item": "Turmeric", "qty": "1/2 tsp", "category": "Spices & Condiments"},
            {"item": "Ghee", "qty": "1 tbsp", "category": "Dairy & Eggs"},
        ],
        "steps": [
            "दाल को हल्दी के साथ उबालकर मैश करें।",
            "घी में जीरा, प्याज़ और टमाटर भूनकर दाल में तड़का लगाएँ।",
            "बासमती चावल को जीरा के साथ पकाएँ।",
            "दही में बूंदी, नमक और थोड़ा जीरा पाउडर मिलाकर रायता बनाएँ।",
            "तीनों को एक थाली में गरमागरम परोसें।",
        ],
    },
    {
        "name": "Sprouts & Roasted Makhana Chaat",
        "category": "Snack",
        "cuisine": "Healthy Indian",
        "description": "जौनपुर की मक्खना और ताज़ा स्प्राउट्स से हल्का, कुरकुरा और प्रोटीन से भरपूर चाट।",
        "image": "food-chaat.jpg",
        "prep_time": 15,
        "calories": 220, "protein": 9, "carbs": 28, "fats": 8,
        "tags": "makhana,sprouts,chaat,snack,protein",
        "ingredients": [
            {"item": "Mixed sprouts", "qty": "150 g", "category": "Vegetables"},
            {"item": "Makhana", "qty": "60 g", "category": "Fruits & Nuts"},
            {"item": "Cucumber", "qty": "1 small", "category": "Vegetables"},
            {"item": "Tomatoes", "qty": "1 medium", "category": "Vegetables"},
            {"item": "Lemon", "qty": "1", "category": "Fruits & Nuts"},
            {"item": "Chaat masala", "qty": "1 tsp", "category": "Spices & Condiments"},
            {"item": "Coriander leaves", "qty": "1 handful", "category": "Vegetables"},
        ],
        "steps": [
            "स्प्राउट्स को हल्का उबालकर ठंडा करें।",
            "मक्खना को थोड़े तेल में कुरकुरा भून लें।",
            "ककड़ी और टमाटर बारीक काट लें।",
            "सभी को नींबू, चाट मसाला और धनिये के साथ मिलाएँ।",
            "तुरंत परोसें ताकि कुरकुरापन बना रहे।",
        ],
    },
    {
        "name": "Paneer Tikka Bowl",
        "category": "Main Course",
        "cuisine": "Healthy Indian",
        "description": "दही-मसाले में मैरिनेटेड पनीर टिक्का, हरियागों और क्विनोआ के साथ एक आधुनिक बाउल।",
        "image": "food-bowl.jpg",
        "prep_time": 25,
        "calories": 430, "protein": 31, "carbs": 30, "fats": 20,
        "tags": "paneer,high-protein,bowl,grill",
        "ingredients": [
            {"item": "Paneer", "qty": "250 g", "category": "Dairy & Eggs"},
            {"item": "Curd", "qty": "100 g", "category": "Dairy & Eggs"},
            {"item": "Capsicum", "qty": "1 medium", "category": "Vegetables"},
            {"item": "Onions", "qty": "1 medium", "category": "Vegetables"},
            {"item": "Quinoa", "qty": "100 g", "category": "Grains & Flours"},
            {"item": "Garam masala", "qty": "1 tsp", "category": "Spices & Condiments"},
            {"item": "Olive oil", "qty": "1 tbsp", "category": "Spices & Condiments"},
            {"item": "Mint leaves", "qty": "1 handful", "category": "Vegetables"},
        ],
        "steps": [
            "पनीर, प्याज़ और शिमला मिर्च को क्यूब्स में काटें।",
            "दही, गरम मसाला और नमक में 20 मिनट मैरिनेट करें।",
            "तवे या ग्रिल पर टिक्के सुनहरे होने तक सेंकें।",
            "क्विनोआ को नमकीन पानी में पकाएँ।",
            "क्विनोआ बाउल में टिक्के रखकर पुदीने से सजाएँ।",
        ],
    },
    {
        "name": "Masala Oats",
        "category": "Breakfast",
        "cuisine": "Healthy Indian",
        "description": "सब्ज़ियों और मसालों से भरा गरमागरम नाश्ता — 15 मिनट में तैयार, दिन भर ऊर्जा देने वाला।",
        "image": "food-oats.jpg",
        "prep_time": 15,
        "calories": 310, "protein": 11, "carbs": 45, "fats": 9,
        "tags": "oats,breakfast,fiber,quick",
        "ingredients": [
            {"item": "Oats", "qty": "100 g", "category": "Grains & Flours"},
            {"item": "Carrot", "qty": "1 small", "category": "Vegetables"},
            {"item": "Green peas", "qty": "50 g", "category": "Vegetables"},
            {"item": "Onions", "qty": "1 small", "category": "Vegetables"},
            {"item": "Tomatoes", "qty": "1 medium", "category": "Vegetables"},
            {"item": "Turmeric", "qty": "1/4 tsp", "category": "Spices & Condiments"},
            {"item": "Cumin seeds", "qty": "1/2 tsp", "category": "Spices & Condiments"},
        ],
        "steps": [
            "थोड़े तेल में जीरा चटकाएँ, प्याज़ और सब्ज़ियाँ भूनें।",
            "ओट्स डालकर 2 मिनट भूनें फिर हल्दी और नमक डालें।",
            "पानी या दूध डालकर 6-8 मिनट पकाएँ।",
            "टमाटर और धनिये से सजाकर गरम परोसें।",
        ],
    },
    {
        "name": "Palak Paneer",
        "category": "Main Course",
        "cuisine": "North Indian",
        "description": "ताज़ी पालक की मलाईदार ग्रेवी में नरम पनीर — आयरन और प्रोटीन का हरा-भरा दोस्त।",
        "image": "food-paneer.jpg",
        "prep_time": 30,
        "calories": 390, "protein": 24, "carbs": 16, "fats": 26,
        "tags": "palak,paneer,iron,green",
        "ingredients": [
            {"item": "Spinach", "qty": "300 g", "category": "Vegetables"},
            {"item": "Paneer", "qty": "200 g", "category": "Dairy & Eggs"},
            {"item": "Onions", "qty": "1 medium", "category": "Vegetables"},
            {"item": "Tomatoes", "qty": "2 medium", "category": "Vegetables"},
            {"item": "Garlic", "qty": "4 cloves", "category": "Vegetables"},
            {"item": "Garam masala", "qty": "1 tsp", "category": "Spices & Condiments"},
            {"item": "Cream", "qty": "2 tbsp", "category": "Dairy & Eggs"},
        ],
        "steps": [
            "पालक को blanch करके ठंडा करें और मైश कर लें।",
            "प्याज़-टमाटर-लहसुन भूनकर मसालों के साथ पकाएँ।",
            "पालक प्यूरी डालकर 5 मिनट उबालें।",
            "पनीर और क्रीम डालकर 3 मिनट पकाएँ, गरम परोसें।",
        ],
    },
    {
        "name": "Ragi Dosa with Coconut Chutney",
        "category": "Breakfast",
        "cuisine": "South Indian",
        "description": "क्रिस्पी रागी दोसा और नारियल की चटनी — कैल्शियम से भरपूर एक हल्का, ग्लूटेन-फ्री नाश्ता।",
        "image": "food-dosa.jpg",
        "prep_time": 25,
        "calories": 280, "protein": 7, "carbs": 44, "fats": 9,
        "tags": "ragi,dosa,gluten-free,calcium",
        "ingredients": [
            {"item": "Ragi flour", "qty": "200 g", "category": "Grains & Flours"},
            {"item": "Rice flour", "qty": "50 g", "category": "Grains & Flours"},
            {"item": "Coconut", "qty": "100 g", "category": "Fruits & Nuts"},
            {"item": "Green chili", "qty": "1", "category": "Vegetables"},
            {"item": "Cumin seeds", "qty": "1/2 tsp", "category": "Spices & Condiments"},
            {"item": "Curry leaves", "qty": "6", "category": "Vegetables"},
        ],
        "steps": [
            "रागी, चावल का आटा और नमक में पानी मिलाकर हलवा बैटर बनाएँ।",
            "तवे पर पतला दोसा डालकर क्रिस्पी होने तक सेंकें।",
            "नारियल, हरी मिर्च और जीरा पीसकर चटनी बनाएँ।",
            "कर्री पत्तों का तड़का चटनी पर डालें।",
            "गरम दोसे को चटनी के साथ परोसें।",
        ],
    },
    {
        "name": "Quinoa Mint Power Bowl",
        "category": "Healthy Bowl",
        "cuisine": "Modern Healthy",
        "description": "क्विनोआ, हरी सब्ज़ियाँ, एवोकाडो और पुदीने की ताज़गी — कैलोरी कम, पोषण ज़्यादा।",
        "image": "food-salad.jpg",
        "prep_time": 20,
        "calories": 350, "protein": 14, "carbs": 42, "fats": 13,
        "tags": "quinoa,bowl,mint,low-calorie,vegan",
        "ingredients": [
            {"item": "Quinoa", "qty": "120 g", "category": "Grains & Flours"},
            {"item": "Lettuce", "qty": "1 handful", "category": "Vegetables"},
            {"item": "Cucumber", "qty": "1 small", "category": "Vegetables"},
            {"item": "Tomatoes", "qty": "1 medium", "category": "Vegetables"},
            {"item": "Mint leaves", "qty": "1 handful", "category": "Vegetables"},
            {"item": "Olive oil", "qty": "1 tbsp", "category": "Spices & Condiments"},
            {"item": "Lemon", "qty": "1", "category": "Fruits & Nuts"},
        ],
        "steps": [
            "क्विनोआ को धोकर नमकीन पानी में पकाएँ और ठंडा करें।",
            "सभी सब्ज़ियाँ बारीक काट लें।",
            "नींबू, ऑलिव ऑइल और पुदीने की ड्रेसिंग बनाएँ।",
            "बाउल में परतें सजाकर ऊपर ड्रेसिंग डालें।",
        ],
    },
]

# (day, slot, recipe index in the list above)
SAMPLE_PLAN = [
    ("Monday", "breakfast", 6), ("Monday", "lunch", 3),
    ("Monday", "snack", 4), ("Monday", "dinner", 2),
    ("Tuesday", "breakfast", 8), ("Tuesday", "lunch", 1),
    ("Tuesday", "snack", 4), ("Tuesday", "dinner", 7),
    ("Wednesday", "breakfast", 6), ("Wednesday", "lunch", 5),
    ("Wednesday", "snack", 0), ("Wednesday", "dinner", 9),
    ("Thursday", "breakfast", 8), ("Thursday", "lunch", 3),
    ("Thursday", "dinner", 2),
    ("Friday", "breakfast", 6), ("Friday", "lunch", 1),
    ("Friday", "snack", 4),
    ("Saturday", "lunch", 0),
]


def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            category TEXT NOT NULL, cuisine TEXT NOT NULL, description TEXT NOT NULL,
            image TEXT NOT NULL, prep_time INTEGER NOT NULL, calories REAL NOT NULL,
            protein REAL NOT NULL, carbs REAL NOT NULL, fats REAL NOT NULL,
            ingredients TEXT NOT NULL, steps TEXT NOT NULL, tags TEXT NOT NULL,
            is_custom INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS weekly_plan (
            id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT NOT NULL,
            slot TEXT NOT NULL, recipe_id INTEGER NOT NULL,
            UNIQUE(day, slot), FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS shopping_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT, item TEXT NOT NULL UNIQUE COLLATE NOCASE,
            qty TEXT NOT NULL, category TEXT NOT NULL, sources TEXT NOT NULL,
            checked INTEGER NOT NULL DEFAULT 0
        );
        """
    )

    existing = conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    if existing:
        print(f"ℹ️  Database already has {existing} recipes. Re-seeding base recipes (custom recipes kept).")
        conn.execute("DELETE FROM weekly_plan")
        conn.execute("DELETE FROM shopping_list")
        conn.execute("DELETE FROM recipes WHERE is_custom = 0")

    for recipe in RECIPES:
        conn.execute(
            """
            INSERT INTO recipes
              (name, category, cuisine, description, image, prep_time,
               calories, protein, carbs, fats, ingredients, steps, tags)
            VALUES (:name,:category,:cuisine,:description,:image,:prep_time,
                    :calories,:protein,:carbs,:fats,:ingredients,:steps,:tags)
            """,
            {**recipe, "ingredients": json.dumps(recipe["ingredients"]), "steps": json.dumps(recipe["steps"])},
        )

    recipe_ids = [row[0] for row in conn.execute("SELECT id FROM recipes WHERE is_custom = 0 ORDER BY id")]
    for day, slot, index in SAMPLE_PLAN:
        conn.execute(
            "INSERT OR REPLACE INTO weekly_plan (day, slot, recipe_id) VALUES (?,?,?)",
            (day, slot, recipe_ids[index]),
        )
    conn.commit()

    # Build the initial grocery list from the sample plan.
    merged = {}
    for _day, _slot, index in SAMPLE_PLAN:
        row = conn.execute("SELECT name, ingredients FROM recipes WHERE id = ?", (recipe_ids[index],)).fetchone()
        for ing in json.loads(row["ingredients"]):
            key = ing["item"].lower()
            if key not in merged:
                merged[key] = {**ing, "sources": set()}
            merged[key]["sources"].add(row["name"])
    conn.execute("DELETE FROM shopping_list")
    for value in merged.values():
        conn.execute(
            "INSERT INTO shopping_list (item, qty, category, sources) VALUES (?,?,?,?)",
            (value["item"], value["qty"], value["category"], ", ".join(sorted(value["sources"]))),
        )
    conn.commit()

    print(f"✅ Seeded {len(RECIPES)} recipes, {len(SAMPLE_PLAN)} planned meals and {len(merged)} grocery items.")
    print("🚀 Start the app with: python3 app.py")
    conn.close()


if __name__ == "__main__":
    main()
