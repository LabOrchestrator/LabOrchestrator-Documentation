import sqlalchemy as sql

from lab_orchestrator_prototype.app import db


class DockerImage(db.Model):
    __tablename__ = 'docker_image'
    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String(32), unique=True)
    description = sql.Column(sql.String(128))
    url = sql.Column(sql.String(256))


class Lab(db.Model):
    __tablename__ = 'lab'
    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String(32), unique=True)
    namespace_prefix = sql.Column(sql.String(32), unique=True)
    description = sql.Column(sql.String(128))
    docker_image_id = sql.Column(sql.Integer, sql.ForeignKey('docker_image.id'))
    docker_image_name = sql.Column(sql.String(32))


class LabInstance(db.Model):
    __tablename__ = 'lab_instance'
    id = sql.Column(sql.Integer, primary_key=True)
    lab_id = sql.Column(sql.Integer, sql.ForeignKey('lab.id'))
    user_id = sql.Column(sql.Integer, sql.ForeignKey('users.id'))
