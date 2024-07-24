from django.urls import path

from .views import (
    ProductEndpoint,
    PaymentLinkEndpoint,
    WorkspaceProductEndpoint,
    WebsitePaymentLinkEndpoint,
    WebsiteUserWorkspaceEndpoint,
    SubscriptionEndpoint,
)

urlpatterns = [
    path(
        "workspaces/<str:slug>/products/",
        ProductEndpoint.as_view(),
        name="products",
    ),
    path(
        "workspaces/<str:slug>/current-plan/",
        WorkspaceProductEndpoint.as_view(),
        name="products",
    ),
    path(
        "workspaces/<str:slug>/payment-link/",
        PaymentLinkEndpoint.as_view(),
        name="products",
    ),
    path(
        "website/payment-link/",
        WebsitePaymentLinkEndpoint.as_view(),
        name="website-payment-link",
    ),
    path(
        "website/workspaces/",
        WebsiteUserWorkspaceEndpoint.as_view(),
        name="website-workspaces",
    ),
    path(
        "workspaces/<str:slug>/subscriptions/",
        SubscriptionEndpoint.as_view(),
        name="subscription",
    ),
]