import streamlit as st
import requests

# FastAPI endpoint
API_URL = "http://127.0.0.1:8000/generate_script/"

# Streamlit app
st.title("Content Script Generator 📝")
st.markdown("""
Generate engaging scripts for various platforms. Choose the format, enter details, and get a human-like script with SEO-friendly keywords and hashtags.
""")

# Input fields
topic = st.text_input("Enter the topic:", placeholder="E.g., AI in Healthcare, Productivity Hacks, etc.")
tone = st.selectbox("Select the tone:", ["conversational", "formal", "humorous"])
format_options = {
    "LinkedIn post": "linkedin",
    "Instagram caption": "instagram",
    "YouTube description": "youtube_desc",
    "Monologue": "monologue",
    "Interview": "interview"
}
script_type = st.selectbox("Select the script type:", [
    "linkedin_post",
    "instagram_caption",
    "youtube_description",
    "video_script"
])

format_selection = st.selectbox("Select the script format:", list(format_options.keys()))
temperature = st.slider("Select variation level (temperature):", min_value=0.1, max_value=1.0, value=0.7, step=0.1)
search_tool = st.selectbox("Select the search tool:", ["duckduckgo", "googlesearch"])

# Generate script
if st.button("Generate Script"):
    if topic.strip():
        st.info("Generating your script. Please wait...")
        try:
            # Send a POST request to the FastAPI backend
            payload = {
                "topic": topic,
                "tone": tone,
                "format": format_options[format_selection],
                "script_type": script_type,  # Ensure this is included
                "temperature": temperature,
                "search_tool": search_tool,
            }
            response = requests.post(API_URL, json=payload)

            if response.status_code == 200:
                result = response.json()
                st.success("Script generated successfully!")
                st.text_area("Generated Script:", value=result["script"], height=300)
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            st.error(f"Request error occurred: {e}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
