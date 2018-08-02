import mock as mock

from django.test import TestCase, RequestFactory

from . import models
from . import serializers
from . import utils
from . import views


################
#  TEST VIEWS  #
################


class DestroyDogViewTests(TestCase):

    def setUp(self):
        self.view = views.DestroyDogView()
        self.dog1 = models.Dog.objects.create(name="testdog")
        self.dog2 = models.Dog.objects.create(name="otherdog")
        self.user = models.User.objects.create(
            username='user',
            password='password'
        )
        self.userdog = models.UserDog.objects.create(
            user=self.user,
            dog=self.dog1,
            status='l'
        )

    @mock.patch('os.remove')
    def test_delete_imagefile_success(self, fake_remove):
        dog = mock.Mock()
        dog.image_filename = mock.Mock()
        dog.image_filename.file = "dogs/412.jpg"
        self.view.delete_imagefile(dog)
        self.assertIsNone(fake_remove.assert_called_with("dogs/412.jpg"))

    @mock.patch('os.remove')
    def test_delete_imagefile_failed(self, fake_remove):
        dog = mock.Mock()
        dog.image_filename = mock.Mock()
        dog.image_filename.file = "dogs/412.jpg"
        fake_remove.side_effect = [OSError]
        result = self.view.delete_imagefile(dog)
        self.assertIsNone(result)

    def test_get_object_success(self):
        self.view.kwargs = {'pk': 1}
        dog = self.view.get_object()
        self.assertEqual(dog.name, 'testdog')

    def test_get_object_failed(self):
        self.view.kwargs = {'pk': 3}
        dog = self.view.get_object()
        self.assertIsNone(dog)

    @mock.patch('pugorugh.views.DestroyDogView.delete_imagefile')
    def test_destroy_success(self, fake_delete):
        self.view.kwargs = {'pk': 1}
        self.view.request = RequestFactory()
        response = self.view.destroy(self.view.request)
        self.assertEqual(response.status_code, 204)

    def test_destroy_failed(self):
        self.view.kwargs = {'pk': 3}
        self.view.request = RequestFactory()
        response = self.view.destroy(self.view.request)
        self.assertEqual(response.status_code, 404)

    def tearDown(self):
        self.dog1.delete()
        self.dog2.delete()


class RetrieveDogViewTests(TestCase):

    def setUp(self):
        self.view = views.RetrieveDogView()
        self.view.request = RequestFactory()
        self.user = models.User.objects.create(
            username='user',
            password='password'
        )
        self.dog1 = models.Dog.objects.create(
            name="testdog",
            gender='f',
            age=10,
            size='xl',
            behaviour='h'
        )
        self.dog2 = models.Dog.objects.create(
            name="otherdog",
            gender='m',
            age=18,
            size='s',
            behaviour='c'
        )
        self.userdog1 = models.UserDog.objects.create(
            user=self.user,
            dog=self.dog1,
            status='l'
        )
        self.userdog2 = models.UserDog.objects.create(
            user=self.user,
            dog=self.dog2,
            status='l'
        )
        self.userpref = models.UserPref.objects.create(
            user=self.user,
            age='b,y',
            gender='m,f',
            size='s,xl',
            behaviour='c,i,h'
        )

    def test_get_queryset(self):
        self.view.kwargs = {'status': 'liked'}
        self.view.request.user = self.user
        userdog = self.view.get_queryset()
        self.assertEqual(userdog[0].dog.name, 'testdog')
        self.assertEqual(userdog.count(), 2)

    def test_get_object_negative_pk(self):
        self.view.kwargs = {'pk': '-1', 'status': 'liked'}
        self.view.request.user = self.user
        dog = self.view.get_object()
        self.assertEqual(dog.name, 'testdog')

    def test_get_object_negative_pk_failed(self):
        self.view.kwargs = {'pk': '-1', 'status': 'disliked'}
        self.view.request.user = self.user
        dog = self.view.get_object()
        self.assertIsNone(dog)

    def test_get_object_next_dog(self):
        self.view.kwargs = {'pk': '1', 'status': 'liked'}
        self.view.request.user = self.user
        dog = self.view.get_object()
        self.assertEqual(dog.name, 'otherdog')

    def test_get_object_repeat_first_dog(self):
        self.view.kwargs = {'pk': '2', 'status': 'liked'}
        self.view.request.user = self.user
        dog = self.view.get_object()
        self.assertEqual(dog.name, 'testdog')

    def test_get_object_none(self):
        self.view.kwargs = {'pk': '5', 'status': 'liked'}
        self.view.request.user = self.user
        dog = self.view.get_object()
        self.assertIsNone(dog)

    def test_get_none(self):
        self.view.kwargs = {'pk': '5', 'status': 'liked'}
        self.view.request.user = self.user
        response = self.view.get(self.view.request)
        self.assertEqual(response.status_code, 404)

    def test_get_success(self):
        self.view.kwargs = {'pk': '1', 'status': 'liked'}
        self.view.request.user = self.user
        response = self.view.get(self.view.request)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.userdog1.delete()
        self.userdog2.delete()
        self.userpref.delete()
        self.user.delete()
        self.dog1.delete()
        self.dog2.delete()


