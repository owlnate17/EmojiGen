from io import BytesIO
from pathlib import Path
from requests import HTTPError
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import base64
import re
import uuid
import time
import os
from huggingface_hub import InferenceClient 

hugging_face_inference_client = None

def draw_emoji_page():
    st.title("EmojiGen Draw")

    st.write(
        """
        Welcome to the EmojiGen Draw page! Here's how you can use the drawing tool:
        
        1. Use the brush size slider in the sidebar to adjust the thickness of your brush.
        2. Pick a color for your brush using the color picker.
        3. Start drawing directly on the canvas. Your drawing will be saved as a PNG.
        4. Once you're done, click the "Export PNG" button to download your drawing.
        """
    )
    
    # Sidebar controls for brush color and size
    st.sidebar.subheader("Brush Settings")
    stroke_width = st.sidebar.slider("Brush Size", 1, 20, 5)  # Slider for brush size
    stroke_color = st.sidebar.color_picker("Brush Color", "#000000")  # Color picker for brush color
   
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
        r"\d+", "", str(uuid.uuid4()).replace("-", "")
    )
    
    file_path = f"tmp/{button_id}.png"


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

        custom_css = f"""
            <style>
                #{button_id} {{
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    background-color: rgb(255, 255, 255);
                    color: rgb(38, 39, 48);
                    padding: .25rem .75rem;
                    border-radius: 4px;
                    border: 1px solid rgb(230, 234, 241);
                }}
                #{button_id}:hover {{
                    border-color: rgb(246, 51, 102);
                    color: FF4081;
                    background-color: FFEB3B;
                }}
                #{button_id}:active {{
                    background-color: rgb(246, 51, 102);
                    color: blue;
                }}
            </style>
        """


        dl_link = (
            custom_css
            + f'<a download="{file_path}" id="{button_id}" href="data:file/txt;base64,{b64}">Export PNG</a><br></br>'
        )

        # Convert image to text:
        converted_text = image_to_text(file_path)
        text_filename = os.path.join("tmp", f'{button_id}.txt')
        text = converted_text.strip()
        with open(text_filename, "w") as file:
            file.write(converted_text)
        file.close()
        st.write(f"Converted Text: {converted_text}")
        dl_link += f'<a href="data:text/plain;base64,{base64.b64encode(converted_text.encode()).decode()}" download="{text_filename}.txt">Download text</a>'

        st.markdown(dl_link, unsafe_allow_html=True)

def emoji_photo_page():
    """Function to create the EmojiGen Photo page."""
    st.title("EmojiGen Photo")

    st.write(
        """
        Welcome to the EmojiGen Photo page! Here's how you can use the camera:
        
        1. Click the 'Take a picture' button to capture an image using your camera.
        2. Once the photo is taken, it will be displayed on the screen.
        3. You can then download the image as a PNG by clicking the download link below.
        """
    )

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

        # Save the image to a temporary file
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
            r"\d+", "", str(uuid.uuid4()).replace("-", "")
        )
            
        file_path = f"tmp/{button_id}.png"
        image.save(file_path, "PNG")

        # Create a download link for the PNG image
        download_link = f'<a href="data:image/png;base64,{b64}" download={file_path}>Download PNG</a>'

        # Convert image to text:
        converted_text = image_to_text(file_path)
        text_filename = os.path.join("tmp", f'{button_id}.txt')
        text = converted_text.strip()
        with open(text_filename, "w") as file:
            file.write(converted_text)
        file.close()
        st.write(f"Converted Text: {converted_text}")
        text_download_link = f'<a href="data:text/plain;base64,{base64.b64encode(converted_text.encode()).decode()}" download="{text_filename}.txt">Download text</a>'

        st.markdown(download_link, unsafe_allow_html=True)
        st.markdown(text_download_link, unsafe_allow_html=True)

def emoji_text_page():
    """Function to create the EmojiGen Text page."""
    st.title("EmojiGen Text")

    st.write(
        """
        Welcome to the EmojiGen Text page! Here's how you can create an emoji description:
        
        1. Type in your text description in the input field.
        2. Click the "Submit" button to see your entered text.
        3. You can download your text file by clicking the download link.
        """
    )

    # Text input widget
    text = st.text_input("Enter text")

    if text:
        text = text.strip()

        # Display the text
        st.write(f"You entered: {text}")
        text_filename = os.path.join("tmp", "text.txt")
        with open(text_filename, "w") as file:
            file.write(text)
        file.close()
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

    st.markdown(
        """
        <style>
        .stApp {
            background-color: #F5F8FF; 
            color: #333333; 
        }
        /* Navigation bar styles */
        .nav-bar {
              display: flex;
            justify-content: center;
            align-items: center;
            background-color: #F5F8FF;
            padding: 10px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            margin-bottom: 20px;
        }


        .stButton>button {
            background-color: #A3D8FF;
            border: none;
            padding: 10px 20px;
            color: white;
            cursor: pointer;
            font-weight: bold;
            border-radius: 5px;
            transition: all 0.3s ease;
            margin: 0 10px
        }

        .stButton>button:hover {
            background-color: pink;
            color: white;
        }
        
        .stButton>button:active {
            background-color: yellow;
            color: white;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    # Initialize session state for page selection
    if "page" not in st.session_state:
        st.session_state.page = "EmojiGen Draw"

    # Create a row of columns for horizontal buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("EmojiGen Draw", key="draw_emoji"):
            st.session_state.page = "EmojiGen Draw"
    
    with col2:
        if st.button("EmojiGen Photo", key="emoji_photo"):
            st.session_state.page = "EmojiGen Photo"
    
    with col3:
        if st.button("EmojiGen Text", key="emoji_text"):
            st.session_state.page = "EmojiGen Text"

    # Display the appropriate page based on the selected option
    if st.session_state.page == "EmojiGen Draw":
        draw_emoji_page()
    elif st.session_state.page == "EmojiGen Photo":
        emoji_photo_page()
    elif st.session_state.page == "EmojiGen Text":
        emoji_text_page()

def image_to_text(imagePath: str):
    ret_val = ""

    try:
        ret_val = hugging_face_inference_client.image_to_text(imagePath).generated_text
    except HTTPError as err:
        ret_val = "Network Error! Stacktrace: \n" + str(err.strerror)

    return ret_val
if __name__ == "__main__":

    try:
        token = ""
        with open(os.path.join("config", "hftoken")) as file:
            while line := file.readline():
                token = line.strip()

        hugging_face_inference_client = InferenceClient(token=token)
    except OSError as oe:
        print("Error finding hftoken, please configure in ./config if you haven't already \n" + oe.strerror)
        hugging_face_inference_client = InferenceClient()
    main()

    

  