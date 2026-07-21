st.set_page_config(page_title="Liste d’achats")

import streamlit as st
from database import (
    init_db,
    add_category,
    get_categories,
    add_item,
    get_items,
    delete_item,
    toggle_needed,
    update_item_category
)

init_db()

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

    # Champ texte SANS key → value contrôlée par session_state
    item_name = st.text_input(
        "Nom de l’item",
        value=st.session_state.get("item_name", "")
    )

    item_cat = st.selectbox("Catégorie", list(cat_dict.keys()))
    item_needed = st.checkbox("J’en ai besoin")

    if st.button("Ajouter item"):
        if item_name.strip():
            add_item(item_name, cat_dict[item_cat], 1 if item_needed else 0)

            # Vider le champ proprement
            st.session_state["item_name"] = ""

            st.rerun()

    st.header("Tous les items")
    st.write("---")

    # -------- TRI DES ITEMS --------
    tri_mode = st.selectbox(
        "Trier les items par",
        ["Alphabétique", "Catégorie", "Besoin","Ordre d’ajout"]
    )

    all_items = get_items(only_needed=False)

    if tri_mode == "Alphabétique":
        all_items = sorted(all_items, key=lambda x: x[1].lower())
    elif tri_mode == "Catégorie":
        all_items = sorted(all_items, key=lambda x: x[2].lower())
    elif tri_mode == "Besoin":
        all_items = sorted(all_items, key=lambda x: x[3], reverse=True)

    # -------- AFFICHAGE DES ITEMS --------
    for iid, name, cat, needed in all_items:

        col1, col2, col3, col4, col5 = st.columns([5, 2, 2.5, 1, 1])

        # Nom
        with col1:
            st.write(f"**{name}**")

        # Bouton Oui/Non (toggle direct)
        with col2:
            if st.button("✔️" if needed else "❌", key=f"toggle_{iid}"):
                toggle_needed(iid)
                st.rerun()

        # Catégorie (selectbox compact)
        with col3:
            new_cat = st.selectbox(
                "",
                list(cat_dict.keys()),
                index=list(cat_dict.keys()).index(cat),
                key=f"cat_select_{iid}"
            )


        # Bouton Changer catégorie
        with col4:
            if st.button("📂", key=f"cat_update_{iid}"):
                update_item_category(iid, cat_dict[new_cat])
                st.rerun()

        # Supprimer
        with col5:
            if st.button("🗑️", key=f"del_{iid}"):
                delete_item(iid)
                st.rerun()

        st.write("")  # lignes rapprochées

# ----------------- BESOINS PAR CATEGORIE -----------------
elif page == "Besoins par catégorie":
    st.title("Besoins par catégorie")

    tri_mode = st.selectbox(
        "Mode de tri",
        ["Alphabétique", "Ordre d’ajout"]
    )

    needed_items = get_items(only_needed=True)

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
