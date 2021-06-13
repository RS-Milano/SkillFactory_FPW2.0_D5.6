from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django import forms
from allauth.account.forms import SignupForm

class Author(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    rating = models.IntegerField(default = 0)

    def update_rating(self):
        author_posts = Post.objects.filter(author = self.id)
        author_posts_rating = 0
        author_posts_comments_rating = 0
        for i in author_posts:
            author_posts_rating += i.rating * 3
            for j in Comment.objects.filter(post = i.id):
                author_posts_comments_rating += j.rating
        author_comments = Comment.objects.filter(author = self.id)
        author_comments_rating = 0
        for i in author_comments:
            author_comments_rating += i.rating
        self.rating = author_posts_rating + author_posts_comments_rating + author_comments_rating
        self.save()
    
    def __str__(self):
        return f'{self.user.username}'

class Category(models.Model):
    category = models.CharField(max_length = 255, unique = True)

    def __str__(self):
        return f'{self.category}'

class Post(models.Model):
    author = models.ForeignKey(Author, on_delete = models.CASCADE)
    my_post_type = [('article', 'article'), ('news', 'news')]
    post_type = models.CharField(max_length = 7, choices = my_post_type)
    create_data = models.DateTimeField(auto_now_add = True)
    title = models.CharField(max_length = 255)
    content = models.TextField()
    rating = models.IntegerField(default = 0)
    category = models.ManyToManyField(Category, through = 'PostCategory')

    def __str__(self):
        return f'{self.title} | {self.author} | {self.create_data} | {self.preview()}'

    def like(self):
        self.rating += 1
        self.save()
    
    def dislike(self):
        self.rating -= 1
        self.save()
    
    def preview(self):
        return self.content[0:124] + '...'

    def get_absolute_url(self):
        return f'/news/{self.id}'

class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    category = models.ForeignKey(Category, on_delete = models.CASCADE)

class Comment(models.Model):
    text = models.TextField()
    data = models.DateTimeField(auto_now_add = True)
    rating = models.IntegerField(default = 0)
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    author = models.ForeignKey(User, on_delete = models.CASCADE)

    def __str__(self):
        return f'{self.author} | {self.create_data}/n{self.text}'

    def like(self):
        self.rating += 1
        self.save()
    
    def dislike(self):
        self.rating -= 1
        self.save()
    
    def show(self):
        return f"{self.text} | {self.data} | rating {self.rating} | {self.author.username}"

class RegisterForm(UserCreationForm):
    email = forms.EmailField(label = "Email")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class MySignupForm(SignupForm):

    def save(self, request):
        user = super(MySignupForm, self).save(request)
        common_group = Group.objects.get(name='common')
        common_group.user_set.add(user)
        return user
