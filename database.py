import sqlite3

# ----------------- INITIALISATION -----------------
def init_db():
    conn = sqlite3.connect("items.db")
    cur = conn.cursor()

    # Table des utilisateurs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)

    # Table des catégories
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)

    # Table des items
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category_id INTEGER,
            needed INTEGER,
            user_id INTEGER,
            FOREIGN KEY(category_id) REFERENCES categories(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# ----------------- UTILISATEURS -----------------
def add_user(name):
    conn = sqlite3.connect("items.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def get_users():
    conn = sqlite3.connect("items.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM users ORDER BY name")
    users = cur.fetchall()
    conn.close()
    return users
def rename_user(user_id, new_name):
    conn = sqlite3.connect("items.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET name = ? WHERE id = ?", (new_name, user_id))
    conn.commit()
    conn.close()


# ----------------- CATEGORIES -----------------
def add_category(name):
    conn = sqlite3.connect("items.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def get_categories():
    conn = sqlite3.connect("items.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM categories ORDER BY name")
    categories = cur.fetchall()
    conn.close()
    return categories


# ----------------- ITEMS -----------------
def add_item(name, category_id, needed, user_id):
    conn = sqlite3.connect("items.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO items (name, category_id, needed, user_id)
        VALUES (?, ?, ?, ?)
    """, (name, category_id, needed, user_id))
    conn.commit()
    conn.close()


def get_items(user_id, only_needed=False):
    conn = sqlite3.connect("items.db")
    cur = conn.cursor()

    if only_needed:
        cur.execute("""
            SELECT items.id, items.name, categories.name, items.needed
            FROM items
            JOIN categories ON items.category_id = categories.id
            WHERE items.needed = 1 AND items.user_id = ?
        """, (user_id,))
    else:
        cur.execute("""
            SELECT items.id, items.name, categories.name, items.needed
            FROM items
            JOIN categories ON items.category_id = categories.id
            WHERE items.user_id = ?
        """, (user_id,))

    items = cur.fetchall()
    conn.close()
    return items


def delete_item(item_id):
    conn = sqlite3.connect("items.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()


def toggle_needed(item_id):
    conn = sqlite3.connect("items.db")
    cur = conn.cursor()

    cur.execute("SELECT needed FROM items WHERE id = ?", (item_id,))
    current = cur.fetchone()[0]
    new_value = 0 if current == 1 else 1

    cur.execute("UPDATE items SET needed = ? WHERE id = ?", (new_value, item_id))
    conn.commit()
    conn.close()


def update_item_category(item_id, new_category_id):
    conn = sqlite3.connect("items.db")
    cur = conn.cursor()
    cur.execute("UPDATE items SET category_id = ? WHERE id = ?", (new_category_id, item_id))
    conn.commit()
    conn.close()


