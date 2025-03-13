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
    prompt = f"You are an AI Project consultant helping students with their final year projects. Based on the dataset provided by the user, create a comprehensive and detailed project plan tailored to their specific project. The plan should cover key stages of project development, including:Idea Validation: How to validate the project concept, define the problem, and ensure its feasibility.Market Research: Steps for conducting market research to understand the target audience, competitors, and demand.Product Development: The process for designing, developing, and testing the solution or prototype.Project Milestones and Deliverables: Breakdown of essential tasks, milestones, and deliverables for each stage of the project.Timelines and Resource Allocation: Define realistic timelines and resource needs (team members, tools, etc.) for each stage.Ensure that the project plan is actionable, comprehensive, and follows best practices in the project ecosystem. The plan should be clear enough to guide the student through each stage of the project while allowing flexibility for adjustments based on project scope or unforeseen challenges\n{user_input}"

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
