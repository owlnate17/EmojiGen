
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
from PIL import Image 
import requests 
from transformers import AutoModelForCausalLM 
from transformers import AutoProcessor 

def emoji_photo_page():
    """Function to create the EmojiGen Photo page."""
    st.title("EmojiGen Photo")

    # Camera input widget
    photo = st.camera_input("Take a picture")

    if photo is not None:
        # Open and display the photo
        image = Image.open(photo)
        st.image(image, caption='Captured Image', use_column_width=True)

        # Convert the image to the format required by the model
        images = [image]  # Model expects a list of images
        placeholder = "<|image_1|>\n"

        messages = [
            {"role": "user", "content": placeholder + "Extract text from the image."},
        ]

        # Generate prompt
        prompt = processor.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # Process the image and prompt
        inputs = processor(prompt, images, return_tensors="pt").to("cuda:0")

        # Define generation arguments
        generation_args = {
            "max_new_tokens": 100,
            "temperature": 0.0,
            "do_sample": False,
        }

        # Generate text from the image
        generate_ids = model.generate(
            **inputs,
            eos_token_id=processor.tokenizer.eos_token_id,
            **generation_args
        )

        # Remove input tokens from output
        generate_ids = generate_ids[:, inputs['input_ids'].shape[1]:]
        response = processor.batch_decode(
            generate_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0]

        # Display the extracted text
        st.subheader("Extracted Text")
        st.write(response)

        # Provide a download link for the text
        text_filename = "extracted_text.txt"
        with open(text_filename, "w") as file:
            file.write(response)

        st.markdown(
            f'<a href="data:text/plain;base64,{base64.b64encode(response.encode()).decode()}" download="{text_filename}">Download Extracted Text</a>',
            unsafe_allow_html=True
        )
