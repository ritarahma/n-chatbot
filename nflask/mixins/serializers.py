import serpy


class BaseSerializer(serpy.Serializer):
    id = serpy.StrField()


class CommonSerializer(BaseSerializer):
    created_by_id = serpy.StrField()
    created_by_email = serpy.StrField()
    created_date = serpy.MethodField('get_created_date')
    updated_by_id = serpy.StrField()
    updated_by_email = serpy.StrField()
    updated_date = serpy.MethodField('get_updated_date')

    def get_created_date(self, obj):
        if obj.created_date is not None:
            return obj.created_date.strftime("%Y-%m-%d %H:%M:%S")

        return None

    def get_updated_date(self, obj):
        if obj.updated_date is not None:
            return obj.updated_date.strftime("%Y-%m-%d %H:%M:%S")

        return None

    def get_deleted_date(self, obj):
        if obj.deleted_date is not None:
            return obj.deleted_date.strftime("%Y-%m-%d %H:%M:%S")

        return None
