#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

import request_object
import scoring

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}


def is_admin(request_obj):
    return request_obj.login == ADMIN_LOGIN


def check_auth(request):
    if is_admin(request):
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(
            (request.account or '') +
            (request.login or '') +
            SALT
        ).hexdigest()

    # for debug only
    logging.debug('correct digest: %s', digest)

    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    req_obj = request_object.MethodRequest(request['body'])
    errors = req_obj.get_validation_errors()
    if errors:
        return errors, INVALID_REQUEST

    if not check_auth(req_obj):
        return ERRORS[FORBIDDEN], FORBIDDEN

    if req_obj.method == 'online_score':
        online_score_obj = request_object.OnlineScoreRequest(req_obj.arguments)

        errors = online_score_obj.get_validation_errors()
        if errors:
            return errors, INVALID_REQUEST

        ctx['has'] = online_score_obj.initialized_fields

        if is_admin(req_obj):
            score = 42
        else:
            score = scoring.get_score(**online_score_obj.asdict())
        return {'score': score}, OK

    elif req_obj.method == 'clients_interests':
        client_interests_obj = request_object.ClientsInterestsRequest(req_obj.arguments)
        errors = client_interests_obj.get_validation_errors()
        if errors:
            return errors, INVALID_REQUEST

        ctx['nclients'] = client_interests_obj.nclients
        interests = {
            client_id: scoring.get_interests(client_id)
            for client_id in client_interests_obj.client_ids
        }
        return interests, OK

    return None, OK


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except Exception:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception, e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
