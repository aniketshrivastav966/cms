# CReated view part
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from cms_project.permissions import IsAdminOrAuthor
from .models import *
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class SignUpAPIView(APIView):
    def post(self, request):
        try:
            request.data['is_staff'] = True
            request.data['is_active'] = True
            request.data['password'] = make_password(request.data['password'])
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Author signup successfully.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class CustomRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        # Add custom claims
        token['user_id'] = user.id
        return token

class LoginView(APIView):
    def post(self, request):
        try:
            # Validate the login data
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Get the user from the serializer
            user = serializer.validated_data['user']
            refresh = CustomRefreshToken.for_user(user)
            access_token = refresh.access_token
            
            return Response({
                "message": "Login successfully.",
                "access_token": str(access_token),
                "refresh_token": str(refresh)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ContentViewSet(ModelViewSet):
    queryset = Content.objects.all().order_by('id')
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrAuthor]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Content.objects.all().order_by('id') 
        return Content.objects.filter(created_by=user).order_by('id')
    
    def create(self, request, *args, **kwargs):
        try:
            # Create a mutable copy of the request data
            data = request.data.copy()
            
            # Add the created_by field
            data['created_by'] = request.user.email
            
            # Pass the modified data to the serializer
            serializer = self.get_serializer(data=data) 
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response({'message': 'Content created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    def partial_update(self, request, pk=None):
        try:
            user = Content.objects.get(pk=pk)
            serializer = ContentSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
            return Response({'message':"Content update successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # DELETE: Delete a user
    def destroy(self, request, pk=None):
        try:
            user = Content.objects.get(pk=pk)
        except Content.DoesNotExist:
            return Response({"error": "Content not found"}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response({"message": "Content deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
