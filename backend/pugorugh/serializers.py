from django.contrib.auth import get_user_model

from rest_framework import serializers

from . import models


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = get_user_model().objects.create(
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()

        models.UserPref.objects.create(user=user)

        for dog in models.Dog.objects.all():
            models.UserDog.objects.create(user=user, dog=dog, status='u')

        return user

    class Meta:
        model = get_user_model()


class DogSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'id',
            'name',
            'image_filename',
            'breed',
            'age',
            'gender',
            'size',
            'behaviour'
        )
        model = models.Dog


class UserPrefSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'age',
            'gender',
            'size',
            'behaviour'
        )
        model = models.UserPref


class UserDogSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'dog',
            'status'
        )
        model = models.UserDog