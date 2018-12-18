from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication, permissions
from django.contrib.auth.models import User

from talentmap_api.feedback.models import FrontendSecrets, ReportedError, ReportedEvent


class ErrorView(APIView):
    """
    View to accept error reporting from the front end.
    """

    def post(self, request, public_secret, format=None):
        """
        Validates the request, then posts the data
        """
        feSecret = FrontendSecrets.objects.filter(public_secret=public_secret)

        if feSecret.count() != 1:
            return Response({"error": "Public secret not found", "success": False}, status=status.HTTP_403_FORBIDDEN)

        feSecret = feSecret[0]
        if not feSecret.is_authorized_request(request.data):
            return Response({"error": "Bad authorization", "success": False}, status=status.HTTP_403_FORBIDDEN)

        rError = ReportedError.objects.create(public_secret=public_secret,
                                              error=request.data.get("payload", {}))

        return Response({"error": None, "success": True}, status=status.HTTP_201_CREATED)


class EventView(APIView):
    """
    View to accept event reporting from the front end.
    """

    def post(self, request, public_secret, format=None):
        """
        Validates the request, then posts the data
        """
        feSecret = FrontendSecrets.objects.filter(public_secret=public_secret)

        if feSecret.count() != 1:
            return Response({"error": "Public secret not found", "success": False}, status=status.HTTP_403_FORBIDDEN)

        feSecret = feSecret[0]
        if not feSecret.is_authorized_request(request.data):
            return Response({"error": "Bad authorization", "success": False}, status=status.HTTP_403_FORBIDDEN)

        rError = ReportedEvent.objects.create(public_secret=public_secret,
                                              event=request.data.get("payload", {}))

        return Response({"error": None, "success": True}, status=status.HTTP_201_CREATED)
