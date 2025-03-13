from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Gemini API key not found in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)

# Store the last Gemini output
last_gemini_output = None

@api_view(["POST"])
def process_survey(request):
    global last_gemini_output
    user_input = request.data  # Get data from React frontend
    
    # Create a prompt for Gemini
    prompt = f"Based on the user's survey responses, provide insights:\n{user_input}"

    try:
        # Call Gemini 2.0 API
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        
        if response and response.candidates:
            gemini_output = response.candidates[0].content.parts[0].text.strip()
            last_gemini_output = gemini_output  # Store the output
            return Response({"response": gemini_output}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No response from Gemini."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def get_activity(request):
    global last_gemini_output
    if last_gemini_output:
        return Response({"response": last_gemini_output}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "No activity found"}, status=status.HTTP_404_NOT_FOUND)
