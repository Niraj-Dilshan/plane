# views.py

import requests
from django.http import JsonResponse
from django.conf import settings

from plane.payment.views.base import BaseAPIView


class FeatureFlagProxyEndpoint(BaseAPIView):

    def get(self, request, slug):
        url = f"{settings.FEATURE_FLAG_SERVER_BASE_URL}/api/feature-flags/"
        json = {"workspace_slug": slug, "user_id": str(request.user.id)}
        headers = {
            "content-type": "application/json",
            "x-api-key": settings.FEATURE_FLAG_SERVER_AUTH_TOKEN,
        }
        response = requests.post(url, json=json, headers=headers)
        response.raise_for_status()
        return JsonResponse(response.json(), status=response.status_code)