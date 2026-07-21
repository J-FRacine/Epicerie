import streamlit as st
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

# -------------------------------------------------
# CONFIG MOBILE-FIRST
# -------------------------------------------------
st.set_page_config(layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 1rem; padding-bottom: 1rem; }

/* Champs plus lisibles sur mobile */
input, select, textarea {
    font-size: 16px !important;
}

/* Boutons larges */
.stButton>button {
    width: 100%;
    border-radius: 10px;
    padding: 0.6rem 1rem;
    font-size: 16px;
}

/* Cartes d’items */
.item-card {
    padding: 0.6rem 0.8rem;
    background-color: #1e1e1e;
    border-radius: 10px;
    margin-bottom: 0.6rem;
}

/* Nom de l’item */
.item-name {
    font-size: 18px;
    font-weight: 600;
}

/* Icônes */
.icon-green {
    color: #4CAF50;
    font-size: 24px;
}
.icon-red {
    color: #FF4B4B;
    font-size: 24px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# INITIALISATION BD
# -------------------------------------------------
init_db()

# -------------------------------------------------
# UTILISATEURS
# -------------------------------------------------
st.sidebar.header("Utilisateur")

users = get_users()
user_names = [u[1] for u in users]

# Ajouter un utilisateur
new_user = st.sidebar.text_input("Ajouter un utilisateur")
if st.sidebar.button("Créer"):
    if new_user.strip():
        add_user(new_user.strip())
        st.rerun()

# Choisir utilisateur
selected_user = st.sidebar.selectbox("Choisir un utilisateur", user_names)
user_id = [u[0] for u in users if u[1] == selected_user][0]

# Renommer utilisateur
rename_val = st.sidebar.text_input("Renommer l'utilisateur")
if st.sidebar.button("Renommer"):
    if rename_val.strip():
        rename_user(user_id, rename_val.strip())
        st.rerun()

# -------------------------------------------------
# CATEGORIES
# -------------------------------------------------
st.sidebar.header("Catégories")

categories = get_categories()
category_names = [c[1] for c in categories]

new_cat = st.sidebar.text_input("Ajouter une catégorie")
if st.sidebar.button("Créer catégorie"):
    if new_cat.strip():
        add_category(new_cat.strip())
        st.rerun()

selected_category = st.sidebar.selectbox("Catégorie par défaut", category_names)
selected_category_id = [c[0] for c in categories if c[1] == selected_category][0]

# -------------------------------------------------
# AJOUT ITEM
# -------------------------------------------------
st.subheader("Ajouter un item")

colA, colB = st.columns([3, 1])

with colA:
    item_name = st.text_input("Nom de l'item", key="item_name")

needed_flag = st.checkbox("J’en ai besoin", value=False)

with colB:
    add_btn = st.button("Ajouter")

if add_btn and item_name.strip():
    add_item(item_name.strip(), selected_category_id, 1 if needed_flag else 0, user_id)
    st.rerun()

# -------------------------------------------------
# LISTE DES ITEMS
# -------------------------------------------------
st.subheader("Tous les items")

sort_option = st.selectbox("Trier les items par", ["Alphabétique", "Catégorie"])

all_items = get_items(user_id)

if sort_option == "Alphabétique":
    all_items = sorted(all_items, key=lambda x: x[1])
else:
    all_items = sorted(all_items, key=lambda x: x[2])

# -------------------------------------------------
# AFFICHAGE MOBILE-FIRST
# -------------------------------------------------
for item_id, name, category, needed in all_items:
    st.markdown('<div class="item-card">', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([3, 3, 2, 1])

    # Nom
    with col1:
        st.markdown(f'<div class="item-name">{name}</div>', unsafe_allow_html=True)

    # Catégorie
    with col2:
        new_cat = st.selectbox(
            "",
            category_names,
            index=category_names.index(category),
            key=f"cat_{item_id}"
        )
        if new_cat != category:
            new_cat_id = [c[0] for c in categories if c[1] == new_cat][0]
            update_item_category(item_id, new_cat_id)
            st.rerun()

    # Besoin / Pas besoin
    with col3:
        if needed:
            if st.button("✓", key=f"need_{item_id}"):
                toggle_needed(item_id)
                st.rerun()
            st.markdown('<span class="icon-green">✓</span>', unsafe_allow_html=True)
        else:
            if st.button("✗", key=f"need_{item_id}"):
                toggle_needed(item_id)
                st.rerun()
            st.markdown('<span class="icon-red">✗</span>', unsafe_allow_html=True)

    # Supprimer
    with col4:
        if st.button("🗑️", key=f"del_{item_id}"):
            delete_item(item_id)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
