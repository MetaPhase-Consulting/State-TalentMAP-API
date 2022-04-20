

class Agenda:
    def __init__(self, **kwargs):
        self.agenda_include_indicator = kwargs["agendaIncludeIndicator"]
        self.assignment_id = kwargs["assignmentId"]
        self.assignment_version = kwargs["assignmentVersion"]
        self.person_id = kwargs["personId"]
        self.agenda_status_code = kwargs["agendaStatusCode"]


class Panel:
    def __init__(self, **kwargs):
        self.panel_include_indicator = kwargs["panelIncludeIndicator"]
        self.panel_meeting_id = kwargs["panelMeetingId"]
        self.panel_meeting_category = kwargs["panelMeetingCategory"]


class AgendaLeg:
    def __init__(self, **kwargs):
        self.leg_include_indicator = kwargs["legIncludeIndicator"]
        self.leg_action_type = kwargs["legActionType"]
        self.person_id = kwargs["personId"]
        self.tour_of_duty_code = kwargs["tourOfDutyCode"]
        self.leg_assignment_id = kwargs["legAssignmentId"]
        self.leg_assignment_version = kwargs["legAssignmentVersion"]
        self.leg_start_date = kwargs["legStartDate"]
        self.leg_end_date = kwargs["legEndDate"]
        
        
class AgendaLegAssignment(AgendaLeg):
    def __init__(self, **kwargs):
        super().__init__
# 1st Version
    ailincind = serializers.ChoiceField(choices=["A"], default="A")
    aillatcode = serializers.ChoiceField(choices=["S", "E"], default="S")
    ailperdetseqnum = serializers.IntegerField(max_value=None, min_value=None)
    ailtodcode = serializers.ChoiceField(choices=["X"], default="X")
    ailasgseqnum = serializers.IntegerField(max_value=None, min_value=None)
    ailasgdrevisionnum = serializers.IntegerField(max_value=None, min_value=None)
    ailetadate = CharField(max_length=None, min_length=None, allow_blank=False, trim_whitespace=True)
    ailetdtedsepdate = CharField(max_length=None, min_length=None, allow_blank=False, trim_whitespace=True)
    # 2nd Version
    ailtfcd = CharField(max_length=None, min_length=None, allow_blank=False, trim_whitespace=True required=False)
    ailcpid = serializers.IntegerField(max_value=None, min_value=None required=False)
    ailtodcode = serializers.ChoiceField(choices=["J"], default="J" required=False)
    ailtodmonthsnum = serializers.IntegerField(max_value=None, min_value=None required=False)
    ailtodothertext = CharField(max_length=None, min_length=None, allow_blank=False, trim_whitespace=True required=False)
    ailetadate = CharField(max_length=None, min_length=None, allow_blank=False, trim_whitespace=True required=False)
    ailetdtedsepdate = CharField(max_length=None, min_length=None, allow_blank=False, trim_whitespace=True required=False)