class RetrieveUpdateUserPrefView(TestCase):

    def setUp(self):
        self.view = views.RetrieveUpdateUserPrefView()
        self.view.request = RequestFactory()
        self.user = models.User.objects.create(
            username='user',
            password='password'
        )
        self.userpref = models.UserPref.objects.create(
            user=self.user,
            age='b,y',
            gender='m,f',
            size='s,xl',
            behaviour='c,i,h'
        )

    def test_get_object(self):
        self.view.request.user = self.user
        userpref = self.view.get_object()
        self.assertEqual(userpref.behaviour, 'c,i,h')

    def tearDown(self):
        self.userpref.delete()
        self.user.delete()


class UpdateUserDogViewTests(TestCase):

    def setUp(self):
        self.view = views.UpdateUserDogView()
        self.view.request = RequestFactory()
        self.user = models.User.objects.create(
            username='user',
            password='password'
        )
        self.dog = models.Dog.objects.create(
            name="testdog",
            gender='f',
            age=10,
            size='xl',
            behaviour='h'
        )
        self.userdog = models.UserDog.objects.create(
            user=self.user,
            dog=self.dog,
            status='l'
        )
        self.userpref = models.UserPref.objects.create(
            user=self.user,
            age='b,y',
            gender='m,f',
            size='s,xl',
            behaviour='c,i,h'
        )

    def test_get_object_success(self):
        self.view.request.user = self.user
        self.view.kwargs = {'pk': '1'}
        userdog = self.view.get_object()
        self.assertEqual(userdog.status, 'l')

    def test_get_object_none(self):
        self.view.request.user = self.user
        self.view.kwargs = {'pk': '5'}
        userdog = self.view.get_object()
        self.assertIsNone(userdog)

    def test_put_success(self):
        self.view.request.user = self.user
        self.view.kwargs = {'pk': '1'}
        kwargs = {'status': 'undecided'}
        response = self.view.put(self.view.request, **kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertIn('u', response.data['status'])

    def test_put_failed(self):
        self.view.request.user = self.user
        self.view.kwargs = {'pk': '3'}
        kwargs = {'status': 'undecided'}
        response = self.view.put(self.view.request, **kwargs)
        self.assertEqual(response.status_code, 404)

    def tearDown(self):
        self.userdog.delete()
        self.userpref.delete()
        self.user.delete()
        self.dog.delete()


#################
#  TEST MODELS  #
#################

class DogModelTests(TestCase):

    def setUp(self):
        self.dog = models.Dog.objects.create(name="testdog")

    def test__str__(self):
        self.assertEqual(str(self.dog), 'Testdog')

    def tearDown(self):
        self.dog.delete()


class UserDogModelTests(TestCase):

    def setUp(self):
        self.user = models.User.objects.create(
            username='user',
            password='password'
        )
        self.dog = models.Dog.objects.create(name="testdog")
        self.userdog = models.UserDog.objects.create(
            user=self.user,
            dog=self.dog,
            status='l'
        )

    def test__str__(self):
        self.assertEqual(str(self.userdog), 'Testdog status is liked by User')

    def tearDown(self):
        self.userdog.delete()
        self.user.delete()
        self.dog.delete()


class UserPrefModelTests(TestCase):

    def setUp(self):
        self.user = models.User.objects.create(
            username='user',
            password='password'
        )
        self.userpref = models.UserPref.objects.create(
            user=self.user,
            age='b',
            gender='f',
            size='xl',
            behaviour='h'
        )

    def test__str__(self):
        self.assertEqual(str(self.userpref), 'User preferences: Age (b), Gender (f), Size (xl), Behaviour (h)')

    def tearDown(self):
        self.userpref.delete()
        self.user.delete()


######################
#  TEST SERIALIZERS  #
######################

class UserSerializerTests(TestCase):

    def setUp(self):
        self.dog1 = models.Dog.objects.create(name="testdog")
        self.dog2 = models.Dog.objects.create(name="otherdog")

    def test_create(self):
        data = {'username': 'user', 'password': 'password'}
        serializer = serializers.UserSerializer()
        self.user = serializer.create(validated_data=data)
        self.userdogs = models.UserDog.objects.all()
        self.assertEqual(self.user.username, 'user')
        self.assertEqual(self.userdogs.count(), 2)

    def tearDown(self):
        self.user.delete()
        self.userdogs.delete()
        self.dog1.delete()
        self.dog2.delete()


class DogSerializerTests(TestCase):

    def setUp(self):
        self.user1 = models.User.objects.create(
            username='user1',
            password='password'
        )
        self.user2 = models.User.objects.create(
            username='user2',
            password='password'
        )

    def test_create(self):
        data = {'name': 'testdog'}
        serializer = serializers.DogSerializer()
        self.dog = serializer.create(validated_data=data)
        self.userdogs = models.UserDog.objects.all()
        self.assertEqual(self.userdogs.count(), 2)

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.userdogs.delete()
        self.dog.delete()


################
#  TEST UTILS  #
################

class MonthFilterTests(TestCase):

    def test_month_filter(self):
        age = "b,y,a,s"
        result = utils.months_filter(age)
        self.assertEqual(len(result), len(list(range(0, 240))))
