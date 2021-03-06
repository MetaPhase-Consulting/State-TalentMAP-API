from talentmap_api.common.serializers import PrefetchedSerializer

from talentmap_api.stats.models import LoginInstance, ViewPositionInstance


class LoginInstanceSerializer(PrefetchedSerializer):

    class Meta:
        model = LoginInstance
        fields = ["id", "date_of_login", "details"]
        writable_fields = ("details")

class LoginInstanceListSerializer(PrefetchedSerializer):

    class Meta:
        model = LoginInstance
        fields = ["id", "date_of_login"]

class ViewPositionInstanceSerializer(PrefetchedSerializer):

    class Meta:
        model = ViewPositionInstance
        fields = []
        writable_fields = ("position_id", "position_type")
