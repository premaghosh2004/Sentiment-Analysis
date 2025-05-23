import streamlit as st
import os
import google.generativeai as genai  
from streamlit_lottie import st_lottie, st_lottie_spinner
from dotenv import load_dotenv
import requests

# ------------------- API Setup -------------------
load_dotenv()
gemini_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=gemini_api_key)

# ------------------- Lottie Loader -------------------
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_url_loading = "https://lottie.host/cc2b3b2d-5589-4c22-a42b-9c3d50fb8315/b8kIpS7sC0.json"
lottie_loading = load_lottieurl(lottie_url_loading)

# ------------------- Utility -------------------
def validateGeminiAPIKey(input_string):
    start_index = input_string.find("AIzaSy")
    if start_index != -1:
        return input_string[start_index:6]
    return None

# ------------------- Home Page -------------------
def HomePage(**kwargs):
    if kwargs.get("parse_function"):
        st.set_page_config(page_title="Sentiment Analysis", page_icon="🤖", layout="wide")

        # Hide streamlit branding
        st.markdown("""
            <style>
                .stDeployButton {visibility: hidden;}
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                .stButton button {background-color: #4CAF50; color: white;}
                .sidebar .sidebar-content {width: 1280px;}
            </style>
        """, unsafe_allow_html=True)

        st.write("# Sentiment Analysis Chatbot.")

        try:
            st.sidebar.image("scripts/assets/Gemini.jpg", use_container_width=True)
        except Exception as e:
            st.sidebar.warning("Image not found or failed to load.")
            st.sidebar.text(str(e))

# ------------------- Run Home Page -------------------
HomePage(parse_function=True)

# ------------------- Chatbot UI -------------------
st.title("✨ AI Chatbot with Sentiment Analysis ✨")
st.subheader("Your AI friend who understands your emotions and responds accordingly!")

st.markdown("""
    <script>
        document.addEventListener('DOMContentLoaded', function () {
            const textarea = document.querySelector('textarea');
            const button = document.querySelector('button');

            textarea.addEventListener('keydown', function(event) {
                if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
                    // Insert newline
                    const cursorPos = textarea.selectionStart;
                    const text = textarea.value;
                    textarea.value = text.slice(0, cursorPos) + '\\n' + text.slice(cursorPos);
                    textarea.selectionStart = textarea.selectionEnd = cursorPos + 1;
                    event.preventDefault();
                } else if (event.key === 'Enter') {
                    event.preventDefault();
                    button.click();
                }
            });
        });
    </script>
""", unsafe_allow_html=True)

# ------------------- Chat Form -------------------
user_input = st.text_area("Type your message", height=200)
submit_button = st.button("🤖 Send Message")

# ------------------- Chat Response -------------------
if submit_button and user_input:
    if not gemini_api_key:
        st.sidebar.error("Google API Key is not set. Please set it in the environment variables.")
    else:
        st.subheader("Analyzing Sentiment... Please Wait...")
        with st_lottie_spinner(lottie_loading, height=175, width=175, speed=0.75, quality="high"):
            try:
                sentiment_prompt = [
                    f"Analyze the sentiment of the following message: '{user_input}'.\n"
                    "Respond with one of the following: Sentiment is Positive, Sentiment is Negative, Sentiment is Neutral."
                ]
                sentiment_response = genai.GenerativeModel("gemini-1.5-flash").generate_content(sentiment_prompt)
                sentiment = sentiment_response.text.strip()

                sentiment_mapping = {
                    "Positive": {
                        "response_prompt": f"The user is happy or excited. Reply in a cheerful and engaging way: {user_input}",
                        "score": 1.0,
                        "text": "😀 Very Positive"
                    },
                    "Negative": {
                        "response_prompt": f"The user is feeling down or upset. Respond in an empathetic and motivational way: {user_input}",
                        "score": 0.0,
                        "text": "😢 Very Negative"
                    },
                    "Neutral": {
                        "response_prompt": f"The user's sentiment is neutral. Respond naturally: {user_input}",
                        "score": 0.5,
                        "text": "😐 Neutral"
                    }
                }

                sentiment_key = None
                for key in sentiment_mapping:
                    if key in sentiment:
                        sentiment_key = key
                        break

                if sentiment_key:
                    response_data = sentiment_mapping[sentiment_key]
                    chatbot_response = genai.GenerativeModel("gemini-1.5-flash").generate_content([response_data["response_prompt"]])

                    st.markdown(
                        f"""
                        <div style="border: 2px solid #006400; padding: 10px; border-radius: 10px; background-color: #006400;">
                            <strong style="color: white;">Buddy's Reply:</strong>
                            <p style="color: white; margin-top: 5px;">{chatbot_response.text}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.subheader("Sentiment Analysis", divider="rainbow")
                    st.progress(response_data["score"])
                    st.write(f"### Sentiment: {response_data['text']}")

            except Exception as exp:
                st.warning("An error occurred while generating the response. Please try again later.")
                st.write(exp)