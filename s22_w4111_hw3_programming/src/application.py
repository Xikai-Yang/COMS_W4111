from flask import Flask, Response, request
from flask_cors import CORS
import json
from datetime import datetime

import rest_utils
from src.service_factory import ServiceFactory

app = Flask(__name__)
CORS(app)

# service_factory = dict()

service_factory = ServiceFactory()

##################################################################################################################

# DFF TODO A real service would have more robust health check methods.
# This path simply echoes to check that the app is working.
# The path is /health and the only method is GETs
@app.route("/health", methods=["GET"])
def health_check():
    rsp_data = {"status": "healthy", "time": str(datetime.now())}
    rsp_str = json.dumps(rsp_data)
    rsp = Response(rsp_str, status=200, content_type="application/json")
    return rsp


# TODO Remove later. Solely for explanatory purposes.
# The method take any REST request, and produces a response indicating what
# the parameters, headers, etc. are. This is simply for education purposes.
#
@app.route("/api/demo/<parameter1>", methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/api/demo/", methods=["GET", "POST", "PUT", "DELETE"])
def demo(parameter1=None):
    """
    Returns a JSON object containing a description of the received request.

    :param parameter1: The first path parameter.
    :return: JSON document containing information about the request.
    """

    # DFF TODO -- We should wrap with an exception pattern.
    #

    # Mostly for isolation. The rest of the method is isolated from the specifics of Flask.
    inputs = rest_utils.RESTContext(request, {"parameter1": parameter1})

    # DFF TODO -- We should replace with logging.
    r_json = inputs.to_json()
    msg = {
        "/demo received the following inputs": inputs.to_json()
    }
    print("/api/demo/<parameter> received/returned:\n", msg)

    rsp = Response(json.dumps(msg), status=200, content_type="application/json")
    return rsp

##################################################################################################################


@app.route('/')
def hello_world():
    return '<u>Hello World!</u>'


@app.route('/api/<resource_collection>', methods=['GET', 'POST'])
def do_resource_collection(resource_collection):
    """
    1. HTTP GET return all resources.
    2. HTTP POST with body --> create a resource, i.e --> database.
    :return:
    """
    request_inputs = rest_utils.RESTContext(request, resource_collection)
    svc = service_factory.get(resource_collection, None)

    if request_inputs.method == "GET":
        res = svc.get_by_template(relative_path=None,
                                  path_parameters=None,
                                  template=request_inputs.args,
                                  field_list=request_inputs.fields,
                                  limit=request_inputs.limit,
                                  offset=request_inputs.offset,
                                  order_by=request_inputs.order_by)

        res = request_inputs.add_pagination(res)
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")

    elif request_inputs.method == "POST":
        raise NotImplementedError("POST NOT IMPLEMENTED")
        # data = request_inputs.data
        # res = svc.create(data)
        #
        # headers = [{"Location", "/users/" + str(res)}]
        # if isinstance(res, int):
        #     rsp = Response("CREATED", status=201, headers=headers, content_type="text/plain")
        # else:
        #     rsp = Response(json.dumps(res, default=str), status=201, headers=headers, content_type="text/plain")
    else:
        rsp = Response("NOT IMPLEMENTED", status=501, content_type="text/plain")

    return rsp


@app.route('/api/<first_resource_collection>/<first_resource_id>/<second_resource_collection>/<second_resource_id>/<third_resource_collection>/<third_resource_id>',
           methods=['GET', 'PUT', 'DELETE'])
@app.route('/api/<first_resource_collection>/<first_resource_id>/<second_resource_collection>/<second_resource_id>/<third_resource_collection>',
           methods=['GET', 'POST'])
@app.route('/api/<first_resource_collection>/<first_resource_id>/<second_resource_collection>', methods=['GET', 'POST'])
@app.route('/api/<first_resource_collection>/<first_resource_id>/<second_resource_collection>/<second_resource_id>',
           methods=['GET', 'PUT', 'DELETE'])
def complex_resource_collection(first_resource_collection, first_resource_id, second_resource_collection=None, second_resource_id=None,
         third_resource_collection=None, third_resource_id=None):
    request_inputs = rest_utils.RESTContext(request, first_resource_collection)
    rsp = None
    new_template = {}
    if first_resource_collection is not None and first_resource_id is not None:
        new_template[first_resource_collection] = first_resource_id
    if second_resource_collection is not None and second_resource_id is not None:
        new_template[second_resource_collection] = second_resource_id
    if third_resource_collection is not None and third_resource_id is not None:
        new_template[third_resource_collection] = third_resource_id

    final_template = {**new_template, **request_inputs.args}

    if third_resource_collection is not None:
        svc = service_factory.get(third_resource_collection, None)
        if request_inputs.method == "GET":
            res = svc.get_by_template(template=final_template,
                                      field_list=request_inputs.fields,
                                      limit=request_inputs.limit,
                                      offset=request_inputs.offset,
                                      order_by=request_inputs.order_by)
            res = request_inputs.add_pagination(res)
            rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")

    elif second_resource_collection is not None:
        svc = service_factory.get(second_resource_collection)
        if request_inputs.method == "GET":
            res = svc.get_by_template(template=final_template,
                                      field_list=request_inputs.fields,
                                      limit=request_inputs.limit,
                                      offset=request_inputs.offset,
                                      order_by=request_inputs.order_by
                                      )
            rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")

    return rsp



@app.route('/api/<resource_collection>/<resource_id>', methods=['GET', 'PUT', 'DELETE'])
def specific_resource(resource_collection, resource_id):
    """
    1. Get a specific one by ID.
    2. Update body and update.
    3. Delete would ID and delete it.
    :param user_id:
    :return:
    """
    request_inputs = rest_utils.RESTContext(request, resource_collection)
    svc = service_factory.get(resource_collection, None)

    if request_inputs.method == "GET":
        res = svc.get_resource_by_id(resource_id)
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    elif request_inputs.method == "DELETE":
        res = svc.delete_resource_by_id(resource_id)
        rsp = Response(json.dumps(res,default=str), status=200, content_type="application/json")
    elif request_inputs.method == "PUT":
        data = request_inputs.data
        res = svc.update_resource_by_id(resource_id, data)
        rsp = Response(json.dumps(res,default=str), status=200, content_type="application/json")
    else:
        rsp = Response("NOT IMPLEMENTED", status=501, content_type="text/plain")

    return rsp




if __name__ == '__main__':

    app.run(host="0.0.0.0", port=5003)
