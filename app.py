import streamlit as st

st.set_page_config(page_title="Liste d’achats", page_icon="🛒")

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

# ----------------- NAVIGATION -----------------
page = st.sidebar.radio(
    "Navigation",
    ["Gestion des items", "Besoins par catégorie", "Gestion des catégories"]
)

categories = get_categories()
cat_dict = {name: cid for cid, name in categories}

# ----------------- GESTION DES CATEGORIES -----------------
if page == "Gestion des catégories":
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
                import sqlite3
                conn = sqlite3.connect("items.db")
                cur = conn.cursor()
                cur.execute("DELETE FROM items WHERE category_id = ?", (cid,))
                cur.execute("DELETE FROM categories WHERE id = ?", (cid,))
                conn.commit()
                conn.close()
                st.rerun()

# ----------------- GESTION DES ITEMS -----------------
elif page == "Gestion des items":
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

    # -------- AFFICHAGE DES ITEMS --------
    for iid, name, cat, needed in all_items:

        col1, col2, col3, col4 = st.columns([5, 2, 3, 1])

        with col1:
            st.write(f"**{name}**")

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

        with col4:
            if st.button("🗑️", key=f"del_{iid}"):
                delete_item(iid)
                st.rerun()

        st.write("")

# ----------------- BESOINS PAR CATEGORIE -----------------
elif page == "Besoins par catégorie":
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
