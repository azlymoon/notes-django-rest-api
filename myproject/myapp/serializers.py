from rest_framework import serializers
from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    is_owner = serializers.SerializerMethodField()
    username_owner = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = ('id', 'title', 'content', 'user', 'created_at', 'is_owner', 'username_owner')

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return request.user == obj.user

    def get_username_owner(self, obj):
        return obj.user.username
