import streamlit as st
from PIL import Image

st.title("EmojiGen Photo")

# Camera input widget
photo = st.camera_input("Take a picture")

if photo is not None:
    # Open and display the photo
    image = Image.open(photo)
    st.image(image, caption='Captured Image', use_column_width=True)