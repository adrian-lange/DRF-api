class UserQuerySetMixin:
    user_field = "user_id"

    def get_queryset(self, *args, **kwargs):
        lookup_data = {}
        lookup_data[self.user_field] = self.request.user.id
        print(lookup_data)
        qs = super().get_queryset(*args, **kwargs)
        print(qs)
        return qs.filter(**lookup_data)
