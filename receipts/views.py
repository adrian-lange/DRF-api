from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics
from django.contrib.auth.decorators import login_required
from django.http import FileResponse

from .models import Receipt
from user.models import CustomUser
from .serializers import ReceiptSerializer

from api.mixins import UserQuerySetMixin


class ReceiptListCreateAPIView(UserQuerySetMixin, generics.ListCreateAPIView):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer

    def perform_create(self, serializer):
        user = CustomUser.objects.get(id=self.request.user.id)
        serializer.save(user=user)

    # def get_queryset(self, *args, **kwargs):
    #     qs = super().get_queryset(*args, **kwargs)
    #     reques = self.request
    #     return qs.filter(user=request.user)


class ReceiptDetailAPIView(UserQuerySetMixin, generics.RetrieveAPIView):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer


class ReceiptUpdateAPIView(UserQuerySetMixin, generics.UpdateAPIView):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    lookup_field = "pk"

    def perform_update(self, serializer):
        instance = serializer.save()


class ReceiptDestroyAPIView(UserQuerySetMixin, generics.DestroyAPIView):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    lookup_field = "pk"

    def perform_destroy(self, instance):
        # instance
        super().perform_destroy(instance)


# class ReceiptMixinView(
#     mixins.CreateModelMixin,
#     mixins.ListModelMixin,
#     mixins.RetrieveModelMixin,
#     generics.GenericAPIView
#     ):
#     queryset = Receipt.objects.all()
#     serializer_class = ReceiptSerializer
#     lookup_field = 'pk'

#     def get(self, request, *args, **kwargs):
#         print(args, kwargs)
#         pk = kwargs.get("pk")
#         if pk is not None:
#             return self.retrieve(request, *args, *kwargs)
#         return self.list(request, *args, *kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, *kwargs)


@login_required
@api_view(["GET"])
def secure_file(request, path):
    user = request.user.id
    try:
        queryset = Receipt.objects.get(file=path, user__id=user)
        response = FileResponse(queryset.file)
        return response
    except ValueError:
        return Response({"detail": "Not found."}, status=404)
