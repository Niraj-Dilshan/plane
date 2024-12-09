# Python imports
import re

# Django imports
from django.db import models
from django.db.models import (
    Q,
    OuterRef,
    Subquery,
    Value,
    UUIDField,
    CharField,
    When,
    Case,
)
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.fields import ArrayField
from django.db.models.functions import Coalesce, Concat

# Third party imports
from rest_framework import status
from rest_framework.response import Response

# Module imports
from plane.app.views.base import BaseAPIView
from plane.db.models import (
    Workspace,
    Project,
    Issue,
    Cycle,
    Module,
    Page,
    IssueView,
    ProjectMember,
    ProjectPage,
)


class GlobalSearchEndpoint(BaseAPIView):
    """Endpoint to search across multiple fields in the workspace and
    also show related workspace if found
    """

    def filter_workspaces(self, query, slug, project_id, workspace_search):
        fields = ["name"]
        q = Q()
        for field in fields:
            q |= Q(**{f"{field}__icontains": query})
        return (
            Workspace.objects.filter(q, workspace_member__member=self.request.user)
            .distinct()
            .values("name", "id", "slug")
        )

    def filter_projects(self, query, slug, project_id, workspace_search):
        fields = ["name", "identifier"]
        q = Q()
        for field in fields:
            q |= Q(**{f"{field}__icontains": query})
        return (
            Project.objects.filter(
                q,
                project_projectmember__member=self.request.user,
                project_projectmember__is_active=True,
                archived_at__isnull=True,
                workspace__slug=slug,
            )
            .distinct()
            .values("name", "id", "identifier", "workspace__slug")
        )

    def filter_issues(self, query, slug, project_id, workspace_search):
        fields = ["name", "sequence_id", "project__identifier"]
        q = Q()
        for field in fields:
            if field == "sequence_id":
                # Match whole integers only (exclude decimal numbers)
                sequences = re.findall(r"\b\d+\b", query)
                for sequence_id in sequences:
                    q |= Q(**{"sequence_id": sequence_id})
            else:
                q |= Q(**{f"{field}__icontains": query})

        issues = Issue.issue_objects.filter(
            q,
            project__project_projectmember__member=self.request.user,
            project__project_projectmember__is_active=True,
            project__archived_at__isnull=True,
            workspace__slug=slug,
        )

        if workspace_search == "false" and project_id:
            issues = issues.filter(project_id=project_id)

        return issues.distinct().values(
            "name",
            "id",
            "sequence_id",
            "project__identifier",
            "project_id",
            "workspace__slug",
        )[:100]

    def filter_cycles(self, query, slug, project_id, workspace_search):
        fields = ["name"]
        q = Q()
        for field in fields:
            q |= Q(**{f"{field}__icontains": query})

        cycles = Cycle.objects.filter(
            q,
            project__project_projectmember__member=self.request.user,
            project__project_projectmember__is_active=True,
            project__archived_at__isnull=True,
            workspace__slug=slug,
        )

        if workspace_search == "false" and project_id:
            cycles = cycles.filter(project_id=project_id)

        return cycles.distinct().values(
            "name", "id", "project_id", "project__identifier", "workspace__slug"
        )

    def filter_modules(self, query, slug, project_id, workspace_search):
        fields = ["name"]
        q = Q()
        for field in fields:
            q |= Q(**{f"{field}__icontains": query})

        modules = Module.objects.filter(
            q,
            project__project_projectmember__member=self.request.user,
            project__project_projectmember__is_active=True,
            project__archived_at__isnull=True,
            workspace__slug=slug,
        )

        if workspace_search == "false" and project_id:
            modules = modules.filter(project_id=project_id)

        return modules.distinct().values(
            "name", "id", "project_id", "project__identifier", "workspace__slug"
        )

    def filter_pages(self, query, slug, project_id, workspace_search):
        fields = ["name"]
        q = Q()
        for field in fields:
            q |= Q(**{f"{field}__icontains": query})

        pages = (
            Page.objects.filter(
                q,
                projects__project_projectmember__member=self.request.user,
                projects__project_projectmember__is_active=True,
                projects__archived_at__isnull=True,
                workspace__slug=slug,
            )
            .annotate(
                project_ids=Coalesce(
                    ArrayAgg(
                        "projects__id", distinct=True, filter=~Q(projects__id=True)
                    ),
                    Value([], output_field=ArrayField(UUIDField())),
                )
            )
            .annotate(
                project_identifiers=Coalesce(
                    ArrayAgg(
                        "projects__identifier",
                        distinct=True,
                        filter=~Q(projects__id=True),
                    ),
                    Value([], output_field=ArrayField(CharField())),
                )
            )
        )

        if workspace_search == "false" and project_id:
            project_subquery = ProjectPage.objects.filter(
                page_id=OuterRef("id"), project_id=project_id
            ).values_list("project_id", flat=True)[:1]

            pages = pages.annotate(project_id=Subquery(project_subquery)).filter(
                project_id=project_id
            )

        return pages.distinct().values(
            "name", "id", "project_ids", "project_identifiers", "workspace__slug"
        )

    def filter_views(self, query, slug, project_id, workspace_search):
        fields = ["name"]
        q = Q()
        for field in fields:
            q |= Q(**{f"{field}__icontains": query})

        issue_views = IssueView.objects.filter(
            q,
            project__project_projectmember__member=self.request.user,
            project__project_projectmember__is_active=True,
            project__archived_at__isnull=True,
            workspace__slug=slug,
        )

        if workspace_search == "false" and project_id:
            issue_views = issue_views.filter(project_id=project_id)

        return issue_views.distinct().values(
            "name", "id", "project_id", "project__identifier", "workspace__slug"
        )

    def get(self, request, slug):
        query = request.query_params.get("search", False)
        workspace_search = request.query_params.get("workspace_search", "false")
        project_id = request.query_params.get("project_id", False)

        if not query:
            return Response(
                {
                    "results": {
                        "workspace": [],
                        "project": [],
                        "issue": [],
                        "cycle": [],
                        "module": [],
                        "issue_view": [],
                        "page": [],
                    }
                },
                status=status.HTTP_200_OK,
            )

        MODELS_MAPPER = {
            "workspace": self.filter_workspaces,
            "project": self.filter_projects,
            "issue": self.filter_issues,
            "cycle": self.filter_cycles,
            "module": self.filter_modules,
            "issue_view": self.filter_views,
            "page": self.filter_pages,
        }

        results = {}

        for model in MODELS_MAPPER.keys():
            func = MODELS_MAPPER.get(model, None)
            results[model] = func(query, slug, project_id, workspace_search)
        return Response({"results": results}, status=status.HTTP_200_OK)


