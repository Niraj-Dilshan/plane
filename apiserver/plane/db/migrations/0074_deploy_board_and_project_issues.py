# Generated by Django 4.2.11 on 2024-08-13 16:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0073_alter_commentreaction_unique_together_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="deployboard",
            name="is_activity_enabled",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="fileasset",
            name="is_archived",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="userfavorite",
            name="sequence",
            field=models.FloatField(default=65535),
        ),
        migrations.CreateModel(
            name="ProjectIssueType",
            fields=[
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Created At"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Last Modified At"
                    ),
                ),
                (
                    "deleted_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Deleted At"
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("level", models.PositiveIntegerField(default=0)),
                ("is_default", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "Project Issue Type",
                "verbose_name_plural": "Project Issue Types",
                "db_table": "project_issue_types",
                "ordering": ("project", "issue_type"),
            },
        ),
        migrations.AlterModelOptions(
            name="issuetype",
            options={
                "verbose_name": "Issue Type",
                "verbose_name_plural": "Issue Types",
            },
        ),
        migrations.RemoveConstraint(
            model_name="issuetype",
            name="issue_type_unique_name_project_when_deleted_at_null",
        ),
        migrations.AlterUniqueTogether(
            name="issuetype",
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name="issuetype",
            name="workspace",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="issue_types",
                to="db.workspace",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="issuetype",
            unique_together={("workspace", "name", "deleted_at")},
        ),
        migrations.AddConstraint(
            model_name="issuetype",
            constraint=models.UniqueConstraint(
                condition=models.Q(("deleted_at__isnull", True)),
                fields=("name", "workspace"),
                name="issue_type_unique_name_workspace_when_deleted_at_null",
            ),
        ),
        migrations.AddField(
            model_name="projectissuetype",
            name="created_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(class)s_created_by",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Created By",
            ),
        ),
        migrations.AddField(
            model_name="projectissuetype",
            name="issue_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="project_issue_types",
                to="db.issuetype",
            ),
        ),
        migrations.AddField(
            model_name="projectissuetype",
            name="project",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="project_%(class)s",
                to="db.project",
            ),
        ),
        migrations.AddField(
            model_name="projectissuetype",
            name="updated_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="%(class)s_updated_by",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Last Modified By",
            ),
        ),
        migrations.AddField(
            model_name="projectissuetype",
            name="workspace",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="workspace_%(class)s",
                to="db.workspace",
            ),
        ),
        migrations.RemoveField(
            model_name="issuetype",
            name="is_default",
        ),
        migrations.RemoveField(
            model_name="issuetype",
            name="project",
        ),
        migrations.RemoveField(
            model_name="issuetype",
            name="sort_order",
        ),
        migrations.RemoveField(
            model_name="issuetype",
            name="weight",
        ),
        migrations.AddConstraint(
            model_name="projectissuetype",
            constraint=models.UniqueConstraint(
                condition=models.Q(("deleted_at__isnull", True)),
                fields=("project", "issue_type"),
                name="project_issue_type_unique_project_issue_type_when_deleted_at_null",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="projectissuetype",
            unique_together={("project", "issue_type", "deleted_at")},
        ),
        migrations.AddField(
            model_name="issuetype",
            name="is_default",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="issuetype",
            name="level",
            field=models.PositiveIntegerField(default=0),
        ),
    ]