"""
Helper functions for interacting with the Google AI API.
"""
import os
import json
import logging
from typing import Dict, Any, List
import base64
import requests
from io import BytesIO

import google.generativeai as genai
from utils.config import Config

# Set up logging
logger = logging.getLogger("discord_bot")

# Initialize Google AI
api_key = Config.get_google_api_key()
genai.configure(api_key=api_key)

def generate_ai_response(prompt: str, user_name: str = "User") -> str:
    """
    Generate a response from Google Gemini based on the prompt.
    
    Args:
        prompt: The user's message
        user_name: The user's name for personalization
        
    Returns:
        str: The AI-generated response
    """
    try:
        logger.debug(f"Generating AI response for prompt: {prompt[:50]}...")
        
        system_message = (
            f"You are a helpful Discord bot assistant named {Config.get_bot_name()}. "
            f"You are currently talking to {user_name} in a Discord server. "
            f"Be friendly, helpful, and concise in your responses. "
            f"If you don't know something, just say so. "
            f"Don't make up information."
        )
        
        # Use Gemini-Pro model
        model = genai.GenerativeModel('gemini-pro')
        
        # Combine system message and prompt
        full_prompt = f"{system_message}\n\nUser: {prompt}"
        
        response = model.generate_content(full_prompt)
        
        result = response.text
        logger.debug(f"Generated AI response: {result[:50]}...")
        return result
    
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        raise Exception(f"Failed to generate AI response: {str(e)}")

def generate_image(prompt: str) -> Dict[str, str]:
    """
    Generate an image using Gemini or redirect to another source.
    
    Args:
        prompt: The image generation prompt
        
    Returns:
        Dict: A dictionary containing the URL of the generated image
    """
    try:
        logger.debug(f"Generating image for prompt: {prompt}")
        
        # Add safety guidelines to the prompt
        safe_prompt = (
            f"Generate a safe, appropriate image for a Discord bot: {prompt}. "
            f"The image should be appropriate for all ages and not contain any "
            f"violent, explicit, or offensive content."
        )
        
        # Note: Gemini doesn't have native image generation like DALL-E
        # We could use another service or API here
        # For now, use a placeholder message
        return {
            "error": "Image generation is not currently available with Google AI. "
                    "Please try a text-based request instead."
        }
    
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        raise Exception(f"Failed to generate image: {str(e)}")

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze the sentiment of a message using Gemini.
    
    Args:
        text: The text to analyze
        
    Returns:
        Dict: A dictionary containing sentiment analysis results
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        sentiment_prompt = (
            "Analyze the sentiment of the following text and provide a rating "
            "from 1 to 5 stars (where 1 is very negative and 5 is very positive), "
            "a confidence score between 0 and 1, and a one-word mood descriptor. "
            "Format the response as JSON with the keys 'rating', 'confidence', and 'mood'.\n\n"
            f"Text to analyze: {text}"
        )
        
        response = model.generate_content(sentiment_prompt)
        
        # Extract JSON from response
        response_text = response.text
        
        # Find JSON content (assuming it might be surrounded by markdown code blocks)
        if "```json" in response_text:
            json_content = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_content = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_content = response_text
        
        try:
            result = json.loads(json_content)
            return {
                "rating": max(1, min(5, round(float(result.get("rating", 3))))),
                "confidence": max(0, min(1, float(result.get("confidence", 0.5)))),
                "mood": result.get("mood", "neutral")
            }
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract numerical values
            logger.warning(f"Failed to parse JSON from sentiment response: {response_text}")
            if "rating" in response_text and "confidence" in response_text:
                import re
                rating_match = re.search(r'rating["\s:]+([0-9.]+)', response_text)
                confidence_match = re.search(r'confidence["\s:]+([0-9.]+)', response_text)
                mood_match = re.search(r'mood["\s:]+["\']?(\w+)["\']?', response_text)
                
                rating = int(float(rating_match.group(1))) if rating_match else 3
                confidence = float(confidence_match.group(1)) if confidence_match else 0.5
                mood = mood_match.group(1) if mood_match else "neutral"
                
                return {
                    "rating": max(1, min(5, rating)),
                    "confidence": max(0, min(1, confidence)),
                    "mood": mood
                }
            return {"rating": 3, "confidence": 0.5, "mood": "neutral"}
    except Exception as e:
        logger.error(f"Failed to analyze sentiment: {e}")
        return {"rating": 3, "confidence": 0, "mood": "unknown"}

def summarize_conversation(messages: List[Dict[str, str]]) -> str:
    """
    Summarize a conversation using the Gemini API.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        
    Returns:
        str: The summary of the conversation
    """
    try:
        conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        prompt = f"Please summarize the following conversation concisely:\n\n{conversation_text}"
        
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        return response.text
    
    except Exception as e:
        logger.error(f"Error summarizing conversation: {e}")
        return "Failed to summarize the conversation."