import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


# API keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_REGION = os.getenv("AZURE_REGION", "eastus")


# Directories
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
STOCK_VIDEOS_DIR = os.getenv("STOCK_VIDEOS_DIR", "E:\$Videos\STOCK_VIDEOS")


# Video settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
MAX_VIDEO_DURATION = 60  # seconds
DEFAULT_FPS = 24


# TTS settings
TTS_FALLBACK_ENABLED = True


# Subtitle settings
SUBTITLE_CHUNK_DURATION = 3  # seconds per chunk
SUBTITLE_FONTSIZE = 80
SUBTITLE_MAX_WORDS_PER_CHUNK = 6
SUBTITLE_COLOR = 'white'
SUBTITLE_STROKE_COLOR = 'black'
SUBTITLE_STROKE_WIDTH = 6


# Create directories if they dont exist
Path(OUTPUT_DIR).mkdir(exist_ok=True)
Path(STOCK_VIDEOS_DIR).mkdir(exist_ok=True)


# Supported video extensions
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv']


# News API settings
NEWS_PAGE_SIZE = 10
NEWS_COUNTRY = "us"
NEWS_LANGUAGE = "en"