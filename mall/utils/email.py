from django.conf import settings
from django.core.mail import send_mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData

from apps.users.models import User


class Email(object):
    """pip install -U itsdangerous
    使用固定密钥/字符串进行加密
    """
    @staticmethod
    def send_verify_email(to_email, verify_url):
        """
        发送验证邮箱邮件
        :param to_email: 收件人邮箱
        :param verify_url: 验证链接
        :return: None
        """
        subject = "美多商城邮箱验证"
        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用美多商城。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)
        try:
            send_mail(subject, "", settings.EMAIL_FROM, [to_email], html_message=html_message)
        except Exception as e:
            print(e)
            return False
        else:
            return True

    @staticmethod
    def generate_verify_email_url(user):
        """
        生成邮箱验证链接
        :param user: 当前登录用户
        :return: verify_url
        """
        serializer = Serializer(settings.SECRET_KEY, expires_in=3600)
        data = {
            'user_id': user.id,
            'email': user.email
        }
        token = serializer.dumps(data).decode()
        verify_url = settings.EMAIL_VERIFY_URL + '?token=' + token
        return verify_url

    @staticmethod
    def verify_email(token):
        """
        验证token并提取user
        :param token: 用户信息签名后的结果
        :return: user, None
        """
        serializer = Serializer(settings.SECRET_KEY, expires_in=3600)
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            user_id = data.get('user_id')
            email = data.get('email')
            try:
                user = User.objects.get(id=user_id, email=email)
            except User.DoesNotExist:
                return None
            else:
                return user

    @classmethod
    def send_email(cls, request, email):
        verify_url = cls.generate_verify_email_url(request.user)
        ret = cls.send_verify_email(email, verify_url)
        return ret