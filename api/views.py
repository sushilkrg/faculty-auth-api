from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Faculty
from .serializers import FacultySerializer
import face_recognition
import numpy as np
import json
import cv2
from PIL import Image
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# ✅ Admin Login API
@api_view(['POST'])
def admin_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    print(username, password)
    
    if username == "user1" and password == "123456":
        response = Response({'message': 'Login successful'})
        # ✅ Add CORS Headers to Login Response
        response["Access-Control-Allow-Origin"] = "https://facultyauth.vercel.app"
        response["Access-Control-Allow-Credentials"] = "true"
        return response

    response = Response({'message': 'Invalid credentials'}, status=401)
    response["Access-Control-Allow-Origin"] = "https://facultyauth.vercel.app"
    response["Access-Control-Allow-Credentials"] = "true"
    return response


# ✅ Admin Logout API
@api_view(['POST'])
def admin_logout(request):
    response = Response({'message': 'Logged out successfully'})
    response["Access-Control-Allow-Origin"] = "https://facultyauth.vercel.app"
    response["Access-Control-Allow-Credentials"] = "true"
    return response


# ✅ Faculty CRUD API (with CORS)
class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            faculty = serializer.save()
            
            # ✅ Process face encoding
            image = face_recognition.load_image_file(faculty.image.path)
            face_encodings = face_recognition.face_encodings(image)
            
            if len(face_encodings) > 0:
                faculty.face_encoding = face_encodings[0].tobytes()
                faculty.save()

                # ✅ Add CORS Headers
                response = Response(serializer.data, status=201)
                response["Access-Control-Allow-Origin"] = "https://facultyauth.vercel.app"
                response["Access-Control-Allow-Credentials"] = "true"
                return response
            else:
                faculty.delete()
                response = Response({'error': 'No face detected'}, status=400)
                response["Access-Control-Allow-Origin"] = "https://facultyauth.vercel.app"
                response["Access-Control-Allow-Credentials"] = "true"
                return response

        response = Response(serializer.errors, status=400)
        response["Access-Control-Allow-Origin"] = "https://facultyauth.vercel.app"
        response["Access-Control-Allow-Credentials"] = "true"
        return response


# ✅ Face Verification API (MOST IMPORTANT)
@csrf_exempt
def verify_face(request):
    # ✅ Handle Preflight (OPTIONS) Requests to Avoid CORS Errors
    if request.method == "OPTIONS":
        response = JsonResponse({"message": "Preflight OK"})
        response["Access-Control-Allow-Origin"] = "https://facultyauth.vercel.app"
        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Allow-Headers"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return response

    # ✅ Handle POST Request
    if request.method == "POST":
        if 'image' not in request.FILES:
            response = Response({'error': 'No image provided'}, status=400)
            response["Access-Control-Allow-Origin"] = "https://facultyauth.vercel.app"
            response["Access-Control-Allow-Credentials"] = "true"
            return response

        # ✅ Load and Encode Image
        image = face_recognition.load_image_file(request.FILES['image'])
        face_encodings = face_recognition.face_encodings(image)
        
        if len(face_encodings) == 0:
            response = Response({'error': 'No face detected'}, status=400)
            response["Access-Control-Allow-Origin"] = "https://facultyauth.vercel.app"
            response["Access-Control-Allow-Credentials"] = "true"
            return response
        
        unknown_encoding = face_encodings[0]
        
        # ✅ Compare Face Encodings
        for faculty in Faculty.objects.all():
            stored_encoding = np.frombuffer(faculty.face_encoding)
            result = face_recognition.compare_faces([stored_encoding], unknown_encoding)[0]
            
            if result:
                response = Response({
                    'match': True,
                    'faculty': {
                        'name': faculty.name,
                        'department': faculty.department
                    }
                })
                response["Access-Control-Allow-Origin"] = "https://facultyauth.vercel.app"
                response["Access-Control-Allow-Credentials"] = "true"
                return response

        # ✅ No Match Found
        response = Response({'match': False})
        response["Access-Control-Allow-Origin"] = "https://facultyauth.vercel.app"
        response["Access-Control-Allow-Credentials"] = "true"
        return response

    # ✅ Handle Invalid Requests
    response = Response({'error': 'Invalid request'}, status=400)
    response["Access-Control-Allow-Origin"] = "https://facultyauth.vercel.app"
    response["Access-Control-Allow-Credentials"] = "true"
    return response
