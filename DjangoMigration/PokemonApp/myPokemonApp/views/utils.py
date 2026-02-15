from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import loader
import django_tables2 as tables
from django.db.models import Q, Count
from collections import Counter
from django.contrib.auth.models import User
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django import forms
from celery.result import AsyncResult
from celery.signals import task_prerun, task_postrun
from bs4 import BeautifulSoup
from jinja2 import Environment, PackageLoader, select_autoescape
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.html import mark_safe
from myPokemonApp.models import *
from django.template.loader import render_to_string
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils import translation
from django.template.defaultfilters import date as lazy_date
import logging



### Auth decorators

def no_login(function):
    def wrapper(request, *args, **kwargs):
        return function(request, *args, **kwargs)
    return wrapper

def user_is_authenticated(function):
    #class call or method call, needs self or not
    if len(function.__qualname__.split("."))> 1:
        def wrapper(self, request, *args, **kwargs):
            if not request.user.is_authenticated: 
                return render(request, '404.html')
            else:
                return function(self, request, *args, **kwargs)
    else:
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated: 
                return render(request, '404.html')
            else:
                return function(request, *args, **kwargs)
    return wrapper

def user_is_superuser(function):
    if len(function.__qualname__.split("."))> 1:
        def wrapper(self, request, *args, **kwargs):
            if not request.user.is_superuser:
                return render(request, '404.html')
            else:
                return function(self, request, *args, **kwargs)
    else:
        def wrapper(request, *args, **kwargs):
            if not request.user.is_superuser:
                return render(request, '404.html')
            else:
                return function(request, *args, **kwargs)
    return wrapper