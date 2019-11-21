from django.conf.urls import url
from . import views

urlpatterns = [
    # 图形验证码
    url(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view(), name='image_codes'),
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view(), name='sms_codes'),
    url(r'^emails/$', views.EmailView.as_view(), name='emails'),
    url(r'^emails/verification/$', views.VerifyEmailView.as_view()),
]