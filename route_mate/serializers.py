import re
from rest_framework import serializers
from .models import Route, RouteJoinRequest

PHONE_REGEX = r'^(?:\+8801|01)[3-9]\d{8}$'

def normalize_and_validate_bd_phone(value):
    if not value:
        return value
    normalized = re.sub(r'[\s-]', '', value)
    if not re.match(PHONE_REGEX, normalized):
        raise serializers.ValidationError("Enter a valid phone number (11 digits starting with 01, or +880 followed by 10 digits).")
    return normalized


class RouteJoinRequestSerializer(serializers.ModelSerializer):
    requester_username = serializers.CharField(source='requester.username', read_only=True)
    requester_full_name = serializers.CharField(source='requester.full_name', read_only=True)
    route_home_area = serializers.CharField(source='route.home_area', read_only=True)
    route_destination = serializers.CharField(source='route.destination', read_only=True)
    route_owner_username = serializers.CharField(source='route.owner.username', read_only=True)

    class Meta:
        model = RouteJoinRequest
        fields = (
            'id',
            'route',
            'route_home_area',
            'route_destination',
            'route_owner_username',
            'requester',
            'requester_username',
            'requester_full_name',
            'status',
            'note',
            'requester_contact_info',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'route',
            'requester',
            'requester_username',
            'requester_full_name',
            'route_home_area',
            'route_destination',
            'route_owner_username',
            'created_at',
            'updated_at',
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')
        
        # Mask requester_contact_info unless the user is the route owner or the requester AND status is ACCEPTED
        if request and request.user.is_authenticated:
            is_owner = (instance.route.owner == request.user)
            is_requester = (instance.requester == request.user)
            if (is_owner or is_requester) and instance.status == 'ACCEPTED':
                return ret
        
        # Otherwise mask contact info
        ret['requester_contact_info'] = "[Unlocked upon acceptance]"
        return ret


class RouteSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    owner_full_name = serializers.CharField(source='owner.full_name', read_only=True)
    user_request_status = serializers.SerializerMethodField()
    accepted_members_count = serializers.SerializerMethodField()

    class Meta:
        model = Route
        fields = (
            'id',
            'owner',
            'owner_username',
            'owner_full_name',
            'home_area',
            'destination',
            'departure_time_start',
            'departure_time_end',
            'days_active',
            'transport_mode',
            'note',
            'gender_preference',
            'status',
            'contact_info',
            'user_request_status',
            'accepted_members_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'owner',
            'owner_username',
            'owner_full_name',
            'user_request_status',
            'accepted_members_count',
            'created_at',
            'updated_at',
        )

    def get_user_request_status(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        join_req = RouteJoinRequest.objects.filter(route=obj, requester=request.user).first()
        return join_req.status if join_req else None

    def get_accepted_members_count(self, obj):
        return obj.join_requests.filter(status='ACCEPTED').count()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')

        # Contact info unlocking logic
        unlocked = False
        if request and request.user.is_authenticated:
            if instance.owner == request.user:
                unlocked = True
            else:
                has_accepted = instance.join_requests.filter(
                    requester=request.user,
                    status='ACCEPTED'
                ).exists()
                if has_accepted:
                    unlocked = True

        if not unlocked:
            ret['contact_info'] = "[Contact info locked until request is accepted]"

        return ret
