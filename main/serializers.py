from rest_framework import serializers

from .models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('title', )


class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class PostAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not instance.first_name and not instance.last_name:
            representation['full_name'] = 'Анонимный пользователь'
        return representation


class PostSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d/%m/%y %H:%M:%S', read_only=True)

    class Meta:
        model = Post
        exclude = ('author', )

    def get_rating(self, instance):
        total_rating = sum(instance.ratings.values_list('rating', flat=True))
        rating_count = instance.ratings.count()
        rating = total_rating / rating_count if rating_count > 0 else 0
        return round(rating, 1)

    def get_like(self, instance):
        total_like = sum(instance.likes.values_list('is_liked', flat=True))
        like = total_like if total_like > 0 else 0
        return like

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['category'] = CategorySerializer(instance.category).data
        repr['author'] = PostAuthorSerializer(instance.author).data
        repr['likes'] = self.get_like(instance)
        repr['rating'] = self.get_rating(instance)
        repr['images'] = ImageSerializer(instance.images.all(), many=True, context=self.context).data
        print(repr)
        repr['comment'] = CommentSerializer(instance.comments.all(), many=True, context=self.context).data
        return repr

    def create(self, validated_data):
        request = self.context.get('request')
        print(request.data)
        user_id = request.user.id
        validated_data['author_id'] = user_id
        post = Post.objects.create(**validated_data)
        return post


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

    def _get_image_url(self, obj):
        if obj.image:
            url = obj.image.url
            request = self.context.get('request')
            if request is not None:
                url = request.build_absolute_uri(url)
        else:
            url = ''
        return url

    def destroy(self, validated_data):
        request = self.context.get('request')
        print(request.data)
        user = request.user.id
        print(user)
        validated_data['author_id'] = user
        image = Image.objects.delete(**validated_data)
        return image

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image'] = self._get_image_url(instance)
        return representation


class CommentAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not instance.first_name and not instance.last_name:
            representation['full_name'] = 'Анонимный пользователь'
        return representation


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ('id', 'author')

    def validate(self, attrs):
        request = self.context.get('request')
        attrs['author'] = request.user
        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = CommentAuthorSerializer(instance.author).data
        return representation


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        exclude = ('id', 'author', 'created_at')

    def validate_post(self, post):
        request = self.context.get('request')
        if post.ratings.filter(author=request.user).exists():
            raise serializers.ValidationError('Вы не можете поставить вторую оценку на пост')
        return post

    def validate_rating(self, rating):
        if not rating in range(1, 6):
            raise serializers.ValidationError('Рейтинг должен быть от 1 до 5')
        return rating

    def validate(self, attrs):
        request = self.context.get('request')
        attrs['author'] = request.user
        return attrs


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        print(instance)
        representation['favorites'] = PostSerializer(Post.objects.filter(favorites=instance.id),
                                                     many=True, context=self.context).data
        return representation

