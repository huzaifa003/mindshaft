from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.serializers import serialize
from .models import Feedback
from users.models import CustomUser
import json

# Feedback List and Create View
@method_decorator(csrf_exempt, name='dispatch')
class FeedbackListCreateView(View):
    def get(self, request):
        """
        Get all feedbacks.
        """
        feedbacks = Feedback.objects.all()
        feedback_list = serialize('json', feedbacks, fields=('user', 'feedback', 'created_at'))
        return JsonResponse({'feedbacks': json.loads(feedback_list)}, safe=False)

    def post(self, request):
        """
        Create a new feedback.
        """
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            feedback_text = data.get('feedback')

            if not user_id or not feedback_text:
                return JsonResponse({'error': 'User ID and feedback are required'}, status=400)

            user = get_object_or_404(CustomUser, pk=user_id)
            feedback = Feedback.objects.create(user=user, feedback=feedback_text)
            return JsonResponse({'message': 'Feedback created', 'feedback_id': feedback.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# Feedback Detail View (Retrieve, Update, Delete)
@method_decorator(csrf_exempt, name='dispatch')
class FeedbackDetailView(View):
    def get(self, request, feedback_id):
        """
        Retrieve a single feedback by ID.
        """
        feedback = get_object_or_404(Feedback, pk=feedback_id)
        return JsonResponse({
            'user': feedback.user.id,
            'feedback': feedback.feedback,
            'created_at': feedback.created_at,
        })

    def put(self, request, feedback_id):
        """
        Update a feedback by ID.
        """
        feedback = get_object_or_404(Feedback, pk=feedback_id)
        try:
            data = json.loads(request.body)
            feedback_text = data.get('feedback')

            if not feedback_text:
                return JsonResponse({'error': 'Feedback text is required'}, status=400)

            feedback.feedback = feedback_text
            feedback.save()
            return JsonResponse({'message': 'Feedback updated'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def delete(self, request, feedback_id):
        """
        Delete a feedback by ID.
        """
        feedback = get_object_or_404(Feedback, pk=feedback_id)
        feedback.delete()
        return JsonResponse({'message': 'Feedback deleted'})
