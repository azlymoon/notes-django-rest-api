from django.contrib import admin
from django.urls import path, include

from myapp.views import CreateNoteAPIView, RetrieveNoteAPIView, UpdateNoteAPIView, DestroyNoteAPIView, ListNoteAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('notes/', ListNoteAPIView.as_view(), name='list_note'),
    path('notes/create/', CreateNoteAPIView.as_view(), name='create_note'),
    path('notes/<int:pk>/', RetrieveNoteAPIView.as_view(), name='retrieve_note'),
    path('notes/<int:pk>/update/', UpdateNoteAPIView.as_view(), name='update_note'),
    path('notes/<int:pk>/delete/', DestroyNoteAPIView.as_view(), name='delete_note'),
]
