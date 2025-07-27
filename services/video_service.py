import os
import random

from pathlib import Path
from typing import Optional, List

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from collections import Counter

try:
    from moviepy.editor import (
        VideoFileClip,
        AudioFileClip,
        CompositeVideoClip,
        ColorClip,
        concatenate_videoclips
    )
    moviepy_available = True
except ImportError:
    moviepy_available = False

from pypexel import Pexels
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


    
    def _extract_keywords_nltk(self, text, num_keywords=10):
        tokens = word_tokenize(text.lower())
        pos_tags = pos_tag(tokens)
        
        stop_words = set(stopwords.words('english'))
        keywords = [word for word, pos in pos_tags 
                    if pos.startswith(('NN', 'JJ')) and 
                    word not in stop_words and 
                    len(word) > 2 and 
                    word.isalpha()]
        
        keyword_freq = Counter(keywords)
        return [word for word, freq in keyword_freq.most_common(num_keywords)]


    def select_clip(self, script_text: str) -> Optional[str]:
        """Select appropriate stock video clip based on script content"""

        pexels = Pexels()

        keywords = self._extract_keywords_nltk(script_text)

        videos = pexels.search_videos(query=str(keywords), as_objects=True)

        video_paths = [pexels.download_video(vid, quality='hd') for vid in videos[:3]]

        return video_paths

        
    
    def compose_video(self, clip_paths: List[str], audio_path: str, script_text: str) -> Optional[str]:
        """Compose final video with clip, audio, and subtitles"""

        print(len(clip_paths))
        if not moviepy_available:
            print("MoviePy not available for video composition")
            return None
        
        if not all([clip_paths, audio_path, script_text]):
            print("Missing required components for video composition")
            return None
        
        videos = []
        audio = None
        final_video = None

        try:
            # load audio and video
            videos = [VideoFileClip(clip_path) for clip_path in clip_paths]
            audio = AudioFileClip(audio_path)

            if len(videos) > 1:
                video = concatenate_videoclips(videos)
            else:
                video = videos[0]

            # calculate final duration
            target_duration = min(audio_clip.duration, MAX_VIDEO_DURATION)

            # check if video needs to be looped to match audio length
            if concatenated_video.duration < target_duration:
                loops_needed = int(target_duration / concatenated_video.duration) + 1
                print(f"Video duration ({concatenated_video.duration:.2f}s) shorter than target ({target_duration:.2f}s)")
                print(f"Looping video {loops_needed} times...")
                
                looped_video = concatenate_videoclips([concatenated_video] * loops_needed)
                if len(video_clips) > 1:
                    concatenated_video.close()

                concatenated_video = looped_video

            video_duration = target_duration

            # trim video and audio to match duration
            trimmed_video = concatenated_video.subclip(0, video_duration)
            trimmed_audio = audio_clip.subclip(0, video_duration)

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

        script_words = set(script_lower.split())

        best_match = None
        best_score = 0

        for video_file in video_files:
            filename_keywords = video_file.stem.lower().split('_')
            filename_words = set(filename_keywords)

            matches = len(script_words.intersection(filename_words))

            if matches > best_score:
                best_score = matches
                best_match = video_file

        if best_match and best_score > 0:
            print(f"Found a match with a score of {best_score}")
            return str(best_match)
        else:
            print(f"No match found picking random video")
            return str(random.choice(video_files))

        # keywords = {
        #     'tech': ['technology', 'computer', 'ai', 'digital', 'software', 'internet', 'data'],
        #     'business': ['business', 'economy', 'market', 'finance', 'money', 'trade', 'company'],
        #     'nature': ['nature', 'environment', 'climate', 'weather', 'earth', 'ocean', 'forest'],
        #     'city': ['city', 'urban', 'building', 'street', 'downtown', 'architecture'],
        #     'people': ['people', 'person', 'community', 'social', 'human', 'crowd'],
        #     'health': ['health', 'medical', 'doctor', 'hospital', 'medicine', 'fitness'],
        #     'sports': ['sports', 'game', 'team', 'player', 'competition', 'athletics']
        # }

        # # find category match
        # for category, words in keywords.items():
        #     if any(word in script_lower for word in words):
        #         category_clips = [f for f in video_files if category in str(f).lower()]
        #         if category_clips:
        #             return str(random.choice(category_clips))
        
        # return str(random.choice(category_clips))
    

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