import os
import random

from pathlib import Path
from typing import Optional, List

try:
    from moviepy.editor import (
        VideoFileClip, AudioFileClip, CompositeVideoClip, 
        ColorClip
    )
    moviepy_available = True
except ImportError:
    moviepy_available = False

from config import (
    STOCK_VIDEOS_DIR,
    OUTPUT_DIR,
    VIDEO_EXTENSIONS,
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    MAX_VIDEO_DURATION,
    DEFAULT_FPS
)

from services.subtitle_service import SubtitleService

class VideoService:
    """Service for video selection and composition"""

    def __init__(self):
        self.subtitle_service = SubtitleService()


    def select_clip(self, script_text: str) -> Optional[str]:
        """Select appropriate stock video clip based on script content"""

        if not os.path.exists(STOCK_VIDEOS_DIR):
            print(f"Stock videos directory not found: {STOCK_VIDEOS_DIR}")
            return self._create_default_video()
        
        try:
            video_files = self._find_video_files()

            if not video_files:
                print("No video files found in stock directory")
                return self._create_default_video()
        
            # try to match script content to video category
            selected_clip = self._match_script_to_video(script_text.lower(), video_files)
            return selected_clip
            
        except Exception as e:
            print(f"Error selecting clip: {e}")
            return self._create_default_video()
        
    
    def compose_video(self, clip_path: str, audio_path: str, script_text: str) -> Optional[str]:
        """Compose final video with clip, audio, and subtitles"""

        if not moviepy_available:
            print("MoviePy not available for video composition")
            return None
        
        if not all([clip_path, audio_path, script_text]):
            print("Missing required components for video composition")
            return None
        
        video = None
        audio = None
        final_video = None

        try:
            # load audio and video
            video = VideoFileClip(clip_path)
            audio = AudioFileClip(audio_path)

            # adjust duration
            video_duration = min(video.duration, audio.duration, MAX_VIDEO_DURATION)
            video = video.subclip(0, video_duration)
            audio = audio.subclip(0, video_duration)

            # create subtitles
            subtitle_chunks = self.subtitle_service.create_subtitle_chunks(script_text, video_duration)
            subtitle_clips = self.subtitle_service.generate_subtitle_clips(subtitle_chunks)

            # compose final video
            if subtitle_clips:
                final_video = CompositeVideoClip([video.set_audio(audio)] + subtitle_clips)
                print(f"Created video with {len(subtitle_clips)} subtitle clips")
            else:
                final_video = video.set_audio(audio)
                print("Created video without subtitles")

            output_path = self._generate_output_path()
            print("Writing video file...")
            
            final_video.write_videofile(
                output_path,
                fps=DEFAULT_FPS,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=f"temp-audio-{random.randint(1000, 9999)}.m4a",
                remove_temp=True,
                verbose=False,
                logger=None,
            )

            return output_path
        
        except Exception as e:
            print(f"Error composing video: {e}")
            return None
        
        # cleanup
        finally:
            if video:
                video.close()
            if audio:
                audio.close()
            if final_video:
                final_video.close()
            self.subtitle_service.cleanup_temp_files()

    
    def _find_video_files(self) -> List[Path]:
        """Find all video files in the stock directory"""

        video_files = []
        for ext in VIDEO_EXTENSIONS:
            video_files.extend(Path(STOCK_VIDEOS_DIR).glob(f"*{ext}"))
        return video_files
    

    def _match_script_to_video(self, script_lower: str, video_files: List[Path]) -> str:
        """Match script content to approriate video category"""

        keywords = {
            'tech': ['technology', 'computer', 'ai', 'digital', 'software', 'internet', 'data'],
            'business': ['business', 'economy', 'market', 'finance', 'money', 'trade', 'company'],
            'nature': ['nature', 'environment', 'climate', 'weather', 'earth', 'ocean', 'forest'],
            'city': ['city', 'urban', 'building', 'street', 'downtown', 'architecture'],
            'people': ['people', 'person', 'community', 'social', 'human', 'crowd'],
            'health': ['health', 'medical', 'doctor', 'hospital', 'medicine', 'fitness'],
            'sports': ['sports', 'game', 'team', 'player', 'competition', 'athletics']
        }

        # find category match
        for category, words in keywords.items():
            if any(word in script_lower for word in words):
                category_clips = [f for f in video_files if category in str(f).lower()]
                if category_clips:
                    return str(random.choice(category_clips))
        
        return str(random.choice(category_clips))
    

    def _create_default_video(self) -> Optional[str]:
        """Create a simple default video clip if no stock videos are available"""

        if not moviepy_available:
            print("Cannot create default video - MoviePy not available")
            return None
        
        try:
            default_clip = ColorClip(
                size=(VIDEO_WIDTH, VIDEO_HEIGHT),
                color=(25, 25, 112), # dark blue
                duration=MAX_VIDEO_DURATION
            )

            default_path = os.path.join(STOCK_VIDEOS_DIR, "default_background.mp4")
            print("Creating default background video...")

            default_clip.write_videofile(
                default_path,
                fps=DEFAULT_FPS,
                codec='libx264',
                verbose=False,
                logger=None
            )

            default_clip.close()

            return default_path
        
        except Exception as e:
            print(f"Error creating default video: {e}")
            return None
        
    
    def _generate_output_path(self) -> str:
        """Generate unique output path for video"""

        timestamp = random.randint(1000, 9999)
        return os.path.join(OUTPUT_DIR, f'news_video_{timestamp}.mp4')
    
    
    def validate_video_file(self, video_path: str) -> bool:
        """Validate that a video file exists and is readable"""
        
        if not os.path.exists(video_path):
            return False
        
        if not moviepy_available:
            return True # cant validate without moviepy
        
        try:
            with VideoFileClip(video_path) as clip:
                return clip.duration > 0
            
        except:
            return False