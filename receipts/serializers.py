from rest_framework import serializers
from .models import Receipt


class ReceiptSerializer(serializers.ModelSerializer):
    # url = serializers.SerializerMethodField(read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name="receipt-detail",
        lookup_field="pk",
    )

    class Meta:
        model = Receipt
        fields = [
            "id",
            "title",
            "shop",
            "tag",
            "description",
            "bought_at",
            "created_at",
            "expire_at",
            "file",
            "url",
        ]

    # def get_url(self, obj):
    #     #return f"/api/receipts/{obj.pk}/"
    #     request = self.context.get('request')
    #     if request is None:
    #         return None
    #     return reverse("receipt-detail", kwargs={"pk": obj.pk}, request=request)
