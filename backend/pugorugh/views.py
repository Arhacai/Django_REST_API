import os

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from . import models
from . import serializers
from . import utils


class UserRegisterView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    model = get_user_model()
    serializer_class = serializers.UserSerializer


class CreateDogView(generics.CreateAPIView):
    permission_classes = (permissions.IsAdminUser,)
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer


class DestroyDogView(generics.DestroyAPIView):
    permission_classes = (permissions.IsAdminUser,)
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer

    @staticmethod
    def delete_imagefile(dog):
        try:
            os.remove(str(dog.image_filename.file))
        except OSError:
            return None

    def get_object(self):
        try:
            dog = self.queryset.get(pk=self.kwargs.get('pk'))
        except ObjectDoesNotExist:
            return None
        else:
            return dog

    def destroy(self, request, *args, **kwargs):
        dog = self.get_object()
        if dog:
            models.UserDog.objects.filter(dog=dog).delete()
            self.delete_imagefile(dog)
            dog.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


class RetrieveDogView(generics.RetrieveAPIView):
    queryset = models.UserDog.objects.all()
    serializer_class = serializers.DogSerializer

    def get_queryset(self):
        return self.queryset.filter(
            user=self.request.user,
            status=self.kwargs.get('status')[0]
        )

    def get_object(self):
        userpref = models.UserPref.objects.get(user=self.request.user)
        dogs = models.Dog.objects.filter(
            age__in=utils.months_filter(userpref.age),
            gender__in=userpref.gender.split(','),
            size__in=userpref.size.split(','),
            behaviour__in=userpref.behaviour.split(',')
        )
        userdogs = self.get_queryset().filter(dog__in=dogs)
        pks = []
        for dog in userdogs:
            pks.append(dog.pk)

        if self.kwargs.get('pk') == '-1':
            try:
                return dogs.get(pk=pks[0])
            except IndexError or ObjectDoesNotExist:
                return None

        for pk in pks:
            if pk > int(self.kwargs.get('pk')):
                return dogs.get(pk=pk)
            elif pk == int(self.kwargs.get('pk')) and pk == pks[-1]:
                return dogs.get(pk=pks[0])
        return None

    def get(self, request, *args, **kwargs):
        dog = self.get_object()
        if dog:
            serializer = serializers.DogSerializer(dog)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)


class RetrieveUpdateUserPrefView(generics.RetrieveUpdateAPIView):
    queryset = models.UserPref.objects.all()
    serializer_class = serializers.UserPrefSerializer

    def get_object(self):
        return self.queryset.get(user=self.request.user)


class UpdateUserDogView(generics.UpdateAPIView):
    queryset = models.UserDog.objects.all()
    serializer_class = serializers.UserDogSerializer

    def get_object(self):
        try:
            return self.queryset.get(
                user=self.request.user,
                dog=models.Dog.objects.get(pk=self.kwargs.get('pk'))
            )
        except ObjectDoesNotExist:
            return None

    def put(self, request, *args, **kwargs):
        userdog = self.get_object()
        if userdog:
            userdog.status = kwargs['status'][0]
            userdog.save()
            serializer = serializers.UserDogSerializer(userdog)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)
