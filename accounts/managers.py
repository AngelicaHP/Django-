from django.contrib.auth.models import BaseUserManager
from . import constants as user_constants

class UserManager(BaseUserManager):
    def create_user(self, email, perfil, mobile, password=None, **extra_fields):
        if not perfil:
            raise ValueError('Se requiere el perfil del usuario')
        if not email:
            raise ValueError('El email es obligatorio')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            perfil=perfil,
            mobile=mobile,
            **extra_fields
        )

        if not password:
            # Si no se especifica, se genera una contraseña aleatoria
            password = self.make_random_password(length=8, allowed_chars="abcdefghjkmnpqrstuvwxyz0123456789")

        user.set_password(password)

        user.is_superuser = extra_fields.get('is_superuser', False)
        user.is_staff = extra_fields.get('is_staff', True)
        user.is_active = extra_fields.get('is_active', True)

        user.save(using=self._db)
        return user

    def create_superuser(self, email, perfil, mobile, password=None, **extra_fields):
        if not perfil:
            raise ValueError('Se requiere el perfil del usuario')

        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('perfil', user_constants.ADMINISTRADOR)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email=email, perfil=perfil, mobile=mobile, password=password, **extra_fields)

    def update_user(self, data_user):
        iduser = data_user.get('username')
        return self.filter(pk=iduser).update(
            full_name=data_user.get('full_name'),
            email=self.normalize_email(data_user.get('email')),
            perfil=data_user.get('perfil_id'),
            mobile=data_user.get('mobile')
        )
        return usuario

