import sqlite3

def ensure_user_id_column():
    conn = sqlite3.connect("items.db")
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(items)")
    columns = [col[1] for col in cur.fetchall()]

    if "user_id" not in columns:
        cur.execute("ALTER TABLE items ADD COLUMN user_id INTEGER;")
        cur.execute("UPDATE items SET user_id = 1;")
        conn.commit()

    conn.close()

ensure_user_id_column()

import streamlit as st

st.set_page_config(page_title="Liste d’achats", page_icon="🛒", layout="wide")

# ----------- STYLE MOBILE-FIRST + ONGLET EN BAS -----------
st.markdown("""
<style>
.block-container { padding-top: 1rem; padding-bottom: 6rem; }

/* Champs lisibles sur mobile */
input, select, textarea {
    font-size: 18px !important;
}

/* Boutons larges */
.stButton>button {
    width: 100%;
    border-radius: 10px;
    padding: 0.7rem 1rem;
    font-size: 18px;
}

/* Cartes d’items */
.item-card {
    padding: 0.8rem;
    background-color: #1e1e1e;
    border-radius: 12px;
    margin-bottom: 0.7rem;
}

/* Nom de l’item */
.item-name {
    font-size: 20px;
    font-weight: 600;
}

/* Icônes ✔️ et ❌ */
.icon-green {
    color: #4CAF50;
    font-size: 26px;
}
.icon-red {
    color: #FF4B4B;
    font-size: 26px;
}

/* Barre d’onglets en bas */
.bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background-color: #111;
    padding: 0.6rem 0;
    border-top: 1px solid #333;
    display: flex;
    justify-content: space-around;
    z-index: 9999;
}

.bottom-nav a {
    color: white;
    text-decoration: none;
    font-size: 16px;
    text-align: center;
}

.bottom-nav a:hover {
    color: #4CAF50;
}
</style>
""", unsafe_allow_html=True)

from database import (
    init_db,
    add_category,
    get_categories,
    add_item,
    get_items,
    delete_item,
    toggle_needed,
    update_item_category,
    add_user,
    get_users,
    rename_user
)

init_db()

# ----------------- CHOIX D'UTILISATEUR -----------------
st.sidebar.header("Utilisateur")

users = get_users()
user_names = [u[1] for u in users]

# Si aucun utilisateur, on en crée un par défaut
if not users:
    add_user("Utilisateur 1")
    users = get_users()
    user_names = [u[1] for u in users]

selected_user = st.sidebar.selectbox("Choisir un utilisateur", user_names)

# Trouver son ID
user_id = [u[0] for u in users if u[1] == selected_user][0]

st.sidebar.write("Renommer l'utilisateur")
new_name = st.sidebar.text_input("Nouveau nom", key="rename_user")

if st.sidebar.button("Renommer"):
    if new_name.strip():
        rename_user(user_id, new_name.strip())
        st.rerun()

# Ajouter un utilisateur
new_user = st.sidebar.text_input("Nouvel utilisateur")
if st.sidebar.button("Créer utilisateur"):
    if new_user.strip():
        add_user(new_user.strip())
        st.rerun()

# ----------------- ONGLET EN BAS -----------------
tabs = {
    "items": "📝 Items",
    "besoins": "❤️ Besoins",
    "categories": "📂 Catégories"
}

# Lecture de l’onglet courant via query params (fallback "items")
try:
    current_tab = st.query_params.get("tab", "items")
except Exception:
    current_tab = "items"

st.markdown(
    f"""
    <div class="bottom-nav">
        <a href="?tab=items">{tabs['items']}</a>
        <a href="?tab=besoins">{tabs['besoins']}</a>
        <a href="?tab=categories">{tabs['categories']}</a>
    </div>
    """,
    unsafe_allow_html=True
)

categories = get_categories()
cat_dict = {name: cid for cid, name in categories}

