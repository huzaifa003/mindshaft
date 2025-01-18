from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.serializers import serialize
from .models import Report
from users.models import CustomUser
from chats.models import Chat
import json

# Report List and Create View
@method_decorator(csrf_exempt, name='dispatch')
class ReportListCreateView(View):
    def get(self, request):
        """
        Get all reports.
        """
        reports = Report.objects.all()
        report_list = serialize('json', reports, fields=('user', 'chat', 'reason', 'created_at'))
        return JsonResponse({'reports': json.loads(report_list)}, safe=False)

    def post(self, request):
        """
        Create a new report.
        """
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            chat_id = data.get('chat_id')
            reason = data.get('reason')

            if not user_id or not chat_id or not reason:
                return JsonResponse({'error': 'User ID, Chat ID, and reason are required.'}, status=400)

            user = get_object_or_404(CustomUser, pk=user_id)
            chat = get_object_or_404(Chat, pk=chat_id, user=user)
            report = Report.objects.create(user=user, chat=chat, reason=reason)
            return JsonResponse({'message': 'Report created', 'report_id': report.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# Report Detail View (Retrieve, Update, Delete)
@method_decorator(csrf_exempt, name='dispatch')
class ReportDetailView(View):
    def get(self, request, report_id):
        """
        Retrieve a single report by ID.
        """
        report = get_object_or_404(Report, pk=report_id)
        return JsonResponse({
            'user': report.user.id,
            'chat': report.chat.id,
            'reason': report.reason,
            'created_at': report.created_at,
        })

    def put(self, request, report_id):
        """
        Update a report by ID.
        """
        report = get_object_or_404(Report, pk=report_id)
        try:
            data = json.loads(request.body)
            reason = data.get('reason')

            if not reason:
                return JsonResponse({'error': 'Reason is required.'}, status=400)

            report.reason = reason
            report.save()
            return JsonResponse({'message': 'Report updated'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def delete(self, request, report_id):
        """
        Delete a report by ID.
        """
        report = get_object_or_404(Report, pk=report_id)
        report.delete()
        return JsonResponse({'message': 'Report deleted'})
