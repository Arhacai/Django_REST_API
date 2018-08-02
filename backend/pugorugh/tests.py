import mock as mock
from django.test import TestCase

# Create your tests here.
from .views import age_filter, DestroyDogView
from .models import Dog

class AgeFilterTests(TestCase):

    def test_age_filter(self):
        age = "b,y,a,s"
        result = age_filter(age)
        self.assertEqual(len(result), len(list(range(0, 240))))


class DestroyDogViewTests(TestCase):

    @mock.patch('os.remove')
    def test_delete_imagefile_success(self, fake_remove):
        view = DestroyDogView()
        dog = mock.Mock()
        dog.image_filename = mock.Mock()
        dog.image_filename.file = "dogs/412.jpg"
        view.delete_imagefile(dog)
        self.assertIsNone(fake_remove.assert_called_with("dogs/412.jpg"))

    @mock.patch('os.remove')
    def test_delete_imagefile_failed(self, fake_remove):
        view = DestroyDogView()
        dog = mock.Mock()
        dog.image_filename = mock.Mock()
        dog.image_filename.file = "dogs/412.jpg"
        fake_remove.side_effect = [OSError]
        result = view.delete_imagefile(dog)
        self.assertIsNone(result)

    def test_get_object_success(self):
        view = DestroyDogView()
        view.kwargs = {'pk': 1}
        view.queryset.get = Dog(name='Nero')
        import ipdb; ipdb.set_trace()
        result = view.get_object()
        self.assertEqual(result.name, 'Nero')