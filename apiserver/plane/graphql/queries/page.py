# Third-Party Imports
import strawberry
from asgiref.sync import sync_to_async

# Strawberry Imports
from strawberry.types import Info
from strawberry.permission import PermissionExtension

# Django Imports
from django.db.models import Exists, OuterRef, Q

# Module Imports
from plane.graphql.types.page import PageType
from plane.db.models import UserFavorite, Page
from plane.graphql.permissions.project import ProjectBasePermission


@strawberry.type
class PageQuery:

    @strawberry.field(
        extensions=[PermissionExtension(permissions=[ProjectBasePermission()])]
    )
    async def pages(
        self, info: Info, slug: str, project: strawberry.ID
    ) -> list[PageType]:
        subquery = UserFavorite.objects.filter(
            user=info.context.user,
            entity_type="page",
            entity_identifier=OuterRef("pk"),
            workspace__slug=slug,
        )
        pages = await sync_to_async(list)(
            Page.objects.filter(workspace__slug=slug, projects__id=project)
            .filter(
                projects__project_projectmember__member=info.context.user,
                projects__project_projectmember__is_active=True,
                projects__archived_at__isnull=True,
            )
            .filter(parent__isnull=True)
            .filter(Q(owned_by=info.context.user) | Q(access=0))
            .select_related("workspace", "owned_by")
            .prefetch_related("projects")
            .annotate(is_favorite=Exists(subquery))
        )
        return pages

    @strawberry.field(
        extensions=[PermissionExtension(permissions=[ProjectBasePermission()])]
    )
    async def page(
        self,
        info: Info,
        slug: str,
        project: strawberry.ID,
        page: strawberry.ID,
    ) -> PageType:
        user = info.context.user

        # Build subquery for UserFavorite
        subquery = UserFavorite.objects.filter(
            user=user,
            entity_type="page",
            entity_identifier=OuterRef("pk"),
            workspace__slug=slug,
        )

        # Build the query
        query = (
            Page.objects.filter(
                workspace__slug=slug, projects__id=project, pk=page
            )
            .filter(
                projects__project_projectmember__member=user,
                projects__project_projectmember__is_active=True,
                projects__archived_at__isnull=True,
            )
            .filter(parent__isnull=True)
            .filter(Q(owned_by=user) | Q(access=0))
            .select_related("workspace", "owned_by")
            .prefetch_related("projects")
            .annotate(is_favorite=Exists(subquery))
        )

        # Fetch the page asynchronously
        page_result = await sync_to_async(query.get, thread_sensitive=True)()

        return page_result