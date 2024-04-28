from datetime import timedelta
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import Note
from rest_framework.generics import CreateAPIView, ListAPIView, DestroyAPIView, \
    RetrieveAPIView, UpdateAPIView
from .permissions import IsOwner
from .serializers import NoteSerializer


class NoteFilter(filters.FilterSet):
    min_date = filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    max_date = filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')

    class Meta:
        model = Note
        fields = ['user', 'min_date', 'max_date']


class ListNoteAPIView(ListAPIView):
    """
    get:
    Retrieves a list of notes.

    Optional query parameters:
    - `user`: Filter by the user id who created the note.
    - `min_date`: Minimum date for the created notes (inclusive).
    - `max_date`: Maximum date for the created notes (inclusive).

    The list is sorted by the date of creation, starting with the most recent.

    Permission:
    - Authenticated users can view all their notes.
    - Unauthenticated users receive a 403 Forbidden response.
    """
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = NoteFilter

    def get_serializer_context(self):
        context = super(ListNoteAPIView, self).get_serializer_context()
        context.update({"request": self.request})
        return context


class RetrieveNoteAPIView(RetrieveAPIView):
    """
    get:
    Retrieves a specific note by ID.

    Permission:
    - Authenticated users can retrieve their own notes.
    - Unauthenticated users receive a 403 Forbidden response.
    """
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Note.DoesNotExist:
            return Response({'error': 'Note not found.'}, status=status.HTTP_404_NOT_FOUND)


class CreateNoteAPIView(CreateAPIView):
    """
    post:
    Creates a new note.

    Permission:
    - Authenticated users can create a note.
    - Unauthenticated users receive a 403 Forbidden response.
    """
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UpdateNoteAPIView(UpdateAPIView):
    """
    put:
    Updates an existing note. Note can only be edited within one day of creation.

    Permission:
    - Authenticated users can only update their own notes.

    The note's `created_at` date must be within the last 24 hours for the note to be editable.
    """
    serializer_class = NoteSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        try:
            note = self.get_object()
        except Note.DoesNotExist:
            return Response({'error': 'Note not found.'}, status=status.HTTP_404_NOT_FOUND)

        if note.created_at < timezone.now() - timedelta(days=1):
            return Response({
                'error': 'You can only edit a note for one day after it has been created.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DestroyNoteAPIView(DestroyAPIView):
    """
    delete:
    Deletes a specific note.

    Permission:
    - Authenticated users can only delete their own notes.
    """
    serializer_class = NoteSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Note.DoesNotExist:
            return Response({'error': 'Note not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
