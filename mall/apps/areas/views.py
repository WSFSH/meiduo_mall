import json
import re

from django import http
from django.core.cache import cache
from django.http import JsonResponse
from django.views import View

from apps.areas.models import Area, Address
from utils import constants
from utils.response_code import RETCODE
from utils.views import LoginRequiredJSONMixin


class AreasView(View):
    """省市区数据"""

    def get(self, request):
        """提供省市区数据"""
        area_id = request.GET.get('area_id')

        if not area_id:
            # 读取cache缓存的数据
            province_list = cache.get('province_list')
            if not province_list:
                # 提供省份数据
                try:
                    # 查询省份数据
                    province_model_list = Area.objects.filter(parent__isnull=True)
    
                    # 序列化省级数据
                    province_list = []
                    for province_model in province_model_list:
                        province_list.append({'id': province_model.id, 'name': province_model.name})
                    # 缓存省份数据
                    cache.set('province_list', province_list, 3600)
                except Exception as e:
                    return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '省份数据错误'})

            # 响应省份数据
            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
        else:
            sub_data = cache.get('sub_' + area_id)
            if not sub_data:
                # 提供市或区数据
                try:
                    parent_model = Area.objects.get(id=area_id)  # 查询市或区的父级
                    sub_model_list = parent_model.subs.all()
    
                    # 序列化市或区数据
                    sub_list = []
                    for sub_model in sub_model_list:
                        sub_list.append({'id': sub_model.id, 'name': sub_model.name})
    
                    sub_data = {
                        'id': parent_model.id,  # 父级pk
                        'name': parent_model.name,  # 父级name
                        'subs': sub_list  # 父级的子集
                    }
                    cache.set('sub_' + area_id, sub_data, 3600)
                except Exception as e:
                    return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '城市或区数据错误'})

            # 响应市或区数据
            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})
        
        
class CreateAddressView(LoginRequiredJSONMixin, View):
    """新增地址"""
    def post(self, request):
        """实现新增地址逻辑"""
        # 判断是否超过地址上限：最多20个
        # Address.objects.filter(user=request.user).count()
        count = request.user.addresses.count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超过地址数量上限'})

        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseBadRequest('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseBadRequest('参数email有误')

        # 保存地址信息
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )

            # 设置默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        # 新增地址成功，将新增的地址响应给前端实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应保存结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})
    
    
class UpdateDestroyAddressView(LoginRequiredJSONMixin, View):
    """修改地址"""

    def put(self, request, address_id):
        """修改地址"""
        # 判断当前收货地址是否是属于当前用户
        address = Address.objects.get(id=address_id)
        if not (address and address.user == request.user):
            return http.HttpResponseBadRequest('非法操作')

        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseBadRequest('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseBadRequest('参数email有误')

        # 判断地址是否存在,并更新地址信息
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新地址失败'})

        # 构造响应数据
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应更新地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})

    def delete(self, request, address_id):
        """删除地址"""
        # 判断当前收货地址的id是否是属于当前用户
        address = Address.objects.get(id=address_id)
        if not (address and address.user == request.user):
            return http.HttpResponseBadRequest('非法操作')
    
        try:
            # 将地址逻辑删除设置为True
            address.is_deleted = True
            address.save()
        except Exception as e:
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})
    
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})
    
    
class DefaultAddressView(LoginRequiredJSONMixin, View):
    """设置默认地址"""

    def put(self, request, address_id):
        """设置默认地址"""
        # 判断当前收货地址的id是否是属于当前用户
        address = Address.objects.get(id=address_id)
        if not (address and address.user == request.user):
            return http.HttpResponseBadRequest('非法操作')

        try:
            # 设置地址为默认地址
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})

        # 响应设置默认地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置默认地址成功'})
    
    
class UpdateTitleAddressView(LoginRequiredJSONMixin, View):
    """设置地址标题"""

    def put(self, request, address_id):
        """设置地址标题"""
        # 判断当前收货地址的id是否是属于当前用户
        address = Address.objects.get(id=address_id)
        if not (address and address.user == request.user):
            return http.HttpResponseBadRequest('非法操作')

        # 接收参数：地址标题
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')

        try:
            # 设置新的地址标题
            address.title = title
            address.save()
        except Exception as e:
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置地址标题失败'})

        # 4.响应删除地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置地址标题成功'})