from django.db import models

from talentmap_api.common.models import StaticRepresentationModel

class BureauExemptionList(StaticRepresentationModel):

    id = models.IntegerField(primary_key=True, null=False)
    user = models.ForeignKey('user_profile.UserProfile', null=False, on_delete=models.DO_NOTHING, help_text="The user to which this tandem favorite belongs")

    class Meta:
        managed = True
        ordering = ["id"]
        unique_together = ('id', 'user')