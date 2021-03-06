from django.contrib.auth.models import User
from django.core.validators import validate_email
from rest_framework import serializers
from taggit.models import Tag
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)
from .models import Type, Person


class CustomEmailField(serializers.Field):
    def get_attribute(self, obj):
        return obj

    def to_representation(self, obj):  # GET
        person = obj.person_set.first()
        if person.public_email or obj == self.context['request'].user:
            return obj.email
        else:
            return ""

    def to_internal_value(self, data):  # POST
        if data:
            validate_email(data)
        return data


class UserSerializer(serializers.ModelSerializer):
    email = CustomEmailField()

    class Meta:
        model = User
        fields = ("last_login", "first_name", "last_name", "email")


class UserTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Type
        fields = "__all__"


class PersonSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    user = UserSerializer()

    class Meta:
        model = Person
        fields = "__all__"

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        instance = super().update(instance, validated_data)
        instance.user.first_name = user_data.get('first_name', instance.user.first_name)
        instance.user.last_name = user_data.get('last_name', instance.user.last_name)
        instance.user.email = user_data.get('email', instance.user.email)
        instance.user.save()
        return instance

class TagSerialiser(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = "__all__"