# ----------------- GESTION DES CATEGORIES -----------------
if current_tab == "categories":
    st.title("Gestion des catégories")

    new_cat = st.text_input("Nouvelle catégorie")
    if st.button("Ajouter"):
        if new_cat.strip():
            add_category(new_cat)
            st.success("Catégorie ajoutée !")
            st.rerun()

    st.subheader("Catégories existantes")
    for cid, name in categories:
        c1, c2 = st.columns([6, 1])
        with c1:
            st.write(name)
        with c2:
            if st.button("🗑️", key=f"del_cat_{cid}"):
                conn = sqlite3.connect("items.db")
                cur = conn.cursor()
                cur.execute("DELETE FROM items WHERE category_id = ?", (cid,))
                cur.execute("DELETE FROM categories WHERE id = ?", (cid,))
                conn.commit()
                conn.close()
                st.rerun()

# ----------------- GESTION DES ITEMS -----------------
elif current_tab == "items":
    st.title("Gestion de liste d’items")

    st.header("Ajouter un item")

    item_name = st.text_input(
        "Nom de l’item",
        value=st.session_state.get("item_name", "")
    )

    item_cat = st.selectbox("Catégorie", list(cat_dict.keys()))
    item_needed = st.checkbox("J’en ai besoin")

    if st.button("Ajouter item"):
        if item_name.strip():
            add_item(item_name, cat_dict[item_cat], 1 if item_needed else 0, user_id)
            st.session_state["item_name"] = ""
            st.rerun()

    st.header("Tous les items")
    st.write("---")

    # -------- TRI DES ITEMS --------
    tri_mode = st.selectbox(
        "Trier les items par",
        ["Alphabétique", "Ordre d’ajout", "Catégorie", "Besoin"]
    )

    all_items = get_items(user_id, only_needed=False)

    if tri_mode == "Alphabétique":
        all_items = sorted(all_items, key=lambda x: x[1].lower())
    elif tri_mode == "Catégorie":
        all_items = sorted(all_items, key=lambda x: x[2].lower())
    elif tri_mode == "Besoin":
        all_items = sorted(all_items, key=lambda x: x[3], reverse=True)

    # -------- AFFICHAGE DES ITEMS (MOBILE-FIRST) --------
    for iid, name, cat, needed in all_items:
        st.markdown('<div class="item-card">', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns([5, 2, 3, 1])

        with col1:
            st.markdown(f'<div class="item-name">{name}</div>', unsafe_allow_html=True)

        with col2:
            if st.button("✔️" if needed else "❌", key=f"toggle_{iid}"):
                toggle_needed(iid)
                st.rerun()

        with col3:
            new_cat = st.selectbox(
                "",
                list(cat_dict.keys()),
                index=list(cat_dict.keys()).index(cat),
                key=f"cat_select_{iid}"
            )
            if new_cat != cat:
                update_item_category(iid, cat_dict[new_cat])
                st.rerun()

        with col4:
            if st.button("🗑️", key=f"del_{iid}"):
                delete_item(iid)
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# ----------------- BESOINS PAR CATEGORIE -----------------
elif current_tab == "besoins":
    st.title("Besoins par catégorie")

    tri_mode = st.selectbox(
        "Mode de tri",
        ["Alphabétique", "Ordre d’ajout"]
    )

    needed_items = get_items(user_id, only_needed=True)

    grouped = {}
    for iid, name, cat, needed in needed_items:
        grouped.setdefault(cat, []).append((iid, name))

    if not grouped:
        st.info("Aucun item marqué comme 'Besoin'.")
    else:
        for cat, items in grouped.items():
            st.subheader(f"📂 {cat}")

            if tri_mode == "Alphabétique":
                items = sorted(items, key=lambda x: x[1])

            for iid, name in items:
                c1, c2 = st.columns([6, 1])
                with c1:
                    st.write(f"**{name}**")
                with c2:
                    if st.button("❌", key=f"need_toggle_{iid}"):
                        toggle_needed(iid)
                        st.rerun()
