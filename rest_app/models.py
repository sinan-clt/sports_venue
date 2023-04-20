from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, username, name=None, email=None, password=None, phone_number=None):
        if not username:
            raise ValueError('User must have an username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            name=name,
            phone_number=phone_number
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, name=None, email=None):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            name=name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_superadmin = True
        user.is_staff = True
        user.is_customer = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='photos/users', blank=True, null=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True, null=True)
    phone_number = models.CharField(max_length=50, unique=True, null=True)
    gender = models.CharField(max_length=15, blank=True, null=True)

    # required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_gmail_authenticated = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'

    objects = UserManager()

    def __str__(self):
        return self.username

    class Meta:
        db_table = "django_user"

# models.py



class Venue(models.Model):
    name = models.CharField(max_length=100)
    venue_type = models.CharField(max_length=100)



class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.CharField(max_length=20)
