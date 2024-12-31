from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from .models import Blog
import json

@csrf_exempt
def blog_list(request):
    """
    Handles listing all blogs and creating a new blog.
    """
    if request.method == 'GET':
        blogs = Blog.objects.all()
        blog_list = [{
            'id': blog.id,
            'title': blog.title,
            'content': blog.content,
            'image': blog.image.url if blog.image else None,
            'uploaded_at': blog.uploaded_at,
            'updated_at': blog.updated_at,
        } for blog in blogs]
        return JsonResponse({'blogs': blog_list}, safe=False)

    elif request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        content = data.get('content')
        image = request.FILES.get('image') if request.FILES else None

        if not title or not content:
            return JsonResponse({'error': 'Title and content are required.'}, status=400)

        blog = Blog.add_blog(title=title, content=content, image=image)
        return JsonResponse({'message': 'Blog created successfully.', 'id': blog.id})


@csrf_exempt
def blog_detail(request, blog_id):
    """
    Handles retrieving, updating, and deleting a specific blog.
    """
    blog = get_object_or_404(Blog, id=blog_id)

    if request.method == 'GET':
        return JsonResponse({
            'id': blog.id,
            'title': blog.title,
            'content': blog.content,
            'image': blog.image.url if blog.image else None,
            'uploaded_at': blog.uploaded_at,
            'updated_at': blog.updated_at,
        })

    elif request.method == 'PUT':
        data = json.loads(request.body)
        title = data.get('title')
        content = data.get('content')
        image = request.FILES.get('image') if request.FILES else None

        blog.update_blog(title=title, content=content, image=image)
        return JsonResponse({'message': 'Blog updated successfully.'})

    elif request.method == 'DELETE':
        blog.delete_blog()
        return JsonResponse({'message': 'Blog deleted successfully.'})


def filter_blogs_by_date(request):
    """
    Filters blogs by a date range.
    """
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date or not end_date:
        return JsonResponse({'error': 'Start date and end date are required.'}, status=400)

    try:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
    except ValueError:
        return JsonResponse({'error': 'Invalid date format.'}, status=400)

    blogs = Blog.filter_by_date(start_date=start_date, end_date=end_date)
    blog_list = [{
        'id': blog.id,
        'title': blog.title,
        'content': blog.content,
        'image': blog.image.url if blog.image else None,
        'uploaded_at': blog.uploaded_at,
        'updated_at': blog.updated_at,
    } for blog in blogs]
    return JsonResponse({'blogs': blog_list}, safe=False)
