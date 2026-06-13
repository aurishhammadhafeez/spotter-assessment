from rest_framework import serializers


class TripPlanRequestSerializer(serializers.Serializer):
    """Validate the trip-planning payload sent by the React form."""

    currentLocation = serializers.CharField(max_length=240, trim_whitespace=True)
    pickupLocation = serializers.CharField(max_length=240, trim_whitespace=True)
    dropoffLocation = serializers.CharField(max_length=240, trim_whitespace=True)
    currentCycleUsedHours = serializers.FloatField(min_value=0, max_value=70)
    # These fields are optional because the planner can still generate a valid
    # route/log with default demo values, but when provided they are printed on
    # the generated daily log sheet header.
    driverName = serializers.CharField(max_length=80, trim_whitespace=True, required=False, allow_blank=True)
    truckTrailerNumber = serializers.CharField(max_length=120, trim_whitespace=True, required=False, allow_blank=True)
    carrierName = serializers.CharField(max_length=120, trim_whitespace=True, required=False, allow_blank=True)
    mainOfficeAddress = serializers.CharField(max_length=160, trim_whitespace=True, required=False, allow_blank=True)
    homeTerminalAddress = serializers.CharField(max_length=160, trim_whitespace=True, required=False, allow_blank=True)


class ReverseGeocodeRequestSerializer(serializers.Serializer):
    """Validate browser GPS coordinates before calling reverse geocoding."""

    lat = serializers.FloatField(min_value=-90, max_value=90)
    lng = serializers.FloatField(min_value=-180, max_value=180)
