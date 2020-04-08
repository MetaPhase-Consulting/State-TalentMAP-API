from __future__ import absolute_import, unicode_literals

from celery import shared_task

from talentmap_api.available_positions.models import AvailablePositionFavorite
from talentmap_api.projected_vacancies.models import ProjectedVacancyFavorite

import logging
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def archive_favorites(self, user_favorites, returned_favorites, isAP):
    try:
        outdated_ids = []
        for fav_id in user_favorites:
            if fav_id not in returned_favorites:
                outdated_ids.append(fav_id)
        if len(outdated_ids) > 0 and isAP is True:
            AvailablePositionFavorite.objects.filter(cp_id__in=outdated_ids).update(archived=True)
            print("Available Position favorites archived")
        elif len(outdated_ids) > 0 and isAP is False:
            ProjectedVacancyFavorite.objects.filter(fv_seq_num__in=outdated_ids).update(archived=True)
            print("Projected Vacancy favorites archived")
        else: 
            print("No favorites were archived")
    except Exception as ex:
        logger.exception(ex)
        self.retry(countdown=3**self.request.retries)