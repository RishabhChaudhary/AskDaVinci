# pages/urls.py
from django.urls import path
from pages import views as pages_views

urlpatterns = [
    path("", pages_views.home_page_view, name="bot-home"),
    path("chatbot/", pages_views.bot_page_view, name="chatbot"),
]
