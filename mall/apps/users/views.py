import re

from django import http
from django.contrib.auth import login, authenticate, logout
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from apps.users.models import User
from utils.response_code import RETCODE


class RegisterView(View):
    """用户注册"""
    def get(self, request):
        """
        提供注册界面
        :param request: 请求对象
        :return: 注册界面
        """
        return render(request, 'register.html')
    
    def post(self, request):
        # 获取参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
        sms_code = request.POST.get('sms_code')
        # 校验参数
        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseBadRequest('缺少必传参数')
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_]{5,20}$', username):
            return http.HttpResponseBadRequest('请输入5-20个字符的用户名')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseBadRequest('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password != password2:
            return http.HttpResponseBadRequest('两次输入的密码不一致')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('请输入正确的手机号码')
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseBadRequest('请勾选用户协议')
        # 短信验证码验证
        redis_conn = get_redis_connection('code')
        sms_code_saved = redis_conn.get('sms_%s' % mobile)
        if sms_code_saved is None:
            return render(request, 'register.html', {'sms_code_errmsg': '无效的短信验证码'})
        if sms_code != sms_code_saved.decode():
            return render(request, 'register.html', {'sms_code_errmsg': '输入短信验证码有误'})
        # 保存注册数据
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': '注册失败'})
        # 实现状态保持>>>将通过认证的用户的唯一标识信息（比如：用户ID）写入到当前session会话中
        login(request, user)
        # 响应注册结果
        response = redirect(reverse('index:index'))
        response.set_cookie('username', user.username, max_age=3600*24*15)
        return response
    

class UsernameCountView(View):
    """判断用户名是否重复注册
    1.前端输入数据
    2.发送ajax请求
    3.获取校验参数
    4.查询数据库数据count
    5.返回json数据
    """
    def get(self, request, username):
        """
        :param request: 请求对象
        :param username: 用户名
        :return: JSON
        """
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})
    
    
class MobileCountView(View):
    """判断手机号是否重复注册"""
    def get(self, request, mobile):
        """
        :param request: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})
    
 
class LoginView(View):
    """用户名登录"""
    def get(self, request):
        """
        提供登录界面
        :param request: 请求对象
        :return: 登录界面
        """
        return render(request, 'login.html')
    
    def post(self, request):
        """
        实现登录逻辑
        :param request: 请求对象
        :return: 登录结果
        """
        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')
    
        # 校验参数
        # 判断参数是否齐全
        if not all([username, password]):
            return http.HttpResponseBadRequest('缺少必传参数')
    
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            # return http.HttpResponseBadRequest('请输入正确的用户名或手机号')
            return render(request, 'login.html', {'account_errmsg': '请输入正确的用户名或手机号'})

        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            # return http.HttpResponseBadRequest('密码最少8位，最长20位')
            return render(request, 'login.html', {'account_errmsg': '密码最少8位，最长20位'})
    
        # 认证登录用户
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})
    
        # 实现状态保持
        login(request, user)
        # 设置状态保持的周期
        if remembered != 'on':
            # 没有记住用户：浏览器会话结束就过期
            request.session.set_expiry(0)
        else:
            # 记住用户：None表示两周后过期
            request.session.set_expiry(None)
            
        # 响应登录结果
        response = redirect(reverse('index:index'))

        # 注册时用户名写入到cookie，有效期15天 渲染模板数据[[]]
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        return response
    

class LogoutView(View):
    """退出登录"""
    def get(self, request):
        """实现退出登录逻辑"""
        # 清理session
        logout(request)

        # 退出登录，重定向到登录页
        response = redirect(reverse('index:index'))
        
        # 退出登录时清除cookie中的username
        response.delete_cookie('username')
        
        return response

