import json
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import base64
import re
import uuid
import time
import os

def draw_emoji_page():
    st.title("EmojiGen Draw")

    """Function to create the Draw Emoji page with brush customization."""
    
    # Sidebar controls for brush color and size
    st.sidebar.subheader("Brush Settings")
    stroke_width = st.sidebar.slider("Brush Size", 1, 20, 5)  # Slider for brush size
    stroke_color = st.sidebar.color_picker("Brush Color", "#000000")  # Color picker for brush color

    st.markdown(
        """
        Here, you can draw your desired emoji! :) \n
        Press the 'Download' button at the bottom of the canvas to update exported image.
        """
    )
    try:
        Path("tmp/").mkdir()
    except FileExistsError:
        pass

    now = time.time()
    N_HOURS_BEFORE_DELETION = 1
    for f in Path("tmp/").glob("*.png"):
        if os.stat(f).st_mtime < now - N_HOURS_BEFORE_DELETION * 3600:
            Path.unlink(f)

    button_id = re.sub(
        "\d+", "", str(uuid.uuid4()).replace("-", "")
    )
    
    file_path = f"tmp/{button_id}.png"

    custom_css = f""" 
        <style>
            #{button_id} {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background-color: rgb(255, 255, 255);
                color: rgb(38, 39, 48);
                padding: .25rem .75rem;
                position: relative;
                text-decoration: none;
                border-radius: 4px;
                border-width: 1px;
                border-style: solid;
                border-color: rgb(230, 234, 241);
            }} 
            #{button_id}:hover {{
                border-color: rgb(246, 51, 102);
                color: rgb(246, 51, 102);
            }}
            #{button_id}:active {{
                box-shadow: none;
                background-color: rgb(246, 51, 102);
                color: white;
            }}
        </style> """

    # Canvas component with brush settings
    data = st_canvas(
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        update_streamlit=False,
        key="png_export"
    )

    if data is not None and data.image_data is not None:
        img_data = data.image_data
        im = Image.fromarray(img_data.astype("uint8"), mode="RGBA")
        im.save(file_path, "PNG")

        buffered = BytesIO()
        im.save(buffered, format="PNG")
        img_data = buffered.getvalue()
        b64 = base64.b64encode(img_data).decode()

        dl_link = (
            custom_css
            + f'<a download="{file_path}" id="{button_id}" href="data:file/txt;base64,{b64}">Export PNG</a><br></br>'
        )
        st.markdown(dl_link, unsafe_allow_html=True)

def emoji_photo_page():
    """Function to create the EmojiGen Photo page."""
    st.title("EmojiGen Photo")

    # Camera input widget
    photo = st.camera_input("Take a picture")

    if photo is not None:
        # Open and display the photo
        image = Image.open(photo)
        st.image(image, caption='Captured Image', use_column_width=True)

        # Convert image to PNG format
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_data = buffered.getvalue()
        b64 = base64.b64encode(img_data).decode()

        # Create a download link for the PNG image
        download_link = f'<a href="data:image/png;base64,{b64}" download="captured_image.png">Download PNG</a>'
        st.markdown(download_link, unsafe_allow_html=True)

def emoji_text_page():
    """Function to create the EmojiGen Text page."""
    st.title("EmojiGen Text")

    # Text input widget
    text = st.text_input("Enter text")

    if text:
        text = text.strip()

        # Display the text
        st.write(f"You entered: {text}")
        text_filename = "tmp/text.txt"
        with open(text_filename, "w") as file:
            file.write(text)

        # Download link for the text file
        st.markdown(
            f'<a href="data:text/plain;base64,{base64.b64encode(text.encode()).decode()}" download="{text_filename}">Download text</a>',
            unsafe_allow_html=True
        )

def main():
    st.set_page_config(
        page_title="Draw your emoji",
        page_icon=":pencil2:",
        layout="wide"  # This makes the page full-width
    )

    st.title("Welcome to EmojiGen!")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a Page", ("Draw Your Emoji", "EmojiGen Photo", "EmojiGen Text"))

    if page == "Draw Your Emoji":
        draw_emoji_page()
    elif page == "EmojiGen Photo":
        emoji_photo_page()
    elif page == "EmojiGen Text":
        emoji_text_page()

if __name__ == "__main__":
    main()
