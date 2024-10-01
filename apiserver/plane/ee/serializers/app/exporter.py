# Module imports
from plane.app.serializers.base import BaseSerializer
from plane.db.models import ExporterHistory


class ExporterHistorySerializer(BaseSerializer):

    class Meta:
        model = ExporterHistory
        fields = [
            "id",
            "created_at",
            "updated_at",
            "project",
            "provider",
            "status",
            "url",
            "initiated_by",
            "token",
            "filters",
            "type",
            "name",
            "created_by",
            "updated_by",
            "workspace",
        ]
        read_only_fields = fields