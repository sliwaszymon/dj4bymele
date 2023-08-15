from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.views.generic import ListView
from django.views.decorators.http import require_POST
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm


# def post_list(request):
#     post_list_query = Post.published.all()
#     paginator = Paginator(post_list_query, 3)
#     page_number = request.GET.get('page', 1)
#     try:
#         posts = paginator.page(page_number)
#     except PageNotAnInteger:
#         # Jak numer strony nie jest liczbą zwraca pierwszą stronę
#         posts = paginator.page(1)
#     except EmptyPage:
#         # Jak numer strony wykracza poza zakres to zwraca ostatnią stronę
#         posts = paginator.page(paginator.num_pages)
#     return render(request, 'blog/post/list.html', {'posts': posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED, slug=post, publish__year=year,
                             publish__month=month, publish__day=day)
    comments = post.comments.filter(active=True)
    form = CommentForm()

    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments,
                                                     'form': form})


def post_share(request, post_id):
    # Pobierz post wg. identyfikatora
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f'{cd["name"]} zaleca Ci przeczytanie {post.title}'
            message = f'Przeczytaj {post.title} pod adresem {post_url}\n\n komentarze {cd["name"]}: {cd["comments"]}'
            send_mail(subject, message, 'twoje_konto@gmail.com', [cd["to"]])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Tworzy obiekt comment bez zapisywania w bazie danych
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form,
                                                      'comment': comment})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'
