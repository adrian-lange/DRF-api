from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.db.models import Q
from django.conf import settings
import os
from django.core.exceptions import ValidationError
from django_uuid_upload import upload_to_uuid


User = settings.AUTH_USER_MODEL


class ReceiptQuerySet(models.QuerySet):
    def search(self, query, user=None):
        lookup = (
            Q(title__icontains=query)
            | Q(shop__icontains=query)
            | Q(tag__icontains=query)
            | Q(description__icontains=query)
        )
        qs = self.filter(lookup)
        if user is not None:
            qs = qs.filter(user=user)
        return qs


class ReceiptManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return ReceiptQuerySet(self.model, using=self._db)

    def search(self, query, user=None):
        return self.get_queryset().serach(query, user=user)


def validate_file(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = [
        ".pdf",
        ".jpg",
        ".png",
    ]
    filesize = value.size
    if not ext.lower() in valid_extensions:
        raise ValidationError("Unsupported file extension.")
    if filesize > 10485760:
        raise ValidationError("The maximum file size that can be uploaded is 10MB")


def user_directory_path(instance, filename):
    #     #return 'receipts/shop_{0}/{1}'.format(instance.shop, filename)
    return "receipts/{0}/{1}".format(instance.user.id, filename)


class Receipt(models.Model):
    title = models.CharField(max_length=50)
    shop = models.CharField(max_length=50, null=True)
    tag = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=50, null=True)
    bought_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField()
    file = models.FileField(upload_to=upload_to_uuid(""), validators=[validate_file])
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)

    objects = ReceiptManager()


def delete_file_if_unused(model, instance, field, instance_file_field):
    dynamic_field = {}
    dynamic_field[field.name] = instance_file_field.name
    other_refs_exist = (
        model.objects.filter(**dynamic_field).exclude(pk=instance.pk).exists()
    )
    if not other_refs_exist:
        instance_file_field.delete(False)


""" Whenever ANY model is deleted, if it has a file field on it, delete the associated file too"""


@receiver(post_delete)
def delete_files_when_row_deleted_from_db(sender, instance, **kwargs):
    for field in sender._meta.concrete_fields:
        if isinstance(field, models.FileField):
            instance_file_field = getattr(instance, field.name)
            delete_file_if_unused(sender, instance, field, instance_file_field)


""" Delete the file if something else get uploaded in its place"""


@receiver(pre_save)
def delete_files_when_file_changed(sender, instance, **kwargs):
    # Don't run on initial save
    if not instance.pk:
        return
    for field in sender._meta.concrete_fields:
        if isinstance(field, models.FileField):
            # its got a file field. Let's see if it changed
            try:
                instance_in_db = sender.objects.get(pk=instance.pk)
            except sender.DoesNotExist:
                # We are probably in a transaction and the PK is just temporary
                # Don't worry about deleting attachments if they aren't actually saved yet.
                return
            instance_in_db_file_field = getattr(instance_in_db, field.name)
            instance_file_field = getattr(instance, field.name)
            if instance_in_db_file_field.name != instance_file_field.name:
                delete_file_if_unused(
                    sender, instance, field, instance_in_db_file_field
                )
