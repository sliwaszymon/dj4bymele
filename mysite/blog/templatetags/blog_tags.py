from django import template
from django.db.models import Count
from ..models import Post
from django.utils.safestring import mark_safe
import markdown

register = template.Library()


@register.simple_tag
def total_posts():
    return Post.published.count()


@register.inclusion_tag('blog/post/lastest_posts.html')
def show_lastest_posts(count=5):
    lastest_posts = Post.published.order_by('-publish')[:count]
    return {'lastest_posts': lastest_posts}


@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]


@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))
