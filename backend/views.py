from django.http import HttpResponse
from django.http import HttpResponse
import stripe
import io
import uuid
import os
from dotenv import load_dotenv
from collections import defaultdict
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
import time
import re
import json
from supabase import create_client, Client
import hashlib
from collections import Counter
from django.db.models import Q
from django.utils import timezone
from django.forms.models import model_to_dict
from django.core import serializers
from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
import pickle
# from langchain.vectorstores import FAISS
# from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from rest_framework import status
from rest_framework.response import Response
import jwt
import secrets
import googlemaps
import requests
from django.conf import settings
from icalendar import Calendar, Event
from datetime import datetime, timedelta
from token_count import TokenCount
from datetime import datetime
import pytz
from twilio.rest import Client

url: str = settings.SUPABASE_URL
key: str = settings.SUPABASE_KEY
supabase: Client = create_client(url, key)



@csrf_exempt
def sign_up_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse the JSON body of the request
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON data"}, status=400
            )

        email = data.get("email")
        password = data.get("password")

        # Step 1: Use Supabase's auth.sign_up to create the user
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
        })

        # Step 2: Extract user details from the response
        user_data = response.user
        user_id = user_data.id  # Supabase user ID (UUID)

        # Step 3: Create a Stripe Customer
        # stripe_customer = stripe.Customer.create(email=email, metadata={"supabase_user_id": user_id})

        #Step 4: Initial User Data
        insert_response = supabase.table('user_data').insert({
            'id': user_id,  # Use the UUID from authentication
            'email': email,  # Optional: Store email if needed
            # 'stripe_customer_id': stripe_customer['id'],  # Store Stripe customer ID
            'subscription_status': 'inactive',  # Default status
        }).execute()

        # Step 5: Return the response with user information
        return JsonResponse(
            {
                "message": "User created successfully",
                "user": {
                    "id": user_id,
                    "email": email,
                    "stripe_customer_id": "abc",
                },
            },
            status=201,
        )
    else:
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405,
        )
    

@csrf_exempt
def log_in_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse the JSON body of the request
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        email = data.get("email")
        password = data.get("password")
        response = supabase.auth.sign_in_with_password({"email": email, "password":  password})
        user_data = response.user
        user_id = user_data.id  # Supabase user ID (UUID)
        response = supabase.table("user_data").select("*").eq('email', email).execute()
        stripe_id = response.data[0]['stripe_customer_id']
        print(stripe_id)
        return JsonResponse(
            {
                "message": "User logged in successfully",
                "user": {
                    "id": user_id,
                    "email": email,
                    "stripe_customer_id": stripe_id
                },
            },
            status=201,
        )
    else:
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405,
        )

@csrf_exempt
def save_form_data(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse the JSON body of the request
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        print(data)
        questions = data.get("data")
        form_id = str(uuid.uuid4())
        form_url = "http://localhost:5200/" + form_id
        # Need to add this for auth users... do i need to?

        # supabase.table('form_data').insert({
        #     'form_data': questions,  # save questions
        #     'form_id': form_id,  # form_id
        #     'form_url': form_url
        # }).execute()
        supabase.table('form_data_customers').insert({
            'form_data': questions,  # save questions
            'form_id': form_id,  # form_id
            'form_url': form_url
        }).execute()

        return JsonResponse(
            {
                "message": "Form Created.",
            },
            status=201,
        )
    else:
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405,
        )
    
@csrf_exempt
def get_form_by_url(request, slug):
    try:
        # Retrieve the user data using the email
        form_url = "http://localhost:5200/" + slug
        response = supabase.table("form_data_customers").select("*").eq('form_url', form_url).execute()
        data_to_return = response.data[0]['form_data']
        print(data_to_return)
        return JsonResponse({"content": data_to_return}, status=200)

    except ObjectDoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)