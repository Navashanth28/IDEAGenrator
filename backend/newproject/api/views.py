from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Load Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Gemini API key not found in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)

# Store the last Gemini output with timestamp
last_gemini_output = {"timestamp": None, "content": None}

# Add these debug flags after the logger setup
DEBUG_MODE = True
SAFETY_SETTINGS = {
    "HARM_CATEGORY_HARASSMENT": "block_none",
    "HARM_CATEGORY_HATE_SPEECH": "block_none",
    "HARM_CATEGORY_SEXUALLY_EXPLICIT": "block_none",
    "HARM_CATEGORY_DANGEROUS_CONTENT": "block_none",
}

GEMINI_MODEL = "gemini-1.5-pro"  # Updated to use gemini-1.5-pro

from .models import Survey

@api_view(["POST"])
def process_survey(request):
    try:
        user_input = request.data
        logger.info(f"Received survey data: {json.dumps(user_input)}")
        
        if not user_input:
            return Response(
                {"error": "No input data provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate required fields
        required_fields = ["industry", "targetAudience", "technology"]
        missing_fields = [field for field in required_fields if not user_input.get(field)]
        
        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Ensure lists are properly initialized
            survey_data = {
                "industry": user_input.get("industry"),
                "industry_other": user_input.get("industryOther", ""),
                "target_audience": user_input.get("targetAudience"),
                "technology": user_input.get("technology", []),
                "sub_technology": user_input.get("subTechnology", ""),
                "platform": user_input.get("platform", ""),
                "web_frontend": user_input.get("webFrontend", []),
                "web_backend": user_input.get("webBackend", []),
                "web_hosting": user_input.get("webHosting", []),
                "web_database": user_input.get("webDatabase", []),
                "security_features": user_input.get("securityFeatures", [])
            }
            
            logger.info(f"Creating survey with data: {json.dumps(survey_data)}")
            survey = Survey.objects.create(**survey_data)
            logger.info(f"Survey created successfully with ID: {survey.id}")
            
        except Exception as db_error:
            logger.error(f"Database error details: {str(db_error)}", exc_info=True)
            return Response(
                {"error": f"Failed to save survey data: {str(db_error)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            if DEBUG_MODE:
                logger.info(f"Initializing Gemini model {GEMINI_MODEL}...")
            
            if not GEMINI_API_KEY:
                logger.error("Gemini API key is missing")
                return Response(
                    {"error": "API configuration error: Missing API key"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Updated model initialization with more configuration
            try:
                model = genai.GenerativeModel(
                    model_name=GEMINI_MODEL,
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.8,
                        "top_k": 40,
                        "max_output_tokens": 2048,
                    }
                )
                logger.info(f"Successfully initialized Gemini model: {GEMINI_MODEL}")
            except Exception as model_error:
                logger.error(f"Failed to initialize Gemini model: {str(model_error)}")
                return Response(
                    {"error": f"AI model initialization failed: {str(model_error)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            if DEBUG_MODE:
                logger.info("Preparing prompt for Gemini API...")

            # Format the prompt more clearly
            technologies = ", ".join(user_input.get("technology", []))
            frontend = ", ".join(user_input.get("webFrontend", []))
            backend = ", ".join(user_input.get("webBackend", []))
            database = ", ".join(user_input.get("webDatabase", []))
            
            prompt = f"""Create a project plan for a {user_input.get('industry')} project with the following details:
            - Target Audience: {user_input.get('targetAudience')}
            - Core Technologies: {technologies}
            - Frontend: {frontend}
            - Backend: {backend}
            - Database: {database}

            Please provide:
            1. Project Overview
            2. Technical Architecture
            3. Development Phases
            4. Timeline Estimation
            5. Key Features
            6. Testing Strategy

            Format with clear headers and bullet points.
            """

            if DEBUG_MODE:
                logger.info("Sending request to Gemini API...")
                logger.info(f"Prompt: {prompt}")

            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }

            try:
                response = model.generate_content(
                    contents=prompt,
                    generation_config=generation_config
                )
                logger.info("Successfully generated content from Gemini API")
            except Exception as generate_error:
                logger.error(f"Content generation failed: {str(generate_error)}")
                return Response(
                    {"error": f"Content generation failed: {str(generate_error)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            if DEBUG_MODE:
                logger.info("Received response from Gemini API")
                
            if not response:
                logger.error("Empty response from Gemini API")
                return Response(
                    {"error": "No response from AI model"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            if not hasattr(response, 'text'):
                logger.error(f"Unexpected response format: {response}")
                return Response(
                    {"error": "Invalid response format from AI model"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            gemini_output = response.text.strip()
            if not gemini_output:
                logger.error("Empty text in Gemini response")
                return Response(
                    {"error": "Empty response from AI model"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Format the output
            formatted_output = gemini_output.replace('\n', '<br>')
            
            return Response({
                "response": formatted_output,
                "timestamp": datetime.now().isoformat()
            }, status=status.HTTP_200_OK)

        except Exception as ai_error:
            logger.error(f"AI model error: {str(ai_error)}", exc_info=True)
            return Response(
                {"error": f"AI model error: {str(ai_error)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except Exception as e:
        logger.error(f"Unexpected error in process_survey: {str(e)}", exc_info=True)
        return Response(
            {"error": f"Server error: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["GET"])
def get_activity(request):
    if last_gemini_output["content"]:
        return Response({
            "response": last_gemini_output["content"],
            "timestamp": last_gemini_output["timestamp"]
        }, status=status.HTTP_200_OK)
    return Response(
        {"error": "No activity found"}, 
        status=status.HTTP_404_NOT_FOUND
    )

@api_view(["GET"])
def get_survey_history(request):
    try:
        surveys = Survey.objects.all().order_by('-created_at')
        survey_data = []
        
        for survey in surveys:
            survey_data.append({
                'id': survey.id,
                'industry': survey.industry,
                'industry_other': survey.industry_other,
                'target_audience': survey.target_audience,
                'technology': survey.technology,
                'sub_technology': survey.sub_technology,
                'platform': survey.platform,
                'web_frontend': survey.web_frontend,
                'web_backend': survey.web_backend,
                'web_hosting': survey.web_hosting,
                'web_database': survey.web_database,
                'security_features': survey.security_features,
                'created_at': survey.created_at.isoformat()
            })
        
        return Response({
            "surveys": survey_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error fetching survey history: {str(e)}")
        return Response(
            {"error": "An error occurred while fetching survey history."}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )