import logging

from django.conf import settings


API_ROOT = settings.WS_ROOT_API_URL

logger = logging.getLogger(__name__)


def validate_agenda_item(query):
    # when adding more validation checks,
    # remember to make sure the allValid check is still properly tracking all valid states
    validation_status = {
        'status': validate_status(query['agendaStatusCode']),
        'reportCategory': validate_report_category(query['panelMeetingCategory']),
        'panelDate': validate_panel_date(query['panelMeetingId']),
        'legs': validate_legs(query['agendaLegs']),
    }

    all_valid = True
    for k in validation_status.keys():
        if k == 'legs':
            all_valid = all_valid and validation_status[k]['allLegs']['valid']
        else:
            all_valid = all_valid and validation_status[k]['valid']
    validation_status['allValid'] = all_valid

    return validation_status


def validate_status(status):
    status_validation = {
        'valid': True,
        'errorMessage': ''
    }

    # AI Status - must make selection
    if not status:
        status_validation['valid'] = False
        status_validation['errorMessage'] = 'No Status Selected'

    return status_validation

def validate_report_category(category):
    category_validation = {
        'valid': True,
        'errorMessage': ''
    }

    # AI Category - must make selection
    if not category:
        category_validation['valid'] = False
        category_validation['errorMessage'] = 'No Category Selected'

    return category_validation

def validate_panel_date(date):
    date_validation = {
        'valid': True,
        'errorMessage': ''
    }

    # AI Date - must make selection
    if not date:
        date_validation['valid'] = False
        date_validation['errorMessage'] = 'No Panel Date Selected'

    return date_validation

def validate_legs(legs):
    legs_validation = {
        'allLegs': {
            'valid': True,
            'errorMessage': ''
        },
        'individualLegs': {}
    }

    # AI Legs - must not be empty
    if not legs:
        legs_validation['allLegs']['valid'] = False
        legs_validation['allLegs']['errorMessage'] = 'Agenda Items must have at least one leg.'
        return legs_validation

    for leg in legs:
        valid_leg_check = validate_individual_leg(leg)
        legs_validation['individualLegs'][leg['ail_seq_num']] = valid_leg_check[0]
        if not valid_leg_check[1]:
            legs_validation['allLegs']['valid'] = False
            legs_validation['allLegs']['errorMessage'] = 'One of the Agenda Item\'s legs failed validation.'

    return legs_validation

def validate_individual_leg(leg):
    whole_leg_valid = True
    individual_leg_validation = {
        'ted': {
            'valid': True,
            'errorMessage': ''
        },
        'eta': {
            'valid': True,
            'errorMessage': ''
        },
        'tod': validate_tod(leg['tod'], leg['tod_months'], leg['tod_long_desc']),
        'action_code': {
            'valid': True,
            'errorMessage': ''
        },
        'travel_code': {
            'valid': True,
            'errorMessage': ''
        },
        'separation_location': {
            'valid': True,
            'errorMessage': ''
        }
    }

    # Leg - must have ETA
    if not leg['eta']:
        individual_leg_validation['eta']['valid'] = False
        individual_leg_validation['eta']['errorMessage'] = 'Missing ETA'
        whole_leg_valid = False

    # Leg - must have TED
    if not leg['ted']:
        individual_leg_validation['ted']['valid'] = False
        individual_leg_validation['ted']['errorMessage'] = 'Missing TED'
        whole_leg_valid = False

    # Leg - must have Action
    if not leg.get('action_code'):
        individual_leg_validation['action_code']['valid'] = False
        individual_leg_validation['action_code']['errorMessage'] = 'Missing Action'
        whole_leg_valid = False

    # Leg - must have Travel - NEED TO CONFIRM THIS
    if not leg.get('travel_code'):
        individual_leg_validation['travel_code']['valid'] = True
        individual_leg_validation['travel_code']['errorMessage'] = 'Missing Travel'
        # Can be nullable according to DB - need to follow up in FSBID
        whole_leg_valid = True

    # Leg - must have duty station for separation
    if leg.get('is_separation', False) and not leg.get('separation_location', False):
        individual_leg_validation['separation_location']['valid'] = False
        individual_leg_validation['separation_location']['errorMessage'] = 'Missing Location'
        whole_leg_valid = False

    return (individual_leg_validation, whole_leg_valid)

def validate_tod(tod, tod_months, tod_long_desc):
    tod_validation = {
        'valid': True,
        'errorMessage': ''
    }

    # Leg - must have TOD
    if not tod:
        tod_validation['valid'] = False
        tod_validation['errorMessage'] = 'Missing TOD'
        return tod_validation

    # if TOD code X(other) - must have months and long text
    if tod == 'X':
        if (not tod_months) or (not tod_long_desc):
            tod_validation['valid'] = False
            tod_validation['errorMessage'] = 'Other TOD must have Tour length'

    return tod_validation
