from django.core.mail import send_mail
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Activity, ActivityUser, Type
from .forms import ActivityForm
from  datetime  import  *

#发送邮件，提醒一天后将要发生的活动
def send_remind_mails():
    #my_email_address = "thss15_zhangqr@163.com"
    email_query_set = ActivityUser.objects.all().filter(status='A')
    today = datetime.today()
    #print(email_query_set)
    for item in email_query_set:
        activity_name = item.activity.title
        t = item.activity.begin_time
        activity_start_time = datetime.strftime(item.activity.begin_time,'%Y-%m-%d %H:%M:%S')
        if t.year==today.year and t.month==today.month and t.day-today.day==1:
            user_email = item.user.email
            send_mail(
            '来自动规的活动提醒',
            '您在本网站安排的活动:' + activity_name + "将在" + activity_start_time + "开始，请记得及时参加哦～",
            'thss15_zhangqr@163.com',
            [user_email],
            fail_silently=False,)
    