from typing import Optional

# Strawberry imports
import strawberry
from strawberry.types import Info
from strawberry.permission import PermissionExtension

# Third-party imports
from asgiref.sync import sync_to_async

# Module imports
from plane.graphql.permissions.project import ProjectMemberPermission
from plane.db.models import Issue
from plane.graphql.types.issue import IssuesType


# create methods
@sync_to_async
def get_sub_issues(sub_issue_ids):
    return list(Issue.issue_objects.filter(id__in=sub_issue_ids))


@sync_to_async
def bulk_update_issues(issues, fields):
    Issue.objects.bulk_update(issues, fields, batch_size=10)


# remove methods
@sync_to_async
def get_sub_issue_details(
    issueId: strawberry.ID, parentIssueId: strawberry.ID
):
    return Issue.issue_objects.get(id=issueId, parent=parentIssueId)


@sync_to_async
def update_issue_parent(
    issue: IssuesType, parentIssueId: Optional[strawberry.ID] = None
):
    issue.parent = parentIssueId
    issue.save()
    return True


@strawberry.type
class SubIssueMutation:
    # adding issue relation
    @strawberry.mutation(
        extensions=[
            PermissionExtension(permissions=[ProjectMemberPermission()])
        ]
    )
    async def createSubIssue(
        self,
        info: Info,
        slug: str,
        project: strawberry.ID,
        parentIssueId: strawberry.ID,
        subIssueIds: list[strawberry.ID],
    ) -> bool:
        try:
            sub_issues = await get_sub_issues(subIssueIds)

            for sub_issue in sub_issues:
                sub_issue.parent_id = parentIssueId

            await bulk_update_issues(sub_issues, ["parent"])
            return True
        except Exception:
            return False

    # removing issue relation
    @strawberry.mutation(
        extensions=[
            PermissionExtension(permissions=[ProjectMemberPermission()])
        ]
    )
    async def removeSubIssue(
        self,
        info: Info,
        slug: str,
        project: strawberry.ID,
        parentIssueId: strawberry.ID,
        subIssueId: strawberry.ID,
    ) -> bool:
        try:
            sub_issue = await get_sub_issue_details(subIssueId, parentIssueId)
            if not sub_issue:
                return False

            await update_issue_parent(sub_issue, None)
            return True
        except Exception:
            return False