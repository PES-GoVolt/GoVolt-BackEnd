from rest_framework import serializers

from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
     class Meta:
        model = CustomUser
        fields = ['username','first_name','last_name', 'photo_url', 'phone', 'email', 'id']