from django.urls import path, include


app_name = 'comments'
urlpatterns = [
    path('api/v1/', include('comments.api.v1.urls')),
]