from base64 import b64encode
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import *
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404, JsonResponse
from rest_framework import status
import requests
from django.conf import settings
from rest_framework.generics import CreateAPIView, ListAPIView, get_object_or_404
from rest_framework.views import APIView
from .serializers import Register, UserSerializer, CollectionSerializer
from .middleware import getcount, reset


class RequestHit(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        url = settings.THIRD_PARTY_MOVIE_API
        credentials = f"{settings.CLIENT_ID}:{settings.CLIENT_SECRET}"
        encoded_credentials = str(b64encode(credentials.encode("utf-8")), "utf-8")

        response = requests.get(url, headers={"Authorization": f"Basic {encoded_credentials}"}, params=request.GET)
        if response.status_code != 200 or 'is_success' in response.json():
            response = requests.get(url, headers={"Authorization": f"Basic {encoded_credentials}"}, params=request.GET)
        return HttpResponse(response)


class RegisterUser(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = Register


class CollectionAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        collections = Collection.objects.filter(user=request.user)
        serializer = CollectionSerializer(collections, many=True)
        response = {"is_success": True, "data": {"collections": serializer.data,
                                                 "favourite_genres": Collection.get_collection_genres(collections)}}
        return JsonResponse(response, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CollectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CollectionEdit(APIView):
    permission_classes = [IsAuthenticated, ]

    def get_object(self, pk):
        try:
            return Collection.objects.get(pk=pk)
        except Collection.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        _collection = self.get_object(pk)
        serializer = CollectionSerializer(_collection)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        _collection = self.get_object(pk)
        serializer = CollectionSerializer(_collection, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        _collection = self.get_object(pk)
        _collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RequestCount(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        try:
            return JsonResponse({"requests": getcount()})
        except Exception as exception:
            return JsonResponse(
                {"is_success": False, "error": "Unable to get request count now", "detail": (str(exception))},
                status=500)


class RequestReset(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            if reset() == 0:
                return JsonResponse({"message": "request count reset successfully"})
            else:
                raise Exception("Exception is there.")

        except Exception as exception:
            return JsonResponse(
                {"is_success": False, "error": "Unable to reset request count now", "detail": (str(exception))},
                status=500)
