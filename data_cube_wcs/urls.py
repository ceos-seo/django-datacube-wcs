from django.conf.urls import url, include

from . import views

urlpatterns = [url(r'^', views.WebService.as_view(), name='web_service')]
