from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegistrationSerializer


class RegistrationView(APIView):
    """API view for user registration."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Creates a new user and returns authentication data."""

        try:
            serializer = RegistrationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            token = Token.objects.create(user=user)

            return Response(
                self._get_auth_response_data(user, token),
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as error:
            return Response(
            error.detail,
            status=status.HTTP_400_BAD_REQUEST,
        )
        except Exception:
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


    def _get_auth_response_data(self, user, token):
        """Builds the authentication response payload."""

        return {
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": user.id,
        }



class LoginView(APIView):
    """API view for user login."""

    permission_classes = [AllowAny]
    

    def post(self, request):
        """Authenticates a user and returns authentication data."""

        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)

            return Response(
                self._get_auth_response_data(user, token),
                status=status.HTTP_200_OK,
            )
        except ValidationError as error:
            return Response(
                error.detail,
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"detail": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_auth_response_data(self, user, token):
        """Builds the authentication response payload."""

        return {
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": user.id,
        }