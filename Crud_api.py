from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
import random
import json
import json
from datetime import datetime

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost/Hporter'
mongo = PyMongo(app)
id_list=[]

data = [
    {'id': random.randint(1,100),
     'name': "Harry Potter and the Order of the Phoenix",
     'img': "https://bit.ly/2IcnSwz",
     'summary': "Harry Potter and Dumbledore's warning about the return of Lord Voldemort is not heeded by the wizard authorities who, in turn, look to undermine Dumbledore's authority at Hogwarts and discredit Harry."
     },
    {'id': 2,
     'name': "The Lord of the Rings: The Fellowship of the Ring",
     'img': "https://bit.ly/2tC1Lcg",
     'summary': "A young hobbit, Frodo, who has found the One Ring that belongs to the Dark Lord Sauron, begins his journey with eight companions to Mount Doom, the only place where it can be destroyed."
     },
    {
        'id': 3,
     'name': "Avengers: Endgame",
     'img': "https://bit.ly/2Pzczlb",
     'summary': "Adrift in space with no food or water, Tony Stark sends a message to Pepper Potts as his oxygen supply starts to dwindle. Meanwhile, the remaining Avengers -- Thor, Black Widow, Captain America, and Bruce Banner -- must figure out a way to bring back their vanquished allies for an epic showdown with Thanos -- the evil demigod demigod who decimated the planet and the universe."
     }
]

def initialData():
    porters = mongo.db.porters
    for d in data:
        porters.insert_one(d)

if mongo.db.porters.count_documents({}) == 0:
    initialData()



def save_response_to_json(response_data, filename):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_to_write = {
        'timestamp': timestamp,
        'response': response_data
    }
    with open(filename, 'a') as f:
        json.dump(data_to_write, f, indent=4)
        f.write('\n')



@app.route('/porters', methods=['GET'])
def getPorters():
    porters = mongo.db.porters.find()
    output = []
    for porter in porters:
        output.append({
            'id': porter['id'],
            'name': porter['name'],
            'img': porter['img'],
            'summary': porter['summary']
        })
    responseData = {'result from get request': output}
    save_response_to_json(responseData, 'api_responses.json')

    return jsonify(responseData)

@app.route('/porters', methods=['POST'])
def addPorter():
    data = request.json
    name = data.get('name')
    img = data.get('img')
    summary = data.get('summary')
    if name or img or summary:
        lastPorter = mongo.db.porters.find().sort([('id', -1)]).limit(1)
        last_id = -1
        for porter in lastPorter:
            lastId = porter['id']

        newId = lastId + 1
        porter_id = mongo.db.porters.insert_one({
            'id': newId,
            'name': name,
            'img': img,
            'summary': summary
        })
        new_porter = mongo.db.porters.find_one({'_id': porter_id.inserted_id})
        response_data = [
            {'message': "New added"},
            {
                'id': new_porter['id'],
                'name': new_porter['name'],
                'img': new_porter['img'],
                'summary': new_porter['summary']
            }]
        save_response_to_json(response_data, 'api_responses.json')

        return jsonify(response_data), 201

    return jsonify({'error': 'data missing'}), 400


@app.route('/porters/<id>', methods=['PATCH'])
def update_porter_by_id(id):
    id = int(id)
    data = request.json
    name = data.get('name')
    img = data.get('img')
    summary = data.get('summary')
    porter = mongo.db.porters.find_one({'id': id})
    if porter:
        if name is not None or img is not None or summary is not None:
            update_data = {}
            if name:
                update_data['name'] = name
            if img:
                update_data['img'] = img
            if summary:
                update_data['summary'] = summary
            print("Update data:", update_data)
            if update_data:
                result = mongo.db.porters.update_one({'id': id}, {'$set': update_data})
                print("Update result:", result)
                if result.modified_count == 1:
                    updated_porter = mongo.db.porters.find_one({'id': id})
                    return jsonify({
                        'message': f'Updated with {id}',
                        'porter': {
                            'id': updated_porter['id'],
                            'name': updated_porter['name'],
                            'img': updated_porter['img'],
                            'summary': updated_porter['summary']
                        }
                    }), 200
                else:
                    return jsonify({'message': 'Failed to update porter,largely  occurs when provided duplicate data'}), 500
            else:
                return jsonify({'message': 'No fields provided for update'}), 400
        else:
            return jsonify({'message': 'No fields provided for update'}), 400
    else:
        return jsonify({'message': 'Porter not found'}), 404


@app.route('/porters/<id>', methods=['DELETE'])
def delete_porter(id):
    try:
        id = int(id)
    except ValueError:
        return jsonify({'message': 'ID must be an integer'}), 400

    result = mongo.db.porters.delete_one({'id': id})
    if result.deleted_count == 1:
        response_data = {'message': f'deleted with id ={id}'}
    else:
        response_data = {'message': 'not found'}
    save_response_to_json(response_data, 'api_responses.json')
    return jsonify(response_data)


if __name__ == '__main__':
    app.run()
