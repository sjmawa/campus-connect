from rest_framework import serializers

from .models import LostFoundItem


class LostFoundItemSerializer(serializers.ModelSerializer):
    reported_by = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = LostFoundItem
        fields = (
            'id',
            'title',
            'description',
            'item_type',
            'category',
            'location',
            'image_url',
            'contact_info',
            'date_seen',
            'found_at',
            'status',
            'reported_by',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'reported_by', 'created_at', 'updated_at')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        contact = ret.get('contact_info')
        if not contact or contact.strip() in ['', 'Contact me via app', 'C']:
            ret['contact_info'] = instance.user.email
        return ret