class SearchEndpoint(BaseAPIView):
    def get(self, request, slug, project_id):
        query = request.query_params.get("query", False)
        query_type = request.query_params.get("query_type", "user_mention")
        count = int(request.query_params.get("count", 5))

        if query_type == "user_mention":
            fields = ["member__first_name", "member__last_name", "member__display_name"]
            q = Q()

            if query:
                for field in fields:
                    q |= Q(**{f"{field}__icontains": query})
            users = (
                ProjectMember.objects.filter(
                    q,
                    project__project_projectmember__member=self.request.user,
                    project__project_projectmember__is_active=True,
                    project_id=project_id,
                    workspace__slug=slug,
                )
                .annotate(
                    member__avatar_url=Case(
                        # If `avatar_asset` exists, use it to generate the asset URL
                        When(
                            member__avatar_asset__isnull=False,
                            then=Concat(
                                Value("/api/assets/v2/static/"),
                                "member__avatar_asset",  # Assuming avatar_asset has an id or relevant field
                                Value("/"),
                            ),
                        ),
                        # If `avatar_asset` is None, fall back to using `avatar` field directly
                        When(member__avatar_asset__isnull=True, then="member__avatar"),
                        default=Value(None),
                        output_field=models.CharField(),
                    )
                )
                .order_by("-created_at")
                .values("member__avatar_url", "member__display_name", "member__id")[
                    :count
                ]
            )

            return Response(users, status=status.HTTP_200_OK)

        if query_type == "project":
            fields = ["name", "identifier"]
            q = Q()

            if query:
                for field in fields:
                    q |= Q(**{f"{field}__icontains": query})
            projects = (
                Project.objects.filter(
                    q,
                    Q(project_projectmember__member=self.request.user) | Q(network=2),
                    workspace__slug=slug,
                )
                .order_by("-created_at")
                .distinct()
                .values("name", "id", "identifier", "logo_props", "workspace__slug")[
                    :count
                ]
            )
            return Response(projects, status=status.HTTP_200_OK)

        if query_type == "issue":
            fields = ["name", "sequence_id", "project__identifier"]
            q = Q()

            if query:
                for field in fields:
                    if field == "sequence_id":
                        # Match whole integers only (exclude decimal numbers)
                        sequences = re.findall(r"\b\d+\b", query)
                        for sequence_id in sequences:
                            q |= Q(**{"sequence_id": sequence_id})
                    else:
                        q |= Q(**{f"{field}__icontains": query})

            issues = (
                Issue.issue_objects.filter(
                    q,
                    project__project_projectmember__member=self.request.user,
                    project__project_projectmember__is_active=True,
                    workspace__slug=slug,
                    project_id=project_id,
                )
                .order_by("-created_at")
                .distinct()
                .values(
                    "name",
                    "id",
                    "sequence_id",
                    "project__identifier",
                    "project_id",
                    "priority",
                    "state_id",
                    "type_id",
                )[:count]
            )
            return Response(issues, status=status.HTTP_200_OK)

        if query_type == "cycle":
            fields = ["name"]
            q = Q()

            if query:
                for field in fields:
                    q |= Q(**{f"{field}__icontains": query})

            cycles = (
                Cycle.objects.filter(
                    q,
                    project__project_projectmember__member=self.request.user,
                    project__project_projectmember__is_active=True,
                    workspace__slug=slug,
                )
                .order_by("-created_at")
                .distinct()
                .values(
                    "name", "id", "project_id", "project__identifier", "workspace__slug"
                )[:count]
            )
            return Response(cycles, status=status.HTTP_200_OK)

        if query_type == "module":
            fields = ["name"]
            q = Q()

            if query:
                for field in fields:
                    q |= Q(**{f"{field}__icontains": query})

            modules = (
                Module.objects.filter(
                    q,
                    project__project_projectmember__member=self.request.user,
                    project__project_projectmember__is_active=True,
                    workspace__slug=slug,
                )
                .order_by("-created_at")
                .distinct()
                .values(
                    "name",
                    "id",
                    "project_id",
                    "project__identifier",
                    "status",
                    "workspace__slug",
                )[:count]
            )
            return Response(modules, status=status.HTTP_200_OK)

        if query_type == "page":
            fields = ["name"]
            q = Q()

            if query:
                for field in fields:
                    q |= Q(**{f"{field}__icontains": query})

            pages = (
                Page.objects.filter(
                    q,
                    projects__project_projectmember__member=self.request.user,
                    projects__project_projectmember__is_active=True,
                    projects__id=project_id,
                    workspace__slug=slug,
                    access=0,
                )
                .order_by("-created_at")
                .distinct()
                .values("name", "id", "logo_props", "projects__id", "workspace__slug")[
                    :count
                ]
            )
            return Response(pages, status=status.HTTP_200_OK)

        return Response(
            {"error": "Please provide a valid query"},
            status=status.HTTP_400_BAD_REQUEST,
        )
