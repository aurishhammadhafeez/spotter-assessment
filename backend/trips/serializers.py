from rest_framework import serializers


class TripPlanRequestSerializer(serializers.Serializer):
    currentLocation = serializers.CharField(max_length=240, trim_whitespace=True)
    pickupLocation = serializers.CharField(max_length=240, trim_whitespace=True)
    dropoffLocation = serializers.CharField(max_length=240, trim_whitespace=True)
    currentCycleUsedHours = serializers.FloatField(min_value=0, max_value=70)


class ReverseGeocodeRequestSerializer(serializers.Serializer):
    lat = serializers.FloatField(min_value=-90, max_value=90)
    lng = serializers.FloatField(min_value=-180, max_value=180)
