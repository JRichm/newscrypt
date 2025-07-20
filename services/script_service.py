
from typing import Optional, Dict, Any
from openai import OpenAI
from config import OPENAI_API_KEY


class ScriptService:
    """Service for generating video scripts from news articles"""

    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    
    def generate_script(self, article: Dict[str, Any]) -> Optional[str]:
        """Generate video script from article using OpenAI"""

        if not article:
            return None
        
        content = article.get("description") or article.get("content") or article.get("title")
        title = article.get("title", "")

        if not content:
            print("No content found in article")
            return None
        
        try:
            if self.client:
                return self._generate_openai_script(title, content)
            else:
                return self._generate_fallback_script(title, content)

        except Exception as e:
            print(f"Error generating script: {e}")
            return self._generate_fallback_script(title, content)
        

    def _generate_openai_script(self, title: str, content: str) -> str:
        """Generate script using OpenAI API"""

        prompt = f"""
            Create an engaging 60-second video script based on this news article.

            Title: {title}
            Content: {content}

            Requirements:
            - Keep it under 100 words
            - Use conversational, engaging tone
            - Start with a hook
            - End with intrigue or call to action
            - Make it suitable for social media video
            - Avoid complex technical terms

            Return only the script text, no additional formatting.
        """

        response = self.client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )

        return response.choices[0].message.content.strip()
    

    def _generate_fallback_script(self, title: str, content: str) -> str:
        """Generate a basic script when OpenAI is not available"""

        script = f"""
            Breaking News! {title}
            {content[:150]}...
            This developing story is capturing attention worldwide.
            What do you think about this? Let us know in the comments!
        """
        return script.strip()
    
    
    def validate_script(self, script: str) -> bool:
        """Validate that the script meets basic requirements"""
        
        if not script:
            return False
        
        words = script.split()
        return 10 <= len(words)