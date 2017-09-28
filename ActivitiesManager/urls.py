from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.index, name = 'index'),
    url(r'^activity/([1-9][0-9]*)$', views.activity, name='activity'),
    url(r'^activity/submit/([1-9][0-9]*)$', views.activity_submit, name='activity-submit'),
    url(r'^activity/unsubmit/([1-9][0-9]*)$',views.activity_unsubmit,name='activity-unsubmit'),
    url(r'^activity/delete/([1-9][0-9]*)$', views.activity_delete, name='activity-delete'),
    url(r'^create', views.create, name='create'),
    url(r'^login', views.login, name='login'),
    url(r'^authenticate$', views.authenticate, name='authenticate'),
    url(r'^signup$', views.signup, name='signup'),
    url(r'^signup/submit$', views.signup_submit, name='signup-submit'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^homepage$', views.homepage, name='homepage'),
    url(r'^manage$',views.manage,name='manage'),
    url(r'^userinfo$',views.userinfo,name='userinfo'),
    url(r'^userinfo/submit$', views.userinfo_submit, name='userinfo-submit'),
    url(r'^schedule/priority$',views.dp_schedule_by_priority,name='schedule-priority'),
    url(r'^schedule/amount$',views.dp_schedule_by_amount,name='schedule-amount'),
    url(r'^upload$', views.upload_file, name='upload'),
    url(r'^exception$',views.exception, name='exception'),
    url(r'^search$',views.search, name='search'),
    url(r'^search/result$',views.search_result, name='search-result'),
    url(r'^help$',views.help, name='help'),

]
