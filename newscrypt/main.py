import os

from newscrypt.config import OUTPUT_DIR
from services.news_service import NewsService
from services.script_service import ScriptService
from services.tts_service import TTSService
from services.video_service import VideoService


def main():
    """Main entry point for the news video generator"""
    try:
        # Initialize services
        news_service = NewsService()
        script_service = ScriptService()
        tts_service = TTSService()
        video_service = VideoService()
        
        # Fetch trending topic
        print("Fetching trending topic...")
        article = news_service.get_trending_topic()
        if not article:
            print("No trending topics found.")
            return

        print(f"Selected article: {article.get('title', 'Unknown')}")

        # Generate script
        print("Generating script...")
        script = script_service.generate_script(article)
        if not script:
            print("Failed to generate script.")
            return

        # Generate audio
        print("Generating audio...")
        audio_path = tts_service.generate_tts(script)
        if not audio_path:
            print("Failed to generate audio.")
            return
        
        # Select video clip
        print("Selecting video clip...")
        clip_path = video_service.select_clip(script)
        if not clip_path:
            print("Failed to select video clip.")
            return
        
        # Compose final video
        print("Composing final video...")
        output_path = video_service.compose_video(clip_path, audio_path, script)
        if output_path:
            print(f"Video created successfully: {output_path}")
        else:
            print("Failed to create video.")

    except Exception as e:
        print(f"Error in main process: {str(e)}")
    
    finally:
        # Cleanup temporary files
        if 'audio_path' in locals() and audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
                print("Cleaned up temporary audio file.")
            except:
                pass


if __name__ == "__main__":
    main()