# Python imports
import requests

# Django imports
from django.conf import settings
from django.db.models import F

# Third party imports
from rest_framework import status
from rest_framework.response import Response

# Module imports
from .base import BaseAPIView
from plane.app.permissions.workspace import WorkspaceOwnerPermission
from plane.db.models import WorkspaceMember, Workspace, WorkspaceMemberInvite
from plane.authentication.utils.host import base_host
from plane.utils.exception_logger import log_exception
from plane.payment.utils.workspace_license_request import (
    resync_workspace_license,
)


class PaymentLinkEndpoint(BaseAPIView):
    permission_classes = [
        WorkspaceOwnerPermission,
    ]

    def post(self, request, slug):
        try:
            workspace = Workspace.objects.get(slug=slug)
            workspace_members = (
                WorkspaceMember.objects.filter(
                    workspace__slug=slug, is_active=True, member__is_bot=False
                )
                .annotate(
                    user_email=F("member__email"),
                    user_id=F("member__id"),
                    user_role=F("role"),
                )
                .values(
                    "user_email",
                    "user_id",
                    "user_role",
                )
            )

            for member in workspace_members:
                member["user_id"] = str(member["user_id"])

            product_id = request.data.get("product_id", False)
            price_id = request.data.get("price_id", False)

            if not product_id or not price_id:
                return Response(
                    {"error": "product_id and price_id are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if settings.PAYMENT_SERVER_BASE_URL:
                # Fetch the workspace license
                workspace_license_response = resync_workspace_license(
                    workspace_slug=slug
                )
                # Check if the workspace is on trial
                if workspace_license_response.get("is_on_trial"):
                    response = requests.post(
                        f"{settings.PAYMENT_SERVER_BASE_URL}/api/trial-subscriptions/upgrade/",
                        headers={
                            "content-type": "application/json",
                            "x-api-key": settings.PAYMENT_SERVER_AUTH_TOKEN,
                        },
                        json={
                            "workspace_id": str(workspace.id),
                            "stripe_price_id": price_id,
                            "members_list": list(workspace_members),
                            "slug": slug,
                        },
                    )
                    # Check if the response is successful
                    response.raise_for_status()
                    # Convert the response to json
                    response = response.json()
                    return Response(response, status=status.HTTP_200_OK)

                # Check if the workspace is on a paid plan
                else:
                    # Check the active paid users in the workspace - for self hosted plans
                    workspace_member_count = WorkspaceMember.objects.filter(
                        workspace__slug=slug,
                        is_active=True,
                        member__is_bot=False,
                        member__gt=10,
                    ).count()

                    invited_member_count = (
                        WorkspaceMemberInvite.objects.filter(
                            workspace__slug=slug,
                            role__gt=10,
                        ).count()
                    )

                    # Create the payment link
                    response = requests.post(
                        f"{settings.PAYMENT_SERVER_BASE_URL}/api/payment-link/",
                        headers={
                            "content-type": "application/json",
                            "x-api-key": settings.PAYMENT_SERVER_AUTH_TOKEN,
                        },
                        json={
                            "workspace_id": str(workspace.id),
                            "slug": slug,
                            "stripe_product_id": product_id,
                            "stripe_price_id": price_id,
                            "customer_email": request.user.email,
                            "members_list": list(workspace_members),
                            "required_seats": (
                                workspace_member_count + invited_member_count
                            ),
                        },
                    )
                    response.raise_for_status()
                    # Convert the response to json
                    response = response.json()
                    return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "error fetching payment link"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except requests.exceptions.RequestException as e:
            if e.response.status_code == 400:
                return Response(
                    e.response.json(),
                    status=status.HTTP_400_BAD_REQUEST,
                )
            log_exception(e)
            return Response(
                {"error": "error fetching payment link"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class WebsitePaymentLinkEndpoint(BaseAPIView):

    def post(self, request):
        try:
            # Get the workspace slug
            slug = request.data.get("slug", False)
            # Check if slug is present
            if not slug:
                return Response(
                    {"error": "slug is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # The user should be workspace admin
            if not WorkspaceMember.objects.filter(
                workspace__slug=slug,
                member=request.user,
                role=20,
                is_active=True,
            ).exists():
                return Response(
                    {"error": "You are not a admin of workspace"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Get the workspace
            workspace = Workspace.objects.get(slug=slug)

            # Get the workspace members
            workspace_members = (
                WorkspaceMember.objects.filter(
                    workspace__slug=slug, is_active=True, member__is_bot=False
                )
                .annotate(
                    user_email=F("member__email"),
                    user_id=F("member__id"),
                    user_role=F("role"),
                )
                .values(
                    "user_email",
                    "user_id",
                    "user_role",
                )
                .values("user_email", "user_id", "user_role")
            )

            # Convert the user_id to string
            for member in workspace_members:
                member["user_id"] = str(member["user_id"])

            # Check if the payment server base url is present
            if settings.PAYMENT_SERVER_BASE_URL:
                response = requests.post(
                    f"{settings.PAYMENT_SERVER_BASE_URL}/api/website/payment-link/",
                    headers={
                        "content-type": "application/json",
                        "x-api-key": settings.PAYMENT_SERVER_AUTH_TOKEN,
                    },
                    json={
                        "workspace_id": str(workspace.id),
                        "slug": slug,
                        "customer_email": request.user.email,
                        "members_list": list(workspace_members),
                        "host": base_host(request=request, is_app=True),
                    },
                )
                response.raise_for_status()
                response = response.json()
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "error fetching payment link"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except requests.exceptions.RequestException as e:
            log_exception(e)
            if e.response.status_code == 400:
                return Response(
                    e.response.json(),
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"error": "error fetching payment link"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class WorkspaceFreeTrialEndpoint(BaseAPIView):

    permission_classes = [
        WorkspaceOwnerPermission,
    ]

    def post(self, request, slug):
        try:
            # Get the product_id and price_id
            product_id = request.data.get("product_id", False)
            price_id = request.data.get("price_id", False)

            # Check if product_id and price_id are present
            if not product_id or not price_id:
                return Response(
                    {"error": "product_id and price_id are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get the workspace
            workspace = Workspace.objects.get(slug=slug)

            # Get the workspace members
            workspace_members = (
                WorkspaceMember.objects.filter(
                    workspace__slug=slug, is_active=True, member__is_bot=False
                )
                .annotate(
                    user_email=F("member__email"),
                    user_id=F("member__id"),
                    user_role=F("role"),
                )
                .values(
                    "user_email",
                    "user_id",
                    "user_role",
                )
                .values("user_email", "user_id", "user_role")
            )

            # Convert the user_id to string
            for member in workspace_members:
                member["user_id"] = str(member["user_id"])

            # Check if the payment server base url is present
            if settings.PAYMENT_SERVER_BASE_URL:
                response = requests.post(
                    f"{settings.PAYMENT_SERVER_BASE_URL}/api/trial-subscriptions/",
                    headers={
                        "content-type": "application/json",
                        "x-api-key": settings.PAYMENT_SERVER_AUTH_TOKEN,
                    },
                    json={
                        "workspace_id": str(workspace.id),
                        "slug": slug,
                        "customer_email": request.user.email,
                        "members_list": list(workspace_members),
                        "stripe_product_id": product_id,
                        "stripe_price_id": price_id,
                    },
                )
                # Check if the response is successful
                response.raise_for_status()
                # Convert the response to json
                response = response.json()
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "error upgrading trial subscriptions"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except requests.exceptions.RequestException as e:
            if e.response.status_code == 400:
                return Response(
                    e.response.json(),
                    status=status.HTTP_400_BAD_REQUEST,
                )
            log_exception(e)
            return Response(
                {"error": "error creating trial subscriptions"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class WorkspaceTrialUpgradeEndpoint(BaseAPIView):

    permission_classes = [
        WorkspaceOwnerPermission,
    ]

    def post(self, request, slug):
        try:
            # Get the product_id and price_id
            price_id = request.data.get("price_id", False)

            # Check if product_id and price_id are present
            if not price_id:
                return Response(
                    {"error": "price_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get the workspace members
            workspace_members = (
                WorkspaceMember.objects.filter(
                    workspace__slug=slug, is_active=True, member__is_bot=False
                )
                .annotate(
                    user_email=F("member__email"),
                    user_id=F("member__id"),
                    user_role=F("role"),
                )
                .values(
                    "user_email",
                    "user_id",
                    "user_role",
                )
                .values("user_email", "user_id", "user_role")
            )

            # Convert the user_id to string
            for member in workspace_members:
                member["user_id"] = str(member["user_id"])

            # Get the workspace
            workspace = Workspace.objects.get(slug=slug)

            # Check if the payment server base url is present
            if settings.PAYMENT_SERVER_BASE_URL:
                response = requests.post(
                    f"{settings.PAYMENT_SERVER_BASE_URL}/api/trial-subscriptions/upgrade/",
                    headers={
                        "content-type": "application/json",
                        "x-api-key": settings.PAYMENT_SERVER_AUTH_TOKEN,
                    },
                    json={
                        "workspace_id": str(workspace.id),
                        "stripe_price_id": price_id,
                        "members_list": list(workspace_members),
                        "slug": slug,
                    },
                )
                # Check if the response is successful
                response.raise_for_status()
                # Convert the response to json
                response = response.json()
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "error upgrading trial subscriptions"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except requests.exceptions.RequestException as e:
            if e.response.status_code == 400:
                return Response(
                    e.response.json(),
                    status=status.HTTP_400_BAD_REQUEST,
                )
            log_exception(e)
            return Response(
                {"error": "error upgrading trial subscriptions"},
                status=status.HTTP_400_BAD_REQUEST,
            )