"""
Django settings for moosejawums project.

Generated by 'django-admin startproject' using Django 5.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
<<<<<<< HEAD
import environ
from django.contrib.messages import constants as messages

=======
>>>>>>> ed3138ec107aa2896907dd9325c20890e674d891

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-es69i(7)fprqd79ygg@am*+mt7_nhj^kxrxuq-z0pk$b-s=zba'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#necessary for CSRF to function properly
CSRF_TRUSTED_ORIGINS = [
<<<<<<< HEAD
    #'https://teammoosejaw-c8akbmb3dffbhjct.centralus-01.azurewebsites.net','https://168.61.217.214'
     "http://127.0.0.1",
    "http://localhost"

]
# ALLOWED_HOSTS = ["teammoosejaw-c8akbmb3dffbhjct.centralus-01.azurewebsites.net", "168.61.217.214", "127.0.0.1"]
ALLOWED_HOSTS = ["127.0.0.1","localhost"]
=======
    'https://teammoosejaw-c8akbmb3dffbhjct.centralus-01.azurewebsites.net','https://168.61.217.214'
]
ALLOWED_HOSTS = ["teammoosejaw-c8akbmb3dffbhjct.centralus-01.azurewebsites.net", "168.61.217.214", "127.0.0.1"]
>>>>>>> ed3138ec107aa2896907dd9325c20890e674d891


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
<<<<<<< HEAD
    'ums'
=======
>>>>>>> ed3138ec107aa2896907dd9325c20890e674d891
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
]

ROOT_URLCONF = 'moosejawums.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.csrf',
            ],
        },
    },
]

WSGI_APPLICATION = 'moosejawums.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mjapp',
        'HOST': 'moosejawdb.mysql.database.azure.com',
        'PORT': '3306',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'USER': os.environ.get('DB_USER'),

    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


<<<<<<< HEAD
# Microsoft Auth API Settings
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

MICROSOFT_AUTH = {
    'TENANT_ID': env('TENANT_ID', default="common"),
    'CLIENT_ID': env('CLIENT_ID'),
    'CLIENT_SECRET': env('CLIENT_SECRET'),
    'REDIRECT_URI': "http://localhost:8000/auth/callback/",
    'AUTHORITY': "https://login.microsoftonline.com/common",
    'SCOPE': ["User.Read"]
}


=======
>>>>>>> ed3138ec107aa2896907dd9325c20890e674d891
# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR /'static']


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

<<<<<<< HEAD
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

MESSAGE_TAGS = {
    messages.ERROR: "danger",
    messages.SUCCESS: "success",
    messages.INFO: "info",
    messages.WARNING: "warning",
}
=======
>>>>>>> ed3138ec107aa2896907dd9325c20890e674d891

