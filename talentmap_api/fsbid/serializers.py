from rest_framework import serializers

class AgendaSerializer(serializers.Serializer):
    aiincind = serializers.ChoiceField(choices=["A"], default="A")
    aiasgseqnum = serializers.IntegerField(max_value=None, min_value=None) 
    aiasgdrevisionnum = serializers.IntegerField(max_value=None, min_value=None)
    aiperdetseqnum = serializers.IntegerField(max_value=None, min_value=None)
    aiaiscode = serializers.ChoiceField(choices=["N"], default="N")

class PanelSerializer(serializers.Serializer):
    pmiincind = serializers.ChoiceField(choices=["A"], default="A")
    pmipmseqnum = serializers.IntegerField(max_value=None, min_value=None)
    pmimiccode = serializers.ChoiceField(choices=["D"], default="D")

class AgendaLegSerializer(serializers.Serializer):
    # 1st Version
    ailincind = serializers.ChoiceField(choices=["A"], default="A")
    aillatcode = serializers.ChoiceField(choices=["S", "E"], default="S")
    ailperdetseqnum = serializers.IntegerField(max_value=None, min_value=None)
    ailtodcode = serializers.ChoiceField(choices=["X"], default="X")
    ailasgseqnum = serializers.IntegerField(max_value=None, min_value=None)
    ailasgdrevisionnum = serializers.IntegerField(max_value=None, min_value=None)
    ailetadate = serializers.CharField(max_length=None, min_length=None, allow_blank=False, trim_whitespace=True)
    ailetdtedsepdate = serializers.CharField(max_length=None, min_length=None, allow_blank=False, trim_whitespace=True)
    # 2nd Version
    ailtfcd = serializers.CharField(max_length=None, min_length=None, allow_blank=False, trim_whitespace=True, required=False)
    ailcpid = serializers.IntegerField(max_value=None, min_value=None, required=False)
    ailtodcode = serializers.ChoiceField(choices=["J"], default="J", required=False)
    ailtodmonthsnum = serializers.IntegerField(max_value=None, min_value=None, required=False)
    ailtodothertext = serializers.CharField(max_length=None, min_length=None, allow_blank=False, trim_whitespace=True, required=False)
    ailetadate = serializers.CharField(max_length=None, min_length=None, allow_blank=False, trim_whitespace=True, required=False)
    ailetdtedsepdate = serializers.CharField(max_length=None, min_length=None, allow_blank=False, trim_whitespace=True, required=False)

