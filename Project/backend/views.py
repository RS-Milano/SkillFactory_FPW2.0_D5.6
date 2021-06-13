from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Post, Author, Category, RegisterForm
from .filter import PostFilter

class PostList(ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'posts'
    ordering = ['-create_data']
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['limit_for_listing'] = Paginator(list(Post.objects.all()), 5).num_pages - 2
        context['all_posts'] = Post.objects.all()
        context['is_not_author'] = not self.request.user.groups.filter(name = 'authors').exists()
        return context

class FilteredPost(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'posts'
    ordering = ['-create_data']
    filterset_class = None
        
    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.all()

    def get_page_param(self):
        page_param = self.request.GET.get("page", None)
        return page_param

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['paginate'] = self.paginate_by
        context['all_posts'] = Post.objects.all()
        context['page_param'] = self.get_page_param()
        context['limit_for_listing'] = Paginator(list(Post.objects.all()), 5).num_pages - 2
        return context

class PostSearch(FilteredPost):
    filterset_class = PostFilter
    ordering = ['-create_data']
    paginate_by = 5

class AddPost(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Post
    template_name = 'addpost.html'
    permission_required = ('backend.add_post')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['authors'] = Author.objects.all()
        context['categories'] = Category.objects.all()
        context['new_post_id'] = len(Post.objects.all()) + 1
        return context

    def post(self, request, *args, **kwargs):
        title = request.POST['title']
        content = request.POST['content']
        author = request.POST['author']
        post_type = request.POST['post_type']
        category = request.POST['category']
        post = Post(author=Author.objects.get(user=author), title=title, content=content, post_type=post_type)
        post.save()
        post.category.add(Category.objects.get(category=category))
        return HttpResponseRedirect(f'{post.id}')

class PostDetail(DetailView):
    model = Post
    template_name = 'new.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name = 'authors').exists()
        return context

class PostEdit(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    fields = []
    template_name = 'editpost.html'
    context_object_name = 'post'
    permission_required = ('backend.change_post')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['authors'] = Author.objects.all()
        context['categories'] = Category.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        post = Post.objects.get(id=request.get_full_path().split("/")[2])
        post.title = request.POST['title']
        post.content = request.POST['content']
        post.author = Author.objects.get(id=request.POST['author'])
        post.post_type = request.POST['post_type']
        category = request.POST.get('category')
        if category:
            post.category.add(Category.objects.get(category=category))
        post.save()
        return HttpResponseRedirect(f"../{post.id}")

class DeletPost(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'deletpost.html'
    context_object_name = 'post'
    queryset = Post.objects.all()
    success_url = '/../../'

class PortalLogin(LoginView):
    template_name = 'login.html'

class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    success_url = '/'

@login_required
def be_author(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return redirect('/')
