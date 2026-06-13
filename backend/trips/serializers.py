from rest_framework import serializers


class TripPlanRequestSerializer(serializers.Serializer):
    currentLocation = serializers.CharField(max_length=240, trim_whitespace=True)
    pickupLocation = serializers.CharField(max_length=240, trim_whitespace=True)
    dropoffLocation = serializers.CharField(max_length=240, trim_whitespace=True)
    currentCycleUsedHours = serializers.FloatField(min_value=0, max_value=70)
    driverName = serializers.CharField(max_length=80, trim_whitespace=True, required=False, allow_blank=True)
    truckTrailerNumber = serializers.CharField(max_length=120, trim_whitespace=True, required=False, allow_blank=True)
    carrierName = serializers.CharField(max_length=120, trim_whitespace=True, required=False, allow_blank=True)
    mainOfficeAddress = serializers.CharField(max_length=160, trim_whitespace=True, required=False, allow_blank=True)
    homeTerminalAddress = serializers.CharField(max_length=160, trim_whitespace=True, required=False, allow_blank=True)


class ReverseGeocodeRequestSerializer(serializers.Serializer):
    lat = serializers.FloatField(min_value=-90, max_value=90)
    lng = serializers.FloatField(min_value=-180, max_value=180)
