"""ChanLun URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from  Main import views

urlpatterns = [
    url(r'^main$', views.Main),
    url(r'^KXian$', views.KXian),
    url(r'^getOneData$', views.getOneData, name='getOneData'),
    url(r'^getUserId$', views.getUserId, name='getUserId'),
    url(r'^RealNewPrice$', views.getNewPrice, name='getNewPrice'),
    url(r'^ZXG_Recommend$', views.getZXG_Recommend, name='ZXG_Recommend'),
    url(r'^MyZXG$', views.getMyZXG, name='getMyZXG'),
    url(r'^OneQuotation$', views.getOneQuotation, name='getOneQuotation')
]
