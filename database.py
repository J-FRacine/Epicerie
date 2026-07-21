import sqlite3

def get_connection():
    return sqlite3.connect("items.db")

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category_id INTEGER,
            needed INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)

    conn.commit()
    conn.close()

def add_category(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def get_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM categories")
    rows = cur.fetchall()
    conn.close()
    return rows

def add_item(name, category_id, needed):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO items (name, category_id, needed) VALUES (?, ?, ?)",
                (name, category_id, needed))
    conn.commit()
    conn.close()

def get_items(only_needed=False):
    conn = get_connection()
    cur = conn.cursor()
    if only_needed:
        cur.execute("""
            SELECT items.id, items.name, categories.name, items.needed
            FROM items
            JOIN categories ON items.category_id = categories.id
            WHERE items.needed = 1
        """)
    else:
        cur.execute("""
            SELECT items.id, items.name, categories.name, items.needed
            FROM items
            JOIN categories ON items.category_id = categories.id
        """)
    rows = cur.fetchall()
    conn.close()
    return rows

def delete_item(item_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def toggle_needed(item_id):
    conn = get_connection()
    cur = conn.cursor()

    # On récupère le statut actuel
    cur.execute("SELECT needed FROM items WHERE id = ?", (item_id,))
    current = cur.fetchone()[0]

    # On inverse : 1 → 0, 0 → 1
    new_value = 0 if current == 1 else 1

    cur.execute("UPDATE items SET needed = ? WHERE id = ?", (new_value, item_id))
    conn.commit()
    conn.close()

def update_item_category(item_id, new_category_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE items SET category_id = ? WHERE id = ?", (new_category_id, item_id))
    conn.commit()
    conn.close()
