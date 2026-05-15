import os
import json

from anthropic import Anthropic
from dotenv import load_dotenv
from utils.image_utils import load_and_encode_image


load_dotenv()
client = Anthropic()

SYSTEM_PROMPT = """
You are a professional product QA analyst specializing in visual fidelity assessment.

Your job is to compare a RAW product image (ground truth) against an AI GENERATED product image.

SCORING RULES:
- Score each feature from 0 to 100
- 100 means perfect match
- 0 means completely wrong or missing

DO NOT penalize for:
- Different background or setting
- Different camera angle or product placement  
- Different lighting direction or shadows
- Different composition or cropping

DO penalize for:
- Wrong product colors, tones, or finish
- Wrong materials or textures on the product itself
- Missing, altered, or hallucinated logos and branding
- Distorted proportions or shape of the product
- Invented features not present in the raw image

BOUNDING BOX INSTRUCTIONS:
For each issue, provide a bounding box showing where the problem is located in the AI GENERATED image.
Use percentage coordinates (0-100) where:
- x_min, y_min = top-left corner of the problem area (as % of image width/height)
- x_max, y_max = bottom-right corner of the problem area (as % of image width/height)

Example: If a logo issue is in the top-right area spanning 70-90% horizontally and 10-25% vertically:
"bbox": {"x_min": 70, "y_min": 10, "x_max": 90, "y_max": 25}

Make boxes tight around the actual problem area, not the entire product.

You must respond ONLY with a valid JSON object. No explanation before or after.
No markdown. No code blocks. Raw JSON only.
"""

JSON_TEMPLATE = """
{
  "overall_match": <number 0-100>,
  "scores": {
    "color_accuracy": <number 0-100>,
    "shape_and_form": <number 0-100>,
    "texture_and_material": <number 0-100>,
    "branding_and_details": <number 0-100>,
    "overall_realism": <number 0-100>
  },
  "issues": [
    {
      "description": "<issue description>",
      "bbox": {
        "x_min": <number 0-100>,
        "y_min": <number 0-100>,
        "x_max": <number 0-100>,
        "y_max": <number 0-100>
      }
    }
  ],
  "improvements": [
    "<improvement suggestion 1>",
    "<improvement suggestion 2>",
    "<improvement suggestion 3>"
  ]
}
"""


def analyze_images(raw_image_path: str, ai_image_path: str) -> dict:
    """
    Sends both images to Claude for QA analysis.
    Returns a dictionary with match scores and improvement notes.
    """
    raw_encoded, raw_media = load_and_encode_image(raw_image_path)

    ai_encoded, ai_media = load_and_encode_image(ai_image_path)

    message_content = [
        {"type": "text", "text": "Here is the RAW product image (ground truth):"},
        {
            "type": "image",
            "source": {"type": "base64", "media_type": raw_media, "data": raw_encoded},
        },
        {"type": "text", "text": "Here is the AI GENERATED product image to evaluate:"},
        {
            "type": "image",
            "source": {"type": "base64", "media_type": ai_media, "data": ai_encoded},
        },
        {
            "type": "text",
            "text": f"Analyze both the images and return your assessment using exactly this josn structure:\n{JSON_TEMPLATE}",
        },
    ]

    response = client.messages.create(
        model="claude-sonnet-4-6",  # "claude-haiku-4-5"
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": message_content}],
    )
    print(response)
    response_text = response.content[0].text

    def _extract_json(raw_text: str) -> str:
        raw_text = raw_text.strip()
        if raw_text.startswith("```") and raw_text.endswith("```"):
            lines = raw_text.splitlines()
            if len(lines) >= 3:
                return "\n".join(lines[1:-1]).strip()
        if raw_text.startswith("```json") and raw_text.endswith("```"):
            lines = raw_text.splitlines()
            if len(lines) >= 3:
                return "\n".join(lines[1:-1]).strip()
        if raw_text.startswith("{") and raw_text.endswith("}"):
            return raw_text
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return raw_text[start : end + 1]
        return raw_text

    def _normalize_result(parsed: dict) -> dict:
        normalized = {}
        normalized["overall_match"] = (
            parsed.get("overall_match")
            or parsed.get("Overall_match")
            or parsed.get("overallMatch")
            or 0
        )

        raw_scores = parsed.get("scores") or parsed.get("Scores") or {}
        normalized["scores"] = {
            "color_accuracy": raw_scores.get("color_accuracy")
            or raw_scores.get("Color_accuracy")
            or raw_scores.get("colorAccuracy")
            or 0,
            "shape_and_form": raw_scores.get("shape_and_form")
            or raw_scores.get("Shape_and_form")
            or raw_scores.get("shapeAndForm")
            or 0,
            "texture_and_material": raw_scores.get("texture_and_material")
            or raw_scores.get("Texture_and_material")
            or raw_scores.get("textureAndMaterial")
            or 0,
            "branding_and_details": raw_scores.get("branding_and_details")
            or raw_scores.get("Branding_and_details")
            or raw_scores.get("brandingAndDetails")
            or 0,
            "overall_realism": raw_scores.get("overall_realism")
            or raw_scores.get("Overall_realism")
            or raw_scores.get("overallRealism")
            or 0,
        }

        normalized["issues"] = parsed.get("issues") or parsed.get("Issues") or []
        normalized["improvements"] = (
            parsed.get("improvements") or parsed.get("Improvements") or []
        )
        return normalized

    cleaned_text = _extract_json(response_text)

    try:
        parsed = json.loads(cleaned_text)
        result = _normalize_result(parsed)
    except json.JSONDecodeError:
        result = {
            "overall_match": 0,
            "scores": {
                "color_accuracy": 0,
                "shape_and_form": 0,
                "texture_and_material": 0,
                "branding_and_details": 0,
                "overall_realism": 0,
            },
            "issues": ["Failed to parse Claude response. Please try again."],
            "improvements": ["Please try again with clearer images."],
        }
    return result
