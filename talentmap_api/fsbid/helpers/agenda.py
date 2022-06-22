

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

# Need to set up two different conditional classes for different types of legs
class AgendaLeg:
    def __init__(self, **kwargs):
        self.leg_include_indicator = kwargs["legIncludeIndicator"] # ailincind
        self.leg_action_type = kwargs["legActionType"] # aillatcode
        self.person_id = kwargs["personId"] # ailperdetseqnum
        self.tour_of_duty_code = kwargs["tourOfDutyCode"] # ailtodcode
        self.leg_start_date = kwargs["legStartDate"] # ailetadate
        self.leg_end_date = kwargs["legEndDate"] # ailetdtedsepdate
        
class AgendaLegCyclePosition(AgendaLeg):
    def __init__(self, **kwargs):
        super().__init__
        self.travel_function_code = kwargs["travelFunctionCode"] # ailtfcd 
        self.cycle_position_id = kwargs["cyclePositionID"] # ailcpid 
        self.tour_of_duty_months_num = kwargs["tourOfDutyMonthsNum"] # ailtodmonthsnum 
        self.tour_of_duty_other_text = kwargs["tourOfDutyOtherText"] # ailtodothertext 

class AgendaLegAssignment(AgendaLeg):
    def __init__(self, **kwargs):
        super().__init__
        self.leg_assignment_id = kwargs["legAssignmentId"] # ailasgseqnum
        self.leg_assignment_version = kwargs["legAssignmentVersion"] # ailasgdrevisionnum

