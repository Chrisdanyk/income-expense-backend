
from rest_framework import views
from rest_framework.generics import GenericAPIView
from authentication.models import User
from authentication.serializers import RegisterSerializer, LoginSerializer, \
    VerifyEmailSerializer
from rest_framework import response, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from incomeexpenseapi.utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
import jwt
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Create your views here.


class AuthUserAPIView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = RegisterSerializer(user)
        return response.Response({"user": serializer.data})


class RegisterAPIView(GenericAPIView):
    serializer_class = RegisterSerializer
    authentication_classes = []

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user_data = serializer.data
            user = User.objects.get(email=user_data['email'])
            token = RefreshToken.for_user(user).access_token
            relativeLink = reverse('email-verify')
            current_site = get_current_site(request).domain
            absUrl = 'http://'+current_site+relativeLink+"?token="+str(token)
            email_body = f"Hi {user.username},\n\nPlease verify your email by \
                clicking the link below:\n\n{absUrl}\n\nThanks,\nThe Team"
            data = {"email_to": user.email, "email_body": email_body,
                    "email_subject": "Verify your emaail"}
            Util.send_email(subject=data["email_subject"],
                            body=data["email_body"],
                            recipients=[user.email])
            return response.Response(serializer.data,
                                     status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors,
                                 status.HTTP_400_BAD_REQUEST)


class VerifyEmail(views.APIView):
    serializer_class = VerifyEmailSerializer
    permission_classes = []

    @swagger_auto_schema(manual_parameters=[openapi.Parameter(
        name='token', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
        description='Token')])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms='HS256')
            user = User.objects.get(id=payload['user_id'])
            if not user.email_verified:
                user.email_verified = True
                user.save()
            return response.Response(
                {"message": "Email verified successfully"},
                status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return response.Response({"error": "Activation Expired"},
                                     status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError:
            return response.Response({"error": "Invalid Token"},
                                     status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer
    authentication_classes = []

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Response(data=serializer.data,
                                 status=status.HTTP_200_OK)
