from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from apps.users.models import User


class UserAdminSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    username = serializers.CharField(
            max_length=32,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    password = serializers.CharField(
            min_length=8,
            write_only=True,
            )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            role=validated_data['role'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserMemberSerializer(UserAdminSerializer):
    role = serializers.ChoiceField(choices=[User.MEMBER])


class UserManagerSerializer(UserAdminSerializer):
    role = serializers.ChoiceField(choices=[User.MEMBER, User.MANAGER])


class UserAdminUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']
        read_only_fields = ['username']


class UserManagerUpdateSerializer(UserAdminUpdateSerializer):
    role = serializers.ChoiceField(choices=[User.MEMBER, User.MANAGER])


class UserMemberUpdateSerializer(UserAdminUpdateSerializer):
    role = serializers.ChoiceField(choices=[User.MEMBER])
