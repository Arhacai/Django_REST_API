from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, permissions
from rest_framework.response import Response

from . import models
from . import serializers


def age_filter(ages):
    filter = []
    if 'b' in ages:
        filter.extend(list(range(0, 12)))
    if 'y' in ages:
        filter.extend(list(range(12, 24)))
    if 'a' in ages:
        filter.extend(list(range(24, 96)))
    if 's' in ages:
        filter.extend(list(range(96, 240)))
    return filter


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

    def get_object(self):
        try:
            return self.queryset.get(pk=self.kwargs.get('pk'))
        except ObjectDoesNotExist:
            return Response(status=404)


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
            age__in=age_filter(userpref.age),
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

    def get(self, request, pk, status, format=None):
        dog = self.get_object()
        if dog:
            serializer = serializers.DogSerializer(dog)
            return Response(serializer.data)
        return Response(status=404)


class RetrieveUpdateUserPrefView(generics.RetrieveUpdateAPIView):
    queryset = models.UserPref.objects.all()
    serializer_class = serializers.UserPrefSerializer

    def get_object(self):
        return self.get_queryset().get(user=self.request.user)


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

    def put(self, request, pk, status, format=None):
        userdog = self.get_object()
        if userdog:
            userdog.status = status[0]
            userdog.save()
            serializer = serializers.UserDogSerializer(userdog)
            return Response(serializer.data)
        return Response(status=404)
