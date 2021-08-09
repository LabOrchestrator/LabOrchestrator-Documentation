import os
import time
from flask import abort, request, jsonify, g, url_for
import jwt
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sql

from lab_orchestrator_prototype.app import app, db, auth


class User(db.Model):
    __tablename__ = 'users'
    id = sql.Column(sql.Integer, primary_key=True)
    username = sql.Column(sql.String(32), index=True)
    password_hash = sql.Column(sql.String(128))
    admin = sql.Column(sql.Boolean)
    lab_instances = relationship("LabInstance")

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=600):
        return jwt.encode(
            {'id': self.id, 'exp': time.time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except:
            return
        return User.query.get(data['id'])


def create_admin(username, password):
    user = User.query.filter_by(username=username).first()
    if user is not None:
        if user.admin:
            return user
        user.admin = True
        user.hash_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    user = User(username=username, admin=True)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return user


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username, 'admin': user.admin})


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})

