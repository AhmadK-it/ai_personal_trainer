from rest_framework import serializers

class DirectoryPathSerializer(serializers.Serializer):
    directory_path = serializers.CharField(max_length=1024)
