import requests

from flask import Flask, request, Response


class ManageableReverseProxy(Flask):
    """
    """
    SITE_NAME = "http://localhost:5000"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


mrp = ManageableReverseProxy()

@mrp.route('/', defaults={'path': ''})
@mrp.route("/<path:path>",methods=["GET","POST","DELETE"])
def proxy(path):
    start = perf_counter()
    try:
        global SITE_NAME
        if request.method=="GET":
            resp = requests.get(f"{SITE_NAME}{path}", headers=request.headers, cookies=request.cookies, allow_redirects=False)
            excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
            headers = [(name, value) for (name, value) in  resp.raw.headers.items() if name.lower() not in excluded_headers]
            response = Response(resp.content.decode(errors="replace").replace("facebook.com", "/").encode(), resp.status_code, headers)
            return response
        
        elif request.method=="POST":
            print(request.headers)
            content_type = request.headers["Content-Type"]
            if content_type == "application/x-www-form-urlencoded":
                # all data is in the url
                resp = requests.post(f"{SITE_NAME}{path}", headers=request.headers, cookies=request.cookies, allow_redirects=False)
    
            elif content_type == "application/json":
                resp = requests.post(f"{SITE_NAME}{path}",headers=request.headers, cookies=request.cookies, json=request.get_json(), allow_redirects=False)
    
            excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
            headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
            response = Response(resp.content, resp.status_code, headers)
            return response
        
        elif request.method=="DELETE":
            resp = requests.delete(f"{SITE_NAME}{path}", allow_redirects=False).content
            response = Response(resp.content, resp.status_code, headers)
            return response
    except Exception as e:
        print(e)
        return "awd"
    finally:
        print(f"{perf_counter()-start=}")


    
if __name__ == "__main__":
    mrp.run(debug=True, port=80)