import streamlit as st
from streamlit_webrtc import VideoTransformerBase, webrtc_streamer

class VideoTransformer(VideoTransformerBase):
    def transform(self, frame):
        return frame  


st.title("EmojiGen")

# Set up the video stream
webrtc_streamer(key="example", video_transformer_factory=VideoTransformer)

# Button to capture the image
if st.button("Capture"):
    frame = webrtc_streamer.get_frame()  # Get the latest frame
    if frame is not None:
        st.image(frame.to_ndarray(), caption='Captured Image', use_column_width=True)
