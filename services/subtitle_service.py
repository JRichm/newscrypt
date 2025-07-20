import os
from typing import List, Dict, Optional

# optional imports
try:
    from PIL import Image, ImageDraw, ImageFont
    pil_available = True
except ImportError:
    pil_available = False

try:
    from moviepy.editor import ImageClip, TextClip
    moviepy_available = True
except ImportError:
    moviepy_available = False


from config import (
    OUTPUT_DIR,
    SUBTITLE_CHUNK_DURATION,
    SUBTITLE_FONTSIZE,
    SUBTITLE_COLOR,
    SUBTITLE_STROKE_COLOR,
    SUBTITLE_STROKE_WIDTH,
    SUBTITLE_MAX_WORDS_PER_CHUNK,
    VIDEO_WIDTH
)


class SubtitleService:
    """Service for generating synchronized subtitles"""

    def __init__(self):
        self.temp_files = []

    
    def create_subtitle_chunks(self, script_text: str, total_duration: float) -> List[Dict]:
        """Create subtitle chunks with estimated timing"""

        words = script_text.split()
        chunks = []
        word_timings = []
        cumulative_time = 0

        # calculate time for each word
        for word in words:
            word_duration = self._estimate_word_duration(word)
            word_timings.append({
                'word': word,
                'duration': word_duration,
                'start_time': cumulative_time,
                'end_time': cumulative_time + word_duration
            })

            cumulative_time += word_duration

        # scale to match audio duration
        if cumulative_time > 0:
            scale_factor = total_duration / cumulative_time
            for timing in word_timings:
                timing['start_time'] *= scale_factor
                timing['end_time'] *= scale_factor
                timing['duration'] *= scale_factor

        # group words into chunks
        current_chunk = []
        chunk_start = 0

        for i, timing in enumerate(word_timings):
            current_chunk.append(timing['word'])

            # check if chunk should end
            should_end_chunk = (
                (timing['end_time'] - chunk_start) >= SUBTITLE_CHUNK_DURATION or
                any(p in timing['word'] for p in '.,!?;:') or
                len(current_chunk) >= SUBTITLE_MAX_WORDS_PER_CHUNK or
                i == len(word_timings) - 1
            )

            if should_end_chunk and current_chunk:
                chunks.append({
                    'text': ' '.join(current_chunk),
                    'start_time': chunk_start,
                    'end_time': timing['end_time'],
                    'duration': timing['end_time'] - chunk_start
                })
                current_chunk = []
                if i < len(word_timings) - 1:
                    chunk_start = word_timings[i + 1]['start_time']
        
        return chunks
    
    
    def generate_subtitle_clips(self, subtitle_chunks: List[Dict]) -> List:
        """Generate subtitle clips from chunks"""

        subtitle_clips = []
        
        if not moviepy_available:
            print("MoviePy not available for subtitle generation")
            return []
        
        try:
            if pil_available:
                print(f"Creating {len(subtitle_chunks)} synchronized subtitle clips with PIL...")
                subtitle_clips = self._create_pil_subtitles(subtitle_chunks)
            else:
                print("PIL not available, using basic TextClip...")
                subtitle_clips = self._create_text_subtitles(subtitle_chunks)
                
        except Exception as e:
            print(f"Could not create subtitles: {e}")
        
        return subtitle_clips
    

    def _create_pil_subtitles(self, subtitle_chunks: List[Dict]) -> List:
        """Create subtitles using PIL for better quality"""

        subtitle_clips = []
        
        for i, chunk in enumerate(subtitle_chunks):
            subtitle_image = self._create_subtitle_image(chunk['text'])
            if subtitle_image:
                temp_img_path = os.path.join(OUTPUT_DIR, f"temp_subtitle_{i}.png")
                subtitle_image.save(temp_img_path)
                self.temp_files.append(temp_img_path)
                
                subtitle_clip = ImageClip(temp_img_path, duration=chunk['duration'])
                subtitle_clip = subtitle_clip.set_start(chunk['start_time']).set_position(('center', 'bottom'))
                subtitle_clips.append(subtitle_clip)
        
        return subtitle_clips
    

    def _create_text_subtitles(self, subtitle_chunks: List[Dict]) -> List:
        """Create basic text subtitles using MoviePy"""

        subtitle_clips = []
        
        for chunk in subtitle_chunks:
            try:
                subtitle = TextClip(
                    chunk['text'],
                    fontsize=SUBTITLE_FONTSIZE,
                    color=SUBTITLE_COLOR,
                ).set_duration(chunk['duration']).set_start(chunk['start_time']).set_position(('center', 'bottom'))
                subtitle_clips.append(subtitle)
            except Exception as e:
                print(f"Skipping subtitle: {e}")
        
        return subtitle_clips
    

    def _create_subtitle_image(self, text: str, width: int = None, height: int = 200) -> Optional[Image.Image]:
        """Create a subtitle as an image using PIL"""

        if not pil_available:
            return None
        
        width = width or VIDEO_WIDTH
        
        try:
            # Create transparent image
            image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Try to load font
            font = self._load_font(SUBTITLE_FONTSIZE)
            
            # Get text dimensions
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Center the text
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # Draw stroke
            for adj_x in range(-SUBTITLE_STROKE_WIDTH, SUBTITLE_STROKE_WIDTH + 1):
                for adj_y in range(-SUBTITLE_STROKE_WIDTH, SUBTITLE_STROKE_WIDTH + 1):
                    if adj_x != 0 or adj_y != 0:
                        draw.text((x + adj_x, y + adj_y), text, font=font, fill=SUBTITLE_STROKE_COLOR)
            
            # Draw main text
            draw.text((x, y), text, font=font, fill=SUBTITLE_COLOR)
            
            return image
            
        except Exception as e:
            print(f"Error creating subtitle image: {e}")
            return None
    

    def _load_font(self, size: int):
        """Load system font with fallbacks"""

        font_paths = [
            "arial.ttf",
            "Arial.ttf", 
            "C:/Windows/Fonts/arial.ttf",
            "/System/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]
        
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue
        
        return ImageFont.load_default()
    
    
    def _estimate_word_duration(self, word: str) -> float:
        """Estimate speaking duration for a word"""

        base_duration = 0.15
        
        # Clean word
        word = word.lower().strip('.,!?;:"')
        if not word:
            return 0.1
        
        # Count syllables roughly
        vowels = 'aeiou'
        syllables = 0
        prev_was_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllables += 1
            prev_was_vowel = is_vowel
        
        syllables = max(1, syllables)
        duration = base_duration * syllables
        
        # Adjust for word length
        if len(word) >= 8:
            duration *= 1.2
        
        # Fast words
        fast_words = {'a', 'an', 'and', 'the', 'is', 'in', 'on', 'at', 'to', 'of', 'it', 'or'}
        if word in fast_words:
            duration *= 0.7
        
        # Add pause for punctuation
        if any(p in word for p in '.,!?;:'):
            duration += 0.2
        
        return duration
    

    def cleanup_temp_files(self):
        """Clean up temporary subtitle image files"""
        
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
        self.temp_files.clear()