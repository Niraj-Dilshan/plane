# Django imports
from django.db.models import F, Value, Case, When
from django.core.exceptions import ValidationError
from django.db.models import (
    Q,
    CharField,
    Func,
)
from django.db.models.functions import Cast
from django.contrib.postgres.aggregates import ArrayAgg

# Third party imports
from rest_framework import status
from rest_framework.response import Response

# Module imports
from plane.ee.models import (
    IssueProperty,
    DraftIssuePropertyValue,
    PropertyTypeEnum,
)
from plane.db.models import Project, DraftIssue
from plane.ee.views.base import BaseAPIView
from plane.ee.permissions import ProjectEntityPermission
from plane.ee.utils.issue_property_validators import (
    property_validators,
    SAVE_MAPPER,
    VALIDATOR_MAPPER,
)
from plane.ee.utils.draft_issue_property_validators import (
    draft_issue_property_savers,
)
from plane.payment.flags.flag_decorator import check_feature_flag
from plane.payment.flags.flag import FeatureFlag


class DraftIssuePropertyValueEndpoint(BaseAPIView):
    permission_classes = [
        ProjectEntityPermission,
    ]

    def query_annotator(self, query):
        return query.values("property_id").annotate(
            values=ArrayAgg(
                Case(
                    When(
                        property__property_type__in=[
                            PropertyTypeEnum.TEXT,
                            PropertyTypeEnum.URL,
                            PropertyTypeEnum.EMAIL,
                            PropertyTypeEnum.FILE,
                        ],
                        then=F("value_text"),
                    ),
                    When(
                        property__property_type=PropertyTypeEnum.DATETIME,
                        then=Func(
                            F("value_datetime"),
                            function="TO_CHAR",
                            template="%(function)s(%(expressions)s, 'YYYY-MM-DD')",
                            output_field=CharField(),
                        ),
                    ),
                    When(
                        property__property_type=PropertyTypeEnum.DECIMAL,
                        then=Cast(
                            F("value_decimal"), output_field=CharField()
                        ),
                    ),
                    When(
                        property__property_type=PropertyTypeEnum.BOOLEAN,
                        then=Cast(
                            F("value_boolean"), output_field=CharField()
                        ),
                    ),
                    When(
                        property__property_type=PropertyTypeEnum.RELATION,
                        then=Cast(F("value_uuid"), output_field=CharField()),
                    ),
                    When(
                        property__property_type=PropertyTypeEnum.OPTION,
                        then=Cast(F("value_option"), output_field=CharField()),
                    ),
                    default=Value(
                        ""
                    ),  # Default value if none of the conditions match
                    output_field=CharField(),
                ),
                filter=Q(property_id=F("property_id")),
                distinct=True,
            ),
        )

    @check_feature_flag(FeatureFlag.ISSUE_TYPE_DISPLAY)
    def get(
        self, request, slug, project_id, draft_issue_id, issue_property_id=None
    ):
        # Get a single issue property value
        if issue_property_id:
            issue_property_value = DraftIssuePropertyValue.objects.filter(
                workspace__slug=slug,
                project_id=project_id,
                draft_issue_id=draft_issue_id,
                property_id=issue_property_id,
            )

            issue_property_value = self.query_annotator(
                issue_property_value
            ).values("property_id", "value")

            return Response(issue_property_value, status=status.HTTP_200_OK)

        # Get all issue property values
        issue_property_values = DraftIssuePropertyValue.objects.filter(
            workspace__slug=slug,
            project_id=project_id,
            draft_issue_id=draft_issue_id,
            property__is_active=True,
        )

        # Annotate the query
        issue_property_values = self.query_annotator(
            issue_property_values
        ).values("property_id", "values")

        # Create dictionary of property_id and values
        response = {
            str(issue_property_value["property_id"]): issue_property_value[
                "values"
            ]
            for issue_property_value in issue_property_values
        }

        return Response(response, status=status.HTTP_200_OK)

    @check_feature_flag(FeatureFlag.ISSUE_TYPE_DISPLAY)
    def post(self, request, slug, project_id, draft_issue_id):
        try:
            # Create a new issue property value
            issue_property_values = request.data.get("property_values", {})

            # Get all the issue property ids
            issue_property_ids = list(issue_property_values.keys())

            # existing values
            existing_prop_queryset = DraftIssuePropertyValue.objects.filter(
                workspace__slug=slug,
                project_id=project_id,
                draft_issue_id=draft_issue_id,
            )

            # Get all issue property values
            existing_prop_values = self.query_annotator(
                existing_prop_queryset
            ).values("property_id", "values")

            # Get issue
            issue = DraftIssue.objects.get(pk=draft_issue_id)

            # Get Issue Type
            issue_type_id = issue.type_id

            # Get Project
            project = Project.objects.get(pk=project_id)
            workspace_id = project.workspace_id

            # Get all issue properties
            issue_properties = IssueProperty.objects.filter(
                workspace__slug=slug,
                project_id=project_id,
                issue_type_id=issue_type_id,
            )

            # Validate the data
            property_validators(
                properties=issue_properties,
                property_values=issue_property_values,
                existing_prop_values=existing_prop_values,
            )

            # Save the data
            bulk_issue_property_values = draft_issue_property_savers(
                properties=issue_properties,
                property_values=issue_property_values,
                draft_issue_id=draft_issue_id,
                workspace_id=workspace_id,
                project_id=project_id,
                existing_prop_values=existing_prop_values,
            )

            # Delete the old values
            existing_prop_queryset.filter(
                property_id__in=issue_property_ids,
                draft_issue__type_id=issue_type_id,
            ).delete()
            # Bulk create the issue property values
            DraftIssuePropertyValue.objects.bulk_create(
                bulk_issue_property_values, batch_size=10
            )

            return Response(status=status.HTTP_201_CREATED)
        except (ValidationError, ValueError) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @check_feature_flag(FeatureFlag.ISSUE_TYPE_DISPLAY)
    def patch(self, request, slug, project_id, draft_issue_id, property_id):
        try:
            # Get the issue property
            issue_property = IssueProperty.objects.get(
                workspace__slug=slug,
                project_id=project_id,
                pk=property_id,
            )

            existing_prop_queryset = DraftIssuePropertyValue.objects.filter(
                workspace__slug=slug,
                project_id=project_id,
                draft_issue_id=draft_issue_id,
                property_id=property_id,
            )

            # Get the value
            values = request.data.get("values", [])

            # Check if the property is required
            if issue_property.is_required and (
                not values or not [v for v in values if v]
            ):
                return Response(
                    {
                        "error": issue_property.display_name
                        + " is a required property"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate the values
            validator = VALIDATOR_MAPPER.get(issue_property.property_type)

            if validator:
                for value in values:
                    validator(issue_property=issue_property, value=value)
            else:
                raise ValidationError("Invalid property type")

            # Save the values
            saver = SAVE_MAPPER.get(issue_property.property_type)
            if saver:
                # Save the data
                property_values = saver(
                    values=values,
                    issue_property=issue_property,
                    draft_issue_id=draft_issue_id,
                    existing_values=[],
                    workspace_id=issue_property.workspace_id,
                    project_id=issue_property.project_id,
                )
                # Delete the old values
                existing_prop_queryset.filter(property_id=property_id).delete()
                # Bulk create the issue property values
                DraftIssuePropertyValue.objects.bulk_create(
                    property_values, batch_size=10
                )

            else:
                raise ValidationError("Invalid property type")

            return Response(status=status.HTTP_204_NO_CONTENT)
        except (ValidationError, ValueError) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )