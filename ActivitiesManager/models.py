from django.db import models
from django.utils import timezone
from tagging.fields import TagField

class Activity(models.Model):
    idActivity = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128)
    description = models.TextField()
    begin_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=128, default='清华大学')
    is_public = models.BooleanField(default=False, verbose_name='公共活动')
    create_time = models.DateTimeField(default=timezone.now)
    duration = models.DurationField()
    type = models.ForeignKey('Type', related_name='type_activities', null=False)
    # tag = models.ManyToManyField('Tag', related_name='tag_activities', blank= True)
    creator = models.ForeignKey('auth.User', related_name='user_create_activities')
    tags = TagField()

    objects = models.Manager

    def __str__(self):
        return self.title



class ActivityUser(models.Model):

    VISIABLE = 'V'
    PICKED = 'P'
    ADDED = 'A'
    STATUS_CHOICES = (
        (VISIABLE, 'visiable to user'),
        (PICKED, 'picked to user\'s candidates list'),
        (ADDED, 'added to user\'s activity list'),
    )

    PRIORITY_CHOICES = (
        (1, '最低'),
        (2, '次低'),
        (3, '中等'),
        (4, '次高'),
        (5, '最高'),
    )

    idActivityUser = models.AutoField(primary_key=True)
    activity = models.ForeignKey(
        'Activity',
        related_name='activity_users',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        'auth.User',
        related_name='user_activities',
        on_delete=models.CASCADE,
    )
    enthusiasm = models.IntegerField(default=1)
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default=VISIABLE,
    )
    priority = models.IntegerField(
        default=1,
        choices=PRIORITY_CHOICES,
    )

    objects = models.Manager

    def __str__(self):
        return str(self.user) + ' ' + str(self.activity)


class Type(models.Model):
    idType = models.AutoField(primary_key=True)
    content = models.CharField(max_length=45)

    objects = models.Manager

    def __str__(self):
        return self.content



class Image(models.Model):
    idImage = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='./static/images', default='static/images/activity_default_image.jpg')
    caption = models.CharField(max_length=128)
    activity = models.ForeignKey(
        'Activity',
        on_delete=models.CASCADE,
        related_name='activity_images',
        null=True,
    )

    objects = models.Manager

    def __str__(self):
        return self.activity.title


class Avatar(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to='./static/images',
        default='static/images/user_default_avatar.jpg',
    )



