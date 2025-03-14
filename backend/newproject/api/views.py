from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import openai
import os
from dotenv import load_dotenv
 
# Load environment variables
load_dotenv()
 
# Load Azure OpenAI API Key, Endpoint, and Deployment Name
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
 
if not AZURE_OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_DEPLOYMENT_NAME:
    raise ValueError("Azure OpenAI API credentials are missing in environment variables.")
 
# Initialize OpenAI API client
openai.api_type = "azure"
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_key = AZURE_OPENAI_API_KEY
 
# Store the last AI output
last_ai_output = None
 
@api_view(["POST"])
def process_survey(request):
    global last_ai_output
    user_input = request.data  # Get data from React frontend
 
    # Ensure user_input is not empty or malformed
    if not user_input:
        return Response({"error": "No input data provided."}, status=status.HTTP_400_BAD_REQUEST)
 
    # Create a prompt for Azure OpenAI
    prompt = f"""
    You are an AI Project consultant assisting students with their final year projects. Based on the dataset provided by the user, create a detailed and structured project plan tailored to their specific project. The plan should cover key stages of project development. Use clear headers, bullet points, and concise paragraphs for each stage. The sections should be clearly labeled and easy to copy into a document. The sections to be included are:
    1. **Idea Validation**:
        - Provide steps for validating the project concept.
        - Define the problem and its scope.
    2. **Market Research**:
        - Identify target audience.
        - Analyze competitors and market demand.
    3. **Product Development**:
        - Outline the process of designing and testing the solution.
        - Include development phases such as Backend, Frontend, and AI model training.
    4. **Key Milestones and Deliverables**:
        - Break down essential tasks and milestones.
        - Provide a timeline for each phase.
    Ensure the format is clean and easy to understand, like a roadmap with clear stages, headings, and bullet points.
    {user_input}
    """
    try:
        # Call Azure OpenAI API
        response = openai.ChatCompletion.create(
            deployment_id=AZURE_OPENAI_DEPLOYMENT_NAME,  # Fix: Use deployment_id
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        if response and "choices" in response and len(response["choices"]) > 0:
            ai_output = response["choices"][0]["message"]["content"].strip()
            last_ai_output = ai_output  # Store the output
            return Response({"response": ai_output}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No response from Azure OpenAI."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(["GET"])
def get_activity(request):
    global last_ai_output
    if last_ai_output:
        return Response({"response": last_ai_output}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "No activity found"}, status=status.HTTP_404_NOT_FOUND)
 
# Function to clean output
def clean_output(response_text):
    """Cleans the generated text output."""
    cleaned_text = response_text.replace("\n\n", "\n").strip()
    return cleaned_text 