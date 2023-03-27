from rest_framework.test import APITestCase
from authentication.models import User
from django.urls import reverse


class TestSetup(APITestCase):

    def setUp(self):
        self.login_url = reverse('login')
        self.register_url = reverse('register')

        self.user_data = {
            'username': "username",
            'email': "email@test.com",
            "password": "password1@212"
            }
        return super().setUp()

    def register_user(self):
        return User.objects.create_user(**self.user_data)


class TestModel(APITestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            'test', 'test@domain.com', 'passWord@//123')
        self.assertIsInstance(user, User)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.email, 'test@domain.com')

    def test_raises_error_when_no_username_is_supplied(self):
        self.assertRaises(ValueError, User.objects.create_user, username='',
                          email='test@domain.com',
                          password='passWord@//123')

    def test_raises_with_message_when_no_email_is_supplied(self):
        with self.assertRaisesMessage(
                ValueError, 'The given email must be set'):
            User.objects.create_user(username='username',
                                     email='',
                                     password='passWord@//123')

    def test_raises_with_message_when_no_username_is_supplied(self):
        with self.assertRaisesMessage(ValueError,
                                      'The given username must be set'):
            User.objects.create_user(username='',
                                     email='email@domain.test',
                                     password='passWord@//123')

    def test_create_super_user_with_is_staff_status(self):
        with self.assertRaisesMessage(ValueError,
                                      'Superuser must have is_staff=True.'):
            User.objects.create_superuser(username='',
                                          email='email@domain.test',
                                          password='passWord@//123',
                                          is_staff=False)

    def test_create_super_user_with_super_user_status(self):
        with self.assertRaisesMessage(
                ValueError,
                'Superuser must have is_superuser=True.'):
            User.objects.create_superuser(username='',
                                          email='email@domain.test',
                                          password='passWord@//123',
                                          is_superuser=False)

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            username='test', email='test@domain.com', password='PassWord12!',
            is_superuser=True)
        self.assertIsInstance(user, User)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.email, 'test@domain.com')
