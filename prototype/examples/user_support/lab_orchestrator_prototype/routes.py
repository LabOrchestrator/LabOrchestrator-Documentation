from flask import request, g, abort

from lab_orchestrator_prototype.app import app, CC, auth


@app.route("/lab_instance", methods=['GET'])
@auth.login_required
def get_lab_instances():
    r = CC.get().lab_instance_ctrl.get_list_of_user(g.user)
    return CC.get().lab_instance_ctrl.make_response(r)


@app.route("/lab_instance/<int:lab_instance_id>", methods=["GET"])
@auth.login_required
def get_lab_instance(lab_instance_id):
    r = CC.get().lab_instance_ctrl.get(lab_instance_id)
    if r.user_id != g.user.id:
        abort(403)
    return CC.get().lab_instance_ctrl.make_response(r)


@app.route('/lab_instance', methods=['POST'])
@auth.login_required
def create_lab_instance():
    lab_id = request.values.get('lab_id', type=int)
    lab = CC.get().lab_ctrl.get(lab_id)
    r = CC.get().lab_instance_ctrl.create(lab, g.user)
    return CC.get().lab_instance_ctrl.make_response(r)


@app.route('/lab_instance/<int:lab_instance_id>', methods=['DELETE'])
@auth.login_required
def delete_lab_instance(lab_instance_id):
    lab_instance = CC.get().lab_instance_ctrl.get(lab_instance_id)
    if lab_instance.user_id != g.user.id:
        abort(403)
    CC.get().lab_instance_ctrl.delete(lab_instance)
    return "", 204


@app.route("/lab_instance/<int:lab_instance_id>/virtual_machine_instances", methods=['GET'])
@auth.login_required
def get_virtual_machine_instances(lab_instance_id):
    lab_instance = CC.get().lab_instance_ctrl.get(lab_instance_id)
    if lab_instance.user_id != g.user.id:
        abort(403)
    r = CC.get().virtual_machine_instance_ctrl.get_list_of_lab_instance(lab_instance)
    return CC.get().virtual_machine_instance_ctrl.make_response(r)


@app.route("/lab_instance/<int:lab_instance_id>/virtual_machine_instances/<string:virtual_machine_instance_id>", methods=['GET'])
@auth.login_required
def get_virtual_machine_instance(lab_instance_id, virtual_machine_instance_id):
    lab_instance = CC.get().lab_instance_ctrl.get(lab_instance_id)
    if lab_instance.user_id != g.user.id:
        abort(403)
    r = CC.get().virtual_machine_instance_ctrl.get_of_lab_instance(lab_instance, virtual_machine_instance_id)
    return CC.get().virtual_machine_instance_ctrl.make_response(r)


@app.route("/lab_instance/<int:lab_instance_id>/virtual_machine_instances/<string:virtual_machine_instance_id>/vnc", methods=['GET'])
@auth.login_required
def get_vnc(lab_instance_id, virtual_machine_instance_id):
    lab_instance = CC.get().lab_instance_ctrl.get(lab_instance_id)
    if lab_instance.user_id != g.user.id:
        abort(403)
    r = CC.get().virtual_machine_instance_ctrl.get_of_lab_instance(lab_instance, virtual_machine_instance_id)
    return CC.get().virtual_machine_instance_ctrl.make_response(r)


@app.route("/docker_image", methods=["GET"])
def get_docker_images():
    r = CC.get().docker_image_ctrl.get_list()
    return CC.get().docker_image_ctrl.make_response(r)


@app.route("/docker_image/<int:docker_image_id>", methods=["GET"])
def get_docker_image(docker_image_id):
    r = CC.get().docker_image_ctrl.get(docker_image_id)
    return CC.get().docker_image_ctrl.make_response(r)


@app.route("/docker_image", methods=["POST"])
@auth.login_required
def create_docker_image():
    if not g.user.admin:
        abort(403)
    name = request.values.get('name', type=str)
    description = request.values.get('description', type=str)
    urls = request.values.get('urls', type=str)
    r = CC.get().docker_image_ctrl.create(name, description, urls)
    return CC.get().docker_image_ctrl.make_response(r)


@app.route("/docker_image/<int:docker_image_id>", methods=["DELETE"])
@auth.login_required
def delete_docker_image(docker_image_id):
    if not g.user.admin:
        abort(403)
    docker_image = CC.get().docker_image_ctrl.get(docker_image_id)
    CC.get().docker_image_ctrl.delete(docker_image)
    return "", 204


@app.route("/lab", methods=["GET"])
def get_labs():
    r = CC.get().lab_ctrl.get_list()
    return CC.get().lab_ctrl.make_response(r)


@app.route("/lab/<int:lab_id>", methods=["GET"])
def get_lab(lab_id):
    r = CC.get().lab_ctrl.get(lab_id)
    return CC.get().lab_ctrl.make_response(r)


@app.route("/lab", methods=["POST"])
@auth.login_required
def create_lab():
    if not g.user.admin:
        abort(403)
    name = request.values.get('name', type=str)
    namespace_prefix = request.values.get('namespace_prefix', type=str)
    description = request.values.get('description', type=str)
    docker_image_id = request.values.get('docker_image_id', type=int)
    docker_image_name = request.values.get('docker_image_name', type=str)
    docker_image = CC.get().docker_image_ctrl.get(docker_image_id)
    r = CC.get().lab_ctrl.create(name, namespace_prefix, description, docker_image, docker_image_name)
    return CC.get().lab_ctrl.make_response(r)


@app.route("/lab/<int:lab_id>", methods=["DELETE"])
def delete_lab(lab_id):
    if not g.user.admin:
        abort(403)
    # delete all lab_instances?
    lab = CC.get().lab_ctrl.get(lab_id)
    CC.get().lab_ctrl.delete(lab)
    return "", 204


def load_routes():
    pass