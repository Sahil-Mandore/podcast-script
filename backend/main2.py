from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.googlesearch import GoogleSearch
from phi.model.huggingface import HuggingFaceChat
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import re

# Load environment variables
load_dotenv()

# FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for request payload
class ScriptRequest(BaseModel):
    topic: str
    tone: str = "conversational"
    format: str  # Options: linkedin, instagram, youtube_desc, monologue, interview
    search_tool: str = "duckduckgo"
    duration: int = 5 

# Define web search agents
duckduckgo_agent = Agent(
    name="DuckDuckGo Agent",
    tools=[DuckDuckGo()],
    model=Groq(id="llama-3.3-70b-versatile"),
    markdown=True,
)

google_search_agent = Agent(
    name="Google Search Agent",
    tools=[GoogleSearch()],
    model=Groq(id="llama-3.3-70b-versatile"),
    markdown=True,
)

# Define a function to sanitize web content
def clean_text(text):
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
    text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace
    return text

# Define a scraping function
def scrape_web_data(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        return clean_text("\n".join(p.text for p in soup.find_all("p")))
    except Exception:
        return "No relevant content found."

script_generation_agent = Agent(
    model=HuggingFaceChat(
        id="meta-llama/Meta-Llama-3-8B-Instruct",
        max_tokens=4096,
    ),
    markdown=True,
)

@app.post("/generate_script/")
async def generate_script(request: ScriptRequest):
    """
    Generate a humanized script for various social media platforms or video formats.
    """
    try:
        # Choose search tool
        if request.search_tool == "duckduckgo":
            web_content = duckduckgo_agent.run(request.topic).content
        elif request.search_tool == "googlesearch":
            web_content = google_search_agent.run(request.topic).content
        else:
            raise HTTPException(status_code=400, detail="Invalid search tool.")

        if not web_content:
            web_content = "No relevant content found."
        else:
            web_content = clean_text(web_content)

        # Define prompts based on selected format
        if request.format == "linkedin":
            prompt = f"""
            Write a LinkedIn post caption about {request.topic}.
            Keep it professional yet engaging. Use a human-like tone.
            Include relevant hashtags and a call to action.
            It should be a bit long.
            """
        elif request.format == "instagram":
            prompt = f"""
            Write an Instagram caption for a post about {request.topic}.
            Make it engaging, relatable, and easy to read.
            Include relevant hashtags to boost engagement.
            """
        elif request.format == "youtube_desc":
            prompt = f"""
            Create a YouTube video description for a video about {request.topic}.
            Include an engaging intro, key points covered, and relevant hashtags.
            """
        elif request.format == "monologue":
            prompt = f"""
            You are a YouTube scriptwriter. Create an engaging and informative script for a YouTube video. Please remember to write the script in a human-like tone; we don’t want a plain machine tone.
            
            Topic: {request.topic}
            
            Duration: {request.duration} minutes
            
            Information to use:
            {web_content}
            
            Follow the style and tone from ConsultAdd videos and website.
            
            Structure:
            1. Introduction: Hook viewers with an interesting fact or statement.
            2. Body: Provide detailed, engaging, and informative content.
            3. Conclusion: End with a call to action or thought-provoking insight.
            
            Include SEO keywords and hashtags for Instagram and LinkedIn.
            """
        elif request.format == "interview":
            prompt = f"""
            You are a podcast scriptwriter. Create a detailed interview script. Please remember to write the script in a human-like tone; we don’t want a plain machine tone.
            
            Topic: {request.topic}
            
            Provide:
            - A brief introduction to the topic.
            - A variety of questions the host can ask the guest, including:
              - Questions about the guest's personal journey.
              - Questions focused on the topic.
              - Engaging or thought-provoking questions.
            - Suggestions for follow-up questions based on guest responses.
            
            Ensure the script is conversational and includes transitions between questions.
            At last, provide 15 questions that can be asked about the topic.
            
            Include SEO keywords and hashtags for Instagram and LinkedIn.
            """
        else:
            raise HTTPException(status_code=400, detail="Invalid format specified.")

        # Generate script and retry if response is malformed
        script_response = script_generation_agent.run(prompt)
        generated_script = script_response.content.strip() if script_response and script_response.content else "No script generated. Please try again."
        
        
        return {"script": generated_script}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
