import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
    GET /drinks
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    selection = Drink.query.all()
    drinks = [drink.short() for drink in selection]

    return jsonify({
        'success': True,
        'drinks': drinks
    })


'''
    GET /drinks-detail
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    selection = Drink.query.all()
    drinks = [drink.long() for drink in selection]

    return jsonify({
      'success': True,
      'drinks': drinks
    })


'''
    POST /drinks
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(jwt):
    entered = request.get_json()
    new_title = entered['title']
    new_recipe = json.dumps(entered['recipe'])

    try:
        new_drink = Drink(title=new_title, recipe=new_recipe)
        new_drink.insert()
        drink = [new_drink.long()]

        return jsonify({
          'success': True,
          'drinks': drink
        })

    except:
        abort(422)


'''
    PATCH /drinks/<id>
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(jwt, id):
    try:
        drink = Drink.query.get(id)
        entered = request.get_json()
        new_title = entered.get('title', None)
        new_recipe = entered.get('recipe', None)

        if drink is None:
            abort(404)
        if new_title is not None:
            drink.title = new_title
        if new_recipe is not None:
            drink.recipe = new_recipe

        drink.update()
        updated_drink = [drink.long()]

        return jsonify({
            'success': True,
            'drinks': updated_drink
            })

    except:
        abort(422)
    


'''
    DELETE /drinks/<id>
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    try:
        drink = Drink.query.get(id)

        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
          'success': True,
          'delete': id
        })

    except:
        abort(422)



## Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def not_found_handler(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error
    })