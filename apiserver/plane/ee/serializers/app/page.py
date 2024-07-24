# Third party imports
from rest_framework import serializers

# Module imports
from plane.app.serializers.base import BaseSerializer
from plane.db.models import Project, Page, Label, ProjectPage, PageLabel


class WorkspacePageSerializer(BaseSerializer):
    is_favorite = serializers.BooleanField(read_only=True)
    labels = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Label.objects.all()),
        write_only=True,
        required=False,
    )
    projects = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=Project.objects.all()
        ),
        write_only=True,
        required=False,
    )
    anchor = serializers.CharField(read_only=True)

    class Meta:
        model = Page
        fields = [
            "id",
            "name",
            "owned_by",
            "access",
            "color",
            "labels",
            "parent",
            "is_favorite",
            "is_locked",
            "archived_at",
            "workspace",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "view_props",
            "logo_props",
            "projects",
            "anchor",
        ]
        read_only_fields = [
            "workspace",
            "owned_by",
            "anchor",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["labels"] = [str(label.id) for label in instance.labels.all()]
        data["projects"] = [
            str(project.id) for project in instance.projects.all()
        ]
        return data

    def create(self, validated_data):
        labels = validated_data.pop("labels", None)
        projects = validated_data.pop("projects", None)
        owned_by_id = self.context["owned_by_id"]
        description_html = self.context["description_html"]
        workspace_id = self.context["workspace_id"]

        # Get the workspace id from the project
        page = Page.objects.create(
            **validated_data,
            description_html=description_html,
            owned_by_id=owned_by_id,
            workspace_id=workspace_id,
        )

        # Create the page labels
        if labels is not None:
            PageLabel.objects.bulk_create(
                [
                    PageLabel(
                        label=label,
                        page=page,
                        workspace_id=workspace_id,
                        created_by_id=page.created_by_id,
                        updated_by_id=page.updated_by_id,
                    )
                    for label in labels
                ],
                batch_size=10,
            )

        #
        if projects is not None:
            ProjectPage.objects.bulk_create(
                [
                    ProjectPage(
                        workspace_id=page.workspace_id,
                        project_id=project,
                        page_id=page.id,
                        created_by_id=page.created_by_id,
                        updated_by_id=page.updated_by_id,
                    )
                    for project in projects
                ],
                batch_size=10,
            )

        return page

    def update(self, instance, validated_data):
        labels = validated_data.pop("labels", None)
        projects = validated_data.pop("projects", None)

        if projects is not None:
            ProjectPage.objects.filter(page=instance).delete()
            ProjectPage.objects.bulk_create(
                [
                    ProjectPage(
                        workspace_id=instance.workspace_id,
                        project_id=project,
                        page_id=instance.id,
                        created_by_id=instance.created_by_id,
                        updated_by_id=instance.updated_by_id,
                    )
                    for project in projects
                ],
                batch_size=10,
            )

        if labels is not None:
            PageLabel.objects.filter(page=instance).delete()
            PageLabel.objects.bulk_create(
                [
                    PageLabel(
                        label=label,
                        page=instance,
                        workspace_id=instance.workspace_id,
                        created_by_id=instance.created_by_id,
                        updated_by_id=instance.updated_by_id,
                    )
                    for label in labels
                ],
                batch_size=10,
            )

        return super().update(instance, validated_data)


class WorkspacePageDetailSerializer(BaseSerializer):
    description_html = serializers.CharField()
    is_favorite = serializers.BooleanField(read_only=True)
    anchor = serializers.CharField(read_only=True)

    class Meta(WorkspacePageSerializer.Meta):
        fields = WorkspacePageSerializer.Meta.fields + [
            "description_html",
            "anchor",
        ]