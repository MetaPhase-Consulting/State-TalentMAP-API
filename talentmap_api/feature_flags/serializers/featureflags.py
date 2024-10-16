from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.feature_flags.models import FeatureFlags


class FeatureFlagsSerializer(PrefetchedSerializer):

    class Meta:
        model = FeatureFlags
        fields = ["feature_flags", "date_updated"]
        writable_fields = ("feature_flags")
