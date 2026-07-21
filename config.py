import streamlit as st

st.title("Mon site personnel")
st.write("Bienvenue sur mon interface interactive !")

nom = st.text_input("Entre ton nom :")
if st.button("Enregistrer"):
    st.write(f"Bonjour {nom} !")
