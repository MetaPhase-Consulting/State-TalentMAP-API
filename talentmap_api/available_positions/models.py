from django.db import models

from talentmap_api.common.models import StaticRepresentationModel


class AvailablePositionFavorite(StaticRepresentationModel):

    cp_id = models.CharField(max_length=255, null=False)
    user = models.ForeignKey('user_profile.UserProfile', null=False, on_delete=models.DO_NOTHING, help_text="The user to which this favorite belongs")
    archived = models.BooleanField(default=False)

    class Meta:
        managed = True
        ordering = ["cp_id"]
        unique_together = ('cp_id', 'user',)


class AvailablePositionDesignation(models.Model):

    cp_id = models.CharField(max_length=255, null=False, unique=True)

    is_highlighted = models.BooleanField(default=False)
    is_urgent_vacancy = models.BooleanField(default=False)
    is_volunteer = models.BooleanField(default=False)
    is_hard_to_fill = models.BooleanField(default=False)

    class Meta:
        managed = True
        ordering = ["cp_id"]


class AvailablePositionRanking(StaticRepresentationModel):

    cp_id = models.CharField(max_length=255, null=False)
    user = models.ForeignKey('user_profile.UserProfile', null=False, on_delete=models.DO_NOTHING, help_text="The user to which this favorite belongs")
    bidder_perdet = models.CharField(max_length=255, null=False)
    rank = models.IntegerField(default=0, help_text="Numerical ranking of the bidder")
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        ordering = ["cp_id"]
        unique_together = ('cp_id', 'rank', 'bidder_perdet')


class AvailablePositionRankingLock(StaticRepresentationModel):

    cp_id = models.CharField(max_length=255, null=False, unique=True)
    bureau_code = models.CharField(max_length=255, null=False)
    org_code = models.CharField(max_length=255, null=False)

    class Meta:
        managed = True
        ordering = ["cp_id"]
