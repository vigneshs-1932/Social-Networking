from django.urls import path, include

urlpatterns = [
    path('api/users/', include('users.urls')),
]
