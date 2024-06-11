from django.urls import path, include

"""
Defines the URL patterns for the API endpoints related to users.
The 'users.urls' module is included to handle the URL routing for user-related functionality.
"""
urlpatterns = [
    path('api/users/', include('users.urls')),
]
