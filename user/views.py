from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from .serializers import UserSerializer, ChangePasswordSerializer, UserUpdateSerializer
from .models import CustomUser
from rest_framework.permissions import AllowAny

from api.mixins import UserQuerySetMixin


class UserCreateAPIView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserUpdateAPIView(UserQuerySetMixin, generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateSerializer

    def get_object(self):
        obj = self.request.user
        return obj

    def perform_update(self, serializer):
        instance = serializer.save()


class UserDestroyAPIView(UserQuerySetMixin, generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        obj = self.request.user
        return obj

    def perform_destroy(self, instance):
        # instance
        super().perform_destroy(instance)


class UserPasswordUpdateAPIView(UserQuerySetMixin, generics.UpdateAPIView):
    # queryset = CustomUser.objects.all()
    serializer_class = ChangePasswordSerializer
    model = CustomUser

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                "status": "success",
                "code": status.HTTP_200_OK,
                "message": "Password updated successfully",
                "data": [],
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def perform_update(self, serializer):
    #     instance = serializer.save()
