import re

from django.core.exceptions import ValidationError
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Client, Notification, Operator_code, Tag


class ClientSerializer(serializers.ModelSerializer):
    number = PhoneNumberField(
        validators=[UniqueValidator(queryset=Client.objects.all())],
    )
    operator_code = serializers.IntegerField(max_value=32767, min_value=0)
    tag = serializers.CharField(required=False)

    class Meta:
        model = Client
        fields = ('id', 'number', 'operator_code', 'tag', 'timezone')

    def create(self, validated_data):
        if 'tag' in validated_data:
            tag, created = Tag.objects.get_or_create(tag=validated_data['tag'])
            tag.save()
            validated_data['tag'] = tag
        operator_code, created = Operator_code.objects.get_or_create(
            operator_code=validated_data['operator_code']
        )
        validated_data['operator_code'] = operator_code
        return Client.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.number = validated_data.get('number', instance.number)
        instance.timezone = validated_data.get('timezone', instance.timezone)
        if 'operator_code' in validated_data:
            operator_code, created = Operator_code.objects.get_or_create(
                operator_code=validated_data['operator_code']
            )
            old_operator_code = instance.operator_code
            instance.operator_code = operator_code
        if 'tag' in validated_data:
            tag, created = Tag.objects.get_or_create(tag=validated_data['tag'])
            old_tag = instance.tag
            instance.tag = tag
        instance.save()
        if old_operator_code.clients.count() == 0:
            old_operator_code.delete()
        if old_tag and old_tag.clients.count() == 0:
            old_tag.delete()
        return instance

    def to_representation(self, instance):
        output = {}
        output['id'] = instance.id
        output['number'] = instance.number.as_e164
        output['operator_code'] = instance.operator_code.operator_code
        output['timezone'] = instance.timezone
        output['tag'] = instance.tag.tag
        return output


class NotificationSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    operator_codes = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=32767),
        required=False,
    )

    class Meta:
        model = Notification
        fields = ('id', 'finish_datetime', 'operator_codes',
                  'start_datetime', 'tags', 'text')

    def validate(self, attrs):
        if attrs['start_datetime'] >= attrs['finish_datetime']:
            raise ValidationError('finish time must be later than start time')
        if 'tags' in attrs:
            tags = attrs['tags']
            for tag in tags:
                if not re.fullmatch(r'^[\d\w]+$', tag):
                    raise ValidationError('field "tag" is not valid')
            if Tag.objects.filter(tag__in=tags).count() != len(tags):
                raise ValidationError('one or more tags do not exist')
        if 'operator_codes' in attrs:
            codes = attrs['operator_codes']
            if (Operator_code.objects.filter(operator_code__in=codes)
               .count() != len(codes)):
                raise ValidationError('one or more operator codes not exist')
        return attrs

    def create(self, validated_data):
        tags = validated_data.pop('tags', None)
        codes = validated_data.pop('operator_codes', None)
        notification = Notification.objects.create(**validated_data)
        if tags:
            tags = (list(tag.id for tag in Tag.objects
                    .filter(tag__in=tags))
                    )
            notification.set_tags(tags)
        if codes:
            codes = (list(code.id for code in Operator_code.objects
                     .filter(operator_code__in=codes))
                     )
            notification.set_operator_codes(codes)
        return notification

    def update(self, instance, validated_data):
        instance.finish_datetime = validated_data.get('finish_datetime')
        instance.start_datetime = validated_data.get('start_datetime')
        instance.text = validated_data.get('text')
        instance.tags.clear()
        tags = validated_data.pop('tags', None)
        if tags:
            tags = (list(tag.id for tag in Tag.objects
                    .filter(tag__in=tags))
                    )
            instance.set_tags(tags)
        instance.operator_codes.clear()
        codes = validated_data.pop('operator_codes')
        if codes:
            codes = (list(code.id for code in Operator_code.objects
                     .filter(operator_code__in=codes))
                     )
            instance.set_operator_codes(codes)
        return instance
