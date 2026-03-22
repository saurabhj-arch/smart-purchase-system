from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import RecentlyViewed
from .serializers import RegisterSerializer, UserProfileSerializer, RecentlyViewedSerializer


def get_tokens_for_user(user):
    """Helper: generate JWT access + refresh tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


# ── Register ────────────────────────────────────────────────────────────────
@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    """
    POST /api/accounts/register/
    Body: { name, email, username, password, phone }
    Returns: { access, refresh, user }
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response({
            **tokens,
            "user": UserProfileSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Login ───────────────────────────────────────────────────────────────────
@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """
    POST /api/accounts/login/
    Body: { username, password }
    Returns: { access, refresh, user }
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if user:
        tokens = get_tokens_for_user(user)
        return Response({
            **tokens,
            "user": UserProfileSerializer(user).data
        })
    return Response({"error": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)


# ── Profile ─────────────────────────────────────────────────────────────────
@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    GET  /api/accounts/profile/  → return logged-in user's details
    PATCH /api/accounts/profile/ → update name / email
    """
    if request.method == "GET":
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    elif request.method == "PATCH":
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Recently Viewed ──────────────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def recently_viewed(request):
    """
    GET /api/accounts/recently-viewed/
    Returns the last 10 products the user viewed, newest first.
    """
    items = RecentlyViewed.objects.filter(user=request.user).select_related("product").order_by("-viewed_at")[:10]
    serializer = RecentlyViewedSerializer(items, many=True)
    return Response(serializer.data)