"""
Helper functions for interacting with the OpenAI API.
"""
import os
import json
import logging
from typing import Dict, Any, List

from openai import OpenAI
from utils.config import Config

# Set up logging
logger = logging.getLogger("discord_bot")

# Initialize OpenAI client
openai = OpenAI(api_key=Config.get_openai_api_key())

def generate_ai_response(prompt: str, user_name: str = "User") -> str:
    """
    Generate a response from OpenAI based on the prompt.
    
    Args:
        prompt: The user's message
        user_name: The user's name for personalization
        
    Returns:
        str: The AI-generated response
    """
    try:
        # The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        logger.debug(f"Generating AI response for prompt: {prompt[:50]}...")
        
        system_message = (
            f"You are a helpful Discord bot assistant named {Config.get_bot_name()}. "
            f"You are currently talking to {user_name} in a Discord server. "
            f"Be friendly, helpful, and concise in your responses. "
            f"If you don't know something, just say so. "
            f"Don't make up information."
        )
        
        response = openai.chat.completions.create(
            model="gpt-4o",  # Using the latest model
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        
        result = response.choices[0].message.content
        logger.debug(f"Generated AI response: {result[:50]}...")
        return result
    
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        raise Exception(f"Failed to generate AI response: {str(e)}")

def generate_image(prompt: str) -> Dict[str, str]:
    """
    Generate an image using OpenAI's DALL-E model.
    
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
        
        response = openai.images.generate(
            model="dall-e-3",
            prompt=safe_prompt,
            n=1,
            size="1024x1024",
        )
        
        result = {"url": response.data[0].url}
        logger.debug(f"Generated image URL: {result['url']}")
        return result
    
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        raise Exception(f"Failed to generate image: {str(e)}")

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze the sentiment of a message.
    
    Args:
        text: The text to analyze
        
    Returns:
        Dict: A dictionary containing sentiment analysis results
    """
    try:
        # The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a sentiment analysis expert. "
                    + "Analyze the sentiment of the text and provide a rating "
                    + "from 1 to 5 stars and a confidence score between 0 and 1. "
                    + "Respond with JSON in this format: "
                    + "{'rating': number, 'confidence': number, 'mood': string}",
                },
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
        )
        
        result = json.loads(response.choices[0].message.content)
        return {
            "rating": max(1, min(5, round(result["rating"]))),
            "confidence": max(0, min(1, result["confidence"])),
            "mood": result.get("mood", "neutral")
        }
    except Exception as e:
        logger.error(f"Failed to analyze sentiment: {e}")
        return {"rating": 3, "confidence": 0, "mood": "unknown"}

def summarize_conversation(messages: List[Dict[str, str]]) -> str:
    """
    Summarize a conversation using the OpenAI API.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        
    Returns:
        str: The summary of the conversation
    """
    try:
        # The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        prompt = f"Please summarize the following conversation concisely:\n\n{conversation_text}"
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=200,
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        logger.error(f"Error summarizing conversation: {e}")
        return "Failed to summarize the conversation."
