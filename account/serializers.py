from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from rest_framework import serializers

User = get_user_model()


class ProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not instance.first_name and not instance.last_name:
            representation['full_name'] = 'Анонимный пользователь'
        return representation


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, required=True)
    password_confirm = serializers.CharField(min_length=6, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Такой пользователь уже зарегистрирован')
        return email

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Пароли не совпадают')
        return attrs

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.create_activation_code()
        user.send_activation_email(user.email, user.activation_code)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password, request=self.context.get('request'))
            if not user:
                raise serializers.ValidationError('Неверно указаны данные')
        else:
            raise serializers.ValidationError('Заполните пустые поля')
        attrs['user'] = user
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Нет такого пользователя')
        return email

    def send_new_password(self):
        email = self.validated_data.get('email')
        new_pass = get_random_string(length=8)
        user = User.objects.get(email=email)
        user.set_password(new_pass)
        user.save()
        send_mail(
            'Восстановление пароля',
            f'Ваш новый пароль: {new_pass}',
            'test@gmail.com',
            [email]
        )


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    new_password = serializers.CharField(min_length=6, required=True)
    new_password_confirm = serializers.CharField(min_length=6, required=True)

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Нет такого пользователя')
        return email

    def validate_old_pass(self, old_password):
        request = self.context.get('request')
        if not request.user.check_password(old_password):
            raise serializers.ValidationError('Неправильный пароль')
        return old_password

    def validate(self, attrs):
        print(attrs)
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.pop('new_password_confirm')
        if new_password != new_password_confirm:
            raise serializers.ValidationError('Пароли не совпадают')
        return attrs

    def set_new_password(self, request):
        # request = self.context.get('request')
        new_password = self.validated_data.get('new_password')
        print(request)
        user = request.user
        user.set_password(new_password)
        user.save()