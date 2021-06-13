from django.urls import path, include
from django.contrib.auth.views import LogoutView
from .views import PostList, PostDetail, PostSearch, AddPost, PostEdit, DeletPost, PortalLogin, RegisterView, be_author

urlpatterns = [
    path('', PostList.as_view()),
    path('<int:pk>', PostDetail.as_view()),
    path('search', PostSearch.as_view()),
    path('addpost', AddPost.as_view()),
    path('<int:pk>/edit', PostEdit.as_view()),
    path('<int:pk>/delet', DeletPost.as_view()),
    # path('login', PortalLogin.as_view()),
    # path('signup', RegisterView.as_view(template_name = 'signup.html')),
    # path('logout', LogoutView.as_view(template_name = 'news.html')),
    path('accounts/', include('allauth.urls')),
    path('upgrade/', be_author)
]
