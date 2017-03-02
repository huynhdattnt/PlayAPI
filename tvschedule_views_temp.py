# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify, json, current_app
from ...restApi.models import mdb
from ...extensions import cache
from ...decorators import get_user_info
from ..helper.tvschedule_helper import tvschedule_list_make_up, check_request_date
from ...utils import convert_to_int, make_cross_domain_response, define_user_geoip, make_response_dict
from datetime import datetime, timedelta
import time

restTemp_tvschedule4 = Blueprint('restTemp_tvschedule4', __name__, url_prefix='/api_temp/ver4')

@restTemp_tvschedule4.route('/tvschedule/<string:channel_id>', methods=['GET'])
def get_tvschedule_list(channel_id):
    #get and validate parameters
    page            = convert_to_int(request.values.get('page'))
    if not page:
        page = int(1)
    per_page        = convert_to_int(request.values.get('per_page'))  #0 meaning get all
    if not per_page:
        per_page = int(50)

    day             = request.values.get('day')
    day             = check_request_date(day, "%d-%m-%Y")
    if not day:
        return_data = make_response_dict(status=0, error_code=1, msg='Cannot convert day "%s" to datetime' % day, data={})
        return make_cross_domain_response(return_data, 400)

    @cache.memoize(600)
    def cached_get_tvschedule_list4(channel_id, day, page, per_page):
        start_time  = datetime.strptime(day, '%d-%m-%Y')
        end_time    = start_time + timedelta(days=1)
        query       = mdb.TVSchedule.get_by_channel_n_time_range_pagi(channel_id, start_time, end_time, page, per_page)
        result      = {}
        if query:
            result['total_found']   = query['total']
            result['total_page']    = query['total_page']
            result['page']          = page
            result['per_page']      = per_page
            result['schedule_list'] = tvschedule_list_make_up(query['items'])
        return result


    data    = cached_get_tvschedule_list4(channel_id, day, page, per_page)
    if not data:
        return_data = make_response_dict(status=0, error_code=2,\
                        msg='Something wrong with inputted parameter. channel_id=%s, day=%s, page=%s, per_page=%s' % (channel_id, day, page, per_page), data={})
        return make_cross_domain_response(return_data, 400)

    return_data = make_response_dict(status=1, error_code=0, msg='Success', data=data)
    return make_cross_domain_response(return_data)
