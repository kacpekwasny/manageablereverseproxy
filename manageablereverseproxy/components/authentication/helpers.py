from flask import request

def requires_authenticated_header(f):
    def wrapped():
        if request.



