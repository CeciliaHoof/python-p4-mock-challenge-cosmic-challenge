#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api=Api(app)

@app.route('/')
def home():
    return ''

class Scientists(Resource):
    def get(self):
        scientists = [scientist.to_dict(rules = ('-missions',)) for scientist in Scientist.query.all()]
        return make_response(scientists, 200)
    
    def post(self):
        scientist_json = request.get_json()
        try:
            scientist = Scientist(**scientist_json)
        except ValueError as e:
            return make_response({'errors': ['validation errors']}, 400)
        db.session.add(scientist)
        db.session.commit()
        return make_response(scientist.to_dict(), 201)
        
class ScientistsById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if not scientist:
            return make_response({'error': 'Scientist not found'}, 404)
        return make_response(scientist.to_dict(), 200)
    
    def patch(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if not scientist:
            return make_response({'error': 'Scientist not found'}, 404)
        scientist_json = request.get_json()
        try:
            for k, v in scientist_json.items():
                setattr(scientist, k, v)
        except ValueError as e:
            return make_response({'errors': ['validation errors']}, 400)
        db.session.commit()
        return make_response(scientist.to_dict(), 202)
    
    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if not scientist:
            return make_response({'error': 'Scientist not found'}, 404)
        db.session.delete(scientist)
        db.session.commit()
        return make_response({}, 204)

class Planets(Resource):
    def get(self):
        planets = [planet.to_dict(rules = ('-missions',)) for planet in Planet.query.all()]
        return make_response(planets, 200)

class Missions(Resource):
    def post(self):
        mission_json = request.get_json()
        try:
            mission = Mission(**mission_json)
        except ValueError as e:
            return make_response({'errors': ['validation errors']}, 400)
        db.session.add(mission)
        db.session.commit()
        return make_response(mission.to_dict(), 201)

api.add_resource(Scientists, '/scientists')
api.add_resource(ScientistsById, '/scientists/<int:id>')
api.add_resource(Planets, '/planets')
api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
