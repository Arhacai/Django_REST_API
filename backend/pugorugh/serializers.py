from django.contrib.auth import get_user_model
from rest_framework import serializers

from . import models
from . import utils


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
    image_filename = utils.Base64ImageField(max_length=None, use_url=True)

    def create(self, validated_data):
        dog = models.Dog.objects.create(**validated_data)
        users = models.User.objects.all()
        for user in users:
            models.UserDog.objects.create(user=user, dog=dog, status='u')
        return dog

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
