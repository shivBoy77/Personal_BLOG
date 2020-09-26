from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 4


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 4

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'image', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user 
        messages.success(self.request, 'Post Created Successfully')
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'image', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post Updated Successfully')
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    success_message = "Post was deleted successfully."

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
        

def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})


def get_user_profile(request, username):
    user = User.objects.get(username=username)
    return render(request, 'blog/user_profile.html', {"user":user})

# added for search

def search(request):
    
    query =  request.GET.get('q')
    if query:
        queryset = (Q(title__icontains=query) |
            Q(image__icontains=query) |
            Q(author__username__icontains=query) |
            Q(date_posted__icontains=query) |
            Q(content__icontains=query))
        results = Post.objects.all().filter(queryset).distinct()
    else:
        results = []
    return render(request, 'blog/search_results.html', {'results':results, 'query':query})



