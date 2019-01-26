from django.core.management.base import BaseCommand
from django.core.management import call_command

import logging
import re

from talentmap_api.common.xml_helpers import XMLloader, strip_extra_spaces, parse_boolean, parse_date, get_nested_tag, set_foreign_key_by_filters
from talentmap_api.position.models import Position
from talentmap_api.user_profile.models import SavedSearch

class Command(BaseCommand):
    help = 'Loads an XML into a supported file'
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.modes = {
            'positions': mode_positions,
        }

    def add_arguments(self, parser):
        parser.add_argument('file', nargs=1, type=str, help="The XML file to load")
        parser.add_argument('type', nargs=1, type=str, choices=self.modes.keys(), help="The type of data in the XML")
        parser.add_argument('--delete', dest='delete', action='store_true', help='Delete collisions')
        parser.add_argument('--update', dest='update', action='store_true', help='Update collisions')
        parser.add_argument('--skippost', dest='skip_post', action='store_true', help='Skip post load functions')

    def handle(self, *args, **options):
        model, instance_tag, tag_map, collision_field, post_load_function = self.modes[options['type'][0]]()

        # Set / update the collision behavior
        collision_behavior = None
        if options['delete']:
            collision_behavior = "delete"
        elif options['update']:
            collision_behavior = "update"
        else:
            collision_behavior = "skip"

        self.logger.info(instance_tag)
        loader = XMLloader(model, instance_tag, tag_map, collision_behavior, collision_field)
        new_ids, updated_ids = loader.create_models_from_xml(options['file'][0])

        # Run the post load function, if it exists
        if callable(post_load_function) and not options['skip_post']:
            post_load_function(new_ids, updated_ids)

        self.logger.info(f"XML Load Report\n\tNew: {len(new_ids)}\n\tUpdated: {len(updated_ids)}\t\t")

        if len(new_ids) + len(updated_ids) > 0:
            self.logger.info("Now updating relationships...")
            call_command('update_relationships')
            self.logger.info("Updating string representations...")
            call_command("update_string_representations")
            self.logger.info("Clearing cache...")
            call_command('clear_cache')


def mode_positions():
    model = Position
    # Response parsing data
    instance_tag = "positions"
    collision_field = "_seq_num"
    tag_map = {
        "pos_id": "_seq_num",
        "position_number": "position_number",
        "title": "title",
        "org_code": "_org_code",
        "bureau_code": "_bureau_code",
        "skill_code": "_skill_code",
        "is_overseas": parse_boolean("is_overseas"),
        "grade": "_grade_code",
        "tod_code": set_foreign_key_by_filters("tour_of_duty", "code", "__icontains"),
        "language_code_1": "_language_1_code",
        "language_code_2": "_language_2_code",
        "location_code": "_location_code",
        "spoken_proficiency_1": "_language_1_spoken_proficiency_code",
        "reading_proficiency_1": "_language_1_reading_proficiency_code",
        "spoken_proficiency_2": "_language_2_spoken_proficiency_code",
        "reading_proficiency_2": "_language_2_reading_proficiency_code",
        "create_date": parse_date("create_date"),
        "update_date": parse_date("update_date"),
        "effective_date": parse_date("effective_date"),
    }

    def post_load_function(new_ids, updated_ids):
        # If we have any new or updated positions, update saved search counts
        if len(new_ids) + len(updated_ids) > 0:
            SavedSearch.update_counts_for_endpoint(endpoint='position', contains=True)

    return (model, instance_tag, tag_map, collision_field, post_load_function)