from django.contrib.auth.models import User
from django.db import models


class Dog(models.Model):
    GENDER_CHOICES = (
        ('m', 'male'),
        ('f', 'female'),
        ('u', 'unknown'),
    )
    SIZE_CHOICES = (
        ('s', 'small'),
        ('m', 'medium'),
        ('l', 'large'),
        ('xl', 'extra large'),
        ('u', 'unknown'),
    )
    BEHAVIOUR_CHOICES = (
        ('c', 'confident'),
        ('s', 'shy'),
        ('i', 'independent'),
        ('h', 'happy'),
        ('a', 'aggressive'),
        ('u', 'unknown')
    )

    name = models.CharField(max_length=100, default='Unnamed')
    image_filename = models.CharField(max_length=100, default='')
    breed = models.CharField(max_length=100, default='Unknown')
    age = models.IntegerField(default=1, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='u')
    size = models.CharField(max_length=1, choices=SIZE_CHOICES, default='u')
    behaviour = models.CharField(max_length=1, choices=BEHAVIOUR_CHOICES, default='u')

    def __str__(self):
        return self.name.title()


class UserDog(models.Model):
    STATUS_CHOICES = (
        ('l', 'liked'),
        ('d', 'disliked'),
        ('u', 'undecided')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)

    def __str__(self):
        return "{} actually {} {}".format(self.user.username.title(), self.get_status_display(), self.dog.name.title())


class UserPref(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    age = models.CharField(
        max_length=7,
        help_text="Options are: 'b,y,a,s' for baby, young, adult and senior.",
        default='b,y,a,s'
    )
    gender = models.CharField(
        max_length=3,
        help_text="Options are: 'm,f' for male and female.",
        default='m,f'
    )
    size = models.CharField(
        max_length=8,
        help_text="Options are 's,m,l,xl' for small, medium, large and extra large",
        default='s,m,l,xl'
    )
    behaviour = models.CharField(
        max_length=11,
        help_text="Options are 'c,s,i,h,a' for confident, shy, independent, happy and aggressive.",
        default='c,s,i,h,a'
    )

    def __str__(self):

        return "{} preferences: Age ({}), Gender ({}), Size ({}), Behaviour ({})".format(
            self.user.username.title(),
            self.age,
            self.gender,
            self.size,
            self.behaviour
        )
