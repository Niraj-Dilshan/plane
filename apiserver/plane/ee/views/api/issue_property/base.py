# Third party imports
from rest_framework import status
from rest_framework.response import Response

# Module imports
from plane.app.permissions import ProjectEntityPermission
from plane.db.models import Workspace, Project, IssueType
from plane.ee.models import IssueProperty
from plane.ee.serializers.api import IssuePropertyAPISerializer
from plane.api.views.base import BaseAPIView
from plane.payment.flags.flag_decorator import check_feature_flag
from plane.payment.flags.flag import FeatureFlag


class IssuePropertyAPIEndpoint(BaseAPIView):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions related to issue type properties.

    """

    model = IssueProperty
    serializer_class = IssuePropertyAPISerializer
    permission_classes = [ProjectEntityPermission]
    webhook_event = "issue_property"

    @property
    def workspace_slug(self):
        return self.kwargs.get("slug", None)

    @property
    def project_id(self):
        return self.kwargs.get("project_id", None)

    @property
    def type_id(self):
        return self.kwargs.get("type_id", None)

    @property
    def property_id(self):
        return self.kwargs.get("property_id", None)

    # list issue properties and get issue property by id
    @check_feature_flag(FeatureFlag.ISSUE_TYPE_SETTINGS)
    def get(self, request, slug, project_id, type_id, property_id=None):
        if self.workspace_slug and self.project_id and self.type_id:
            # list of issue properties
            if self.property_id is None:
                issue_properties = self.model.objects.filter(
                    workspace__slug=self.workspace_slug,
                    project_id=self.project_id,
                    issue_type_id=self.type_id,
                )
                serializer = self.serializer_class(issue_properties, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            # getting issue property by id
            issue_property = self.model.objects.get(
                workspace__slug=self.workspace_slug,
                project_id=self.project_id,
                issue_type_id=self.type_id,
                pk=self.property_id,
            )
            serializer = self.serializer_class(issue_property)
            return Response(serializer.data, status=status.HTTP_200_OK)

    # create issue property
    @check_feature_flag(FeatureFlag.ISSUE_TYPE_SETTINGS)
    def post(self, request, slug, project_id, type_id):
        if self.workspace_slug and self.project_id and self.type_id:
            workspace = Workspace.objects.get(slug=self.workspace_slug)
            project = Project.objects.get(pk=self.project_id)
            issue_type = IssueType.objects.get(pk=self.type_id)

            # check if issue property with the same external id and external source already exists
            external_id = request.data.get("external_id")
            external_existing_issue_property = self.model.objects.filter(
                workspace__slug=self.workspace_slug,
                project_id=self.project_id,
                issue_type_id=self.type_id,
                external_source=request.data.get("external_source"),
                external_id=request.data.get("external_id"),
            )
            if (
                external_id
                and request.data.get("external_source")
                and external_existing_issue_property.exists()
            ):
                issue_property = self.model.objects.filter(
                    workspace__slug=self.workspace_slug,
                    project_id=self.project_id,
                    issue_type_id=self.type_id,
                    external_source=request.data.get("external_source"),
                    external_id=external_id,
                ).first()
                return Response(
                    {
                        "error": "Issue Property with the same external id and external source already exists",
                        "id": str(issue_property.id),
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            data = request.data
            issue_property_serializer = self.serializer_class(data=data)
            issue_property_serializer.is_valid(raise_exception=True)
            issue_property_serializer.save(
                workspace=workspace, project=project, issue_type=issue_type
            )

            # getting the issue property
            issue_property = self.model.objects.get(
                workspace__slug=self.workspace_slug,
                project_id=self.project_id,
                issue_type_id=self.type_id,
                pk=issue_property_serializer.data["id"],
            )
            serializer = self.serializer_class(issue_property)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    # update issue property by id
    @check_feature_flag(FeatureFlag.ISSUE_TYPE_SETTINGS)
    def patch(self, request, slug, project_id, type_id, property_id):
        if (
            self.workspace_slug
            and self.project_id
            and self.type_id
            and self.property_id
        ):
            issue_property = self.model.objects.get(
                workspace__slug=self.workspace_slug,
                project_id=self.project_id,
                issue_type_id=self.type_id,
                pk=self.property_id,
            )

            data = request.data
            issue_property_serializer = self.serializer_class(
                issue_property, data=data, partial=True
            )
            issue_property_serializer.is_valid(raise_exception=True)

            # check if issue type with the same external id and external source already exists
            external_id = request.data.get("external_id")
            external_existing_issue_property = self.model.objects.filter(
                workspace__slug=self.workspace_slug,
                project_id=self.project_id,
                issue_type_id=self.type_id,
                external_source=request.data.get(
                    "external_source", issue_property.external_source
                ),
                external_id=external_id,
            )
            if (
                external_id
                and (issue_property.external_id != external_id)
                and external_existing_issue_property.exists()
            ):
                return Response(
                    {
                        "error": "Issue property with the same external id and external source already exists",
                        "id": str(issue_property.id),
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            issue_property_serializer.save()

            return Response(
                issue_property_serializer.data, status=status.HTTP_200_OK
            )

    # delete issue property by id
    @check_feature_flag(FeatureFlag.ISSUE_TYPE_SETTINGS)
    def delete(self, request, slug, project_id, type_id, property_id):
        if (
            self.workspace_slug
            and self.project_id
            and self.type_id
            and self.property_id
        ):
            issue_property = self.model.objects.get(
                workspace__slug=self.workspace_slug,
                project_id=self.project_id,
                issue_type_id=self.type_id,
                pk=self.property_id,
            )
            issue_property.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)