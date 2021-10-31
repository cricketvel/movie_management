from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from movies import settings
import datetime, jwt


# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    created_on = models.DateTimeField(editable=False)
    updated_on = models.DateTimeField(editable=False)
    is_confirmed = models.BooleanField(default=False)
    role = models.CharField(max_length=255, blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_on = timezone.now()
            self.set_password(self.password)

        self.updated_on = timezone.now()
        return super(CustomUser, self).save(*args, **kwargs)


    @property
    def token(self):
        return self._generate_jwt_token()


    def _generate_jwt_token(self):
        dt = datetime.datetime.now() + datetime.timedelta(days=60)
        SECRET_KEY = settings.SECRET_KEY
        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')