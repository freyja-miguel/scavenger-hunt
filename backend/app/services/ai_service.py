"""AI service - Groq integration for activity generation and photo validation."""

import base64
import json
from typing import Optional

from groq import Groq

from app.config import settings
from app.models.schemas import ActivityCategory, GenerateActivitiesRequest


class AIService:
    """Handles Groq API calls for text (activities) and vision (photo validation)."""

    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None

    async def generate_activities(self, req: GenerateActivitiesRequest) -> list[dict]:
        """Generate activity list via Groq LLM based on category, age, location."""
        if not self.client:
            raise ValueError("GROQ_API_KEY not configured")

        prompt = f"""Generate {req.count} treasure hunt activities for kids in Sydney.
Category: {req.category.value}
Age group: {req.age_min}-{req.age_max} years
Location/area: {req.location_sydney}

For each activity provide:
- title: Short catchy title
- description: What the child should find/do (1-2 sentences)
- ai_validation_prompt: What to look for in the photo to validate completion (e.g. "Must show a fountain or water feature")
- location_sydney: Specific place if applicable

Return JSON array only, no markdown."""

        completion = self.client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )
        text = completion.choices[0].message.content
        # Strip markdown code blocks if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())

    async def validate_photo(
        self, image_base64: str, activity_description: str, validation_criteria: str
    ) -> dict:
        """Validate photo against activity using Groq vision model."""
        if not self.client:
            raise ValueError("GROQ_API_KEY not configured")

        # Groq vision accepts base64 or URL
        # Llama 4 Scout supports image input
        prompt = f"""You are validating a photo for a kids treasure hunt activity.
Activity: {activity_description}
Validation criteria: {validation_criteria}

Does this photo show the child actually completing the activity? Consider:
- Does the image match what was asked?
- Does it look like a real photo (not a screenshot or stock image)?
- Is it appropriate for a kids app?

Respond with JSON only: {{"valid": true/false, "reasoning": "brief explanation"}}"""

        # Use vision model - format depends on Groq API
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ],
            }
        ]

        completion = self.client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=messages,
            max_tokens=256,
            temperature=0.2,
        )
        text = completion.choices[0].message.content
        if text.startswith("```"):
            text = text.split("```")[1]
            if "json" in text[:10]:
                text = text[text.find("{"):]
        return json.loads(text.strip())
