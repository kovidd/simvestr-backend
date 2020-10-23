# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 12:07:31 2020

@author: Kovid
"""
import numpy as np
from flask_restx import abort, reqparse
from functools import wraps
from simvestr.apis.verifytoken import validate_passed_token, AuthenticationToken


SECRET_KEY = "thisismysecretkeydonotstealit"
EXPIRES_IN = 86400  # 24 Hours
auth = AuthenticationToken(SECRET_KEY, EXPIRES_IN)


token_parser = reqparse.RequestParser()
token_parser.add_argument('token', location='cookies')


        
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        arg = token_parser.parse_args() # From http cookies
        token = arg.get("token")
        try:
            user = auth.validate_token(token)
        except Exception as e:
            abort(401, e)
        return f(*args, **kwargs)
    
    return decorated

def get_email():
    arg = token_parser.parse_args() # From http cookies
    token = arg.get("token")
    passed, param =  validate_passed_token(token)
    if passed:
        return param
    return False