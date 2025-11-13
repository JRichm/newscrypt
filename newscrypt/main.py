import os

from newscrypt.config import OUTPUT_DIR
from newscrypt.services.news_service import NewsService
from newscrypt.services.script_service import ScriptService
from newscrypt.services.tts_service import TTSService
from newscrypt.services.video_service import VideoService
from newscrypt.services.subtitle_service import SubtitleService


class NewScrypt:
    def __init__(self):
        self.news = NewsService()
        self.script = ScriptService()
        self.subtitles = SubtitleService()
        self.tts = TTSService()
        self.video = VideoService()


    def get_trending_articles(self):
        return self.news.get_trending_articles()


    def get_trending_article(self):
        return self.news.get_trending_topic()


    def search_articles(self, search_term, page_size: int = 5):
        return self.news.search_news(query=search_term, page_size=page_size)
    

    def summarize_article(self, article):
        return self.script.generate_script(article)
    

    def validate_script(self, script):
        return self.script.validate_script(script)

    
    def create_subtitle_chunks(self, script_text, total_duration):
        return self.subtitles.create_subtitle_chunks(script_text, total_duration)
    

    def create_subtitle_clips(self, subtitle_chunks, video_width, video_height):
        return self.subtitles.generate_subtitle_clips(subtitle_chunks, video_width, video_height)
    

    def cleanup_subtitle_temp(self):
        self.subtitles.cleanup_temp_files()


    def create_text_to_speech(self, script_text):
        return self.tts.generate_tts(script_text)


    def find_stock_video(self, script_text):
        return self.video.select_clip()
    

    def compose_video(self, clip_paths, audio_path, script_text):
        return self.video.compose_video(clip_paths, audio_path, script_text)
    

    def validate_video(self, video_path):
        return self.video.validate_video_file(video_path)
    

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
