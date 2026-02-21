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
        """Generate object-based scavenger hunt activities via Groq LLM."""
        if not self.client:
            raise ValueError("GROQ_API_KEY not configured")

        category_hints = {
            "beach": "shells, sea glass, driftwood, pebbles, feathers, seaweed, interesting rocks",
            "bush": "leaves with specific shapes, bark textures, seed pods, flowers, feathers, nuts, gumnuts",
            "garden": "leaves by shape or color, flowers by color, seeds, petals, insects (e.g. butterfly), stones",
            "city": "objects of a specific shape and color, signs, textures, patterns, street art, plants in parks",
        }
        hints = category_hints.get(req.category.value, "natural or urban objects")

        prompt = f"""Generate {req.count} scavenger hunt activities for kids aged {req.age_min}-{req.age_max} in Sydney.
Category: {req.category.value}
Location/area: {req.location_sydney}

Each activity must be a "find an object" task that the kid can photograph. Use objects like: {hints}.

Rules:
- Be specific: include shape, color, or texture (e.g. "find a leaf shaped like a heart", "find a shell that is spiral-shaped and white", "find something round and blue").
- Age {req.age_min}-7: simpler (e.g. "find a red flower", "find a smooth stone").
- Age 8-12: can be more specific (e.g. "find a leaf with 5 pointed edges", "find a shell with stripes").
- The kid will take a photo of the object they find; AI will validate that the photo shows the correct object.

For each activity provide:
- title: Short catchy title (e.g. "Spiral Shell Hunter")
- description: Clear instruction for the kid (e.g. "Find a spiral-shaped shell on the beach")
- ai_validation_prompt: Exact criteria for photo validation - object type, shape, and/or color the AI must see (e.g. "Photo must show a spiral or coiled shell, not flat or broken")
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
        prompt = f"""You are validating a photo for a kids scavenger hunt activity.
The kid was asked to find an object and take a photo of it.

Activity: {activity_description}
Validation criteria (what the photo must show): {validation_criteria}

Check:
1. Does the photo clearly show the required object (correct type, shape, color)?
2. Is it a real photo of a physical object (not a screenshot, drawing, or stock image)?
3. Is it appropriate for a kids app?

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
