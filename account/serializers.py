from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from rest_framework import serializers

User = get_user_model()


# class ProfileSerializer(serializers.Serializer):
#     class Meta:
#         Model = User
#         fields = '__all__'


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