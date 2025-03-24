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
        # Log the raw request data
        logger.info("Raw request data received: %s", request.data)
        
        user_input = request.data
        if not user_input:
            logger.error("Empty request data received")
            return Response(
                {"error": "No input data provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate required fields
        required_fields = ["industry", "targetAudience", "technology"]
        missing_fields = [field for field in required_fields if not user_input.get(field)]
        
        if missing_fields:
            logger.error("Missing required fields: %s", missing_fields)
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Initialize empty lists for optional fields
        survey_data = {
            "industry": user_input.get("industry"),
            "industry_other": user_input.get("industryOther") or "",
            "target_audience": user_input.get("targetAudience"),
            "technology": user_input.get("technology") or [],
            "sub_technology": user_input.get("subTechnology") or "",
            "platform": user_input.get("platform") or "",
            "web_frontend": user_input.get("webFrontend") or [],
            "web_backend": user_input.get("webBackend") or [],
            "web_hosting": user_input.get("webHosting") or [],
            "web_database": user_input.get("webDatabase") or [],
            "security_features": user_input.get("securityFeatures") or []
        }

        # Validate data types
        list_fields = ["technology", "web_frontend", "web_backend", "web_hosting", "web_database", "security_features"]
        for field in list_fields:
            if not isinstance(survey_data[field], list):
                logger.error("Invalid data type for field %s: expected list, got %s", field, type(survey_data[field]))
                return Response(
                    {"error": f"Invalid data type for {field}: must be a list"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        try:
            logger.info("Creating survey with data: %s", survey_data)
            survey = Survey.objects.create(**survey_data)
            logger.info("Survey created successfully with ID: %s", survey.id)
        except Exception as db_error:
            logger.error("Database error: %s", str(db_error), exc_info=True)
            return Response(
                {"error": f"Database error: {str(db_error)}"}, 
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
            
            prompt = f"""Create a comprehensive project documentation for a {user_input.get('industry')} project. Follow this EXACT structure and include ALL sections:

1. Abstract (40 lines)
2. Table of Contents
3. Introduction (30 lines)
4. Project Overview (35 lines)
5. Literature Review
6. Problem Statement & Motivation
7. Aim and Objectives
8. Methodology
9. Functional & Non-Functional Requirements
10. System Architecture
11. Software & Hardware Requirements
12. Model Description
- Detailed explanation of model selection
- Working mechanism analysis
- Justification for model choice
13. Input and Output Design
- Input parameters specification
- Data flow description
- Expected output formats
14. Testing and Implementation
- Testing strategies
- Implementation phases
- Validation steps
15. Deployment Strategy
- Deployment scenarios
- Implementation steps
- Resource requirements
16. Maintenance and Future Enhancements
- Maintenance procedures
- Potential improvements
- Scalability considerations
17. Conclusion (30 lines)
18. References

Important: 
- Each section MUST begin with its corresponding heading (e.g., "## Model Description")
- Include ALL sections listed above
- Maintain consistent formatting
- Use proper section breaks
- Ensure comprehensive coverage of each topic
- Keep the specified line counts where indicated

Technical Specifications:
Industry: {user_input.get('industry')}
Technologies: {technologies}
Frontend: {frontend}
Backend: {backend}
Database: {database}

Please provide detailed content for each section, ensuring no sections are omitted."""

            # Update generation config for longer output
            generation_config = {
                "temperature": 0.9,  # Increased for more creative responses
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 8192,  # Increased token limit
            }

            # Validate response sections
            def validate_response(response_text):
                required_sections = [
                    "## Model Description",
                    "## Input and Output Design",
                    "## Testing and Implementation",
                    "## Deployment Strategy",
                    "## Maintenance and Future Enhancements",
                    "## Conclusion",
                    "## References"
                ]
                
                missing_sections = []
                for section in required_sections:
                    if section not in response_text:
                        missing_sections.append(section)
                
                if missing_sections:
                    logger.warning(f"Missing sections in response: {missing_sections}")
                    # Generate missing sections separately
                    additional_prompt = f"Please generate content for these missing sections: {', '.join(missing_sections)}"
                    try:
                        additional_response = model.generate_content(additional_prompt)
                        if additional_response and hasattr(additional_response, 'text'):
                            return response_text + "\n\n" + additional_response.text
                    except Exception as e:
                        logger.error(f"Error generating missing sections: {str(e)}")
                
                return response_text

            try:
                response = model.generate_content(
                    contents=prompt,
                    generation_config=generation_config
                )
                logger.info("Successfully generated content from Gemini API")
                
                # Handle the response and validate sections
                if response and hasattr(response, 'text'):
                    main_content = response.text
                    validated_content = validate_response(main_content)
                    formatted_output = validated_content.replace('\n', '<br>')
                    
                    return Response({
                        "response": formatted_output,
                        "timestamp": datetime.now().isoformat()
                    }, status=status.HTTP_200_OK)
                else:
                    raise ValueError("Invalid response format from Gemini API")
                
            except Exception as generate_error:
                logger.error(f"Content generation failed: {str(generate_error)}")
                return Response(
                    {"error": f"Content generation failed: {str(generate_error)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

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
    try:
        # Get the most recent survey
        latest_survey = Survey.objects.order_by('-created_at').first()
        
        if latest_survey:
            # Format the response similar to process_survey
            activity_data = {
                'industry': latest_survey.industry,
                'target_audience': latest_survey.target_audience,
                'technology': latest_survey.technology,
                'created_at': latest_survey.created_at.isoformat()
            }
            return Response({
                "response": f"Latest activity: {activity_data}",
                "timestamp": latest_survey.created_at.isoformat()
            }, status=status.HTTP_200_OK)
        
        return Response(
            {"error": "No surveys found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
        
    except Exception as e:
        logger.error(f"Error fetching activity: {str(e)}")
        return Response(
            {"error": f"Error fetching activity: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
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