from flask import Flask, jsonify, request
import json
import os
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

app = Flask(__name__)

# Load GeoJSON data
def load_geojson(file_path):
    with open(file_path) as f:
        return json.load(f)

geojson_data = load_geojson(os.path.join(os.path.dirname(__file__), 'data/places.geojson'))

# OGC API - Features: Landing page
@app.route('/')
def landing_page():
    return jsonify({
        'links': [
            {
                'rel': 'self',
                'type': 'application/json',
                'title': 'This document',
                'href': 'http://localhost:5000'
            },
            {
                'rel': 'data',
                'type': 'application/json',
                'title': 'Local GeoJSON Data',
                'href': 'http://localhost:5000/collections/features/items'
            }
        ]
    })

# OGC API - Features: Collections endpoint
@app.route('/collections')
def collections():
    return jsonify({
        'collections': [
            {
                'id': 'features',
                'title': 'Local GeoJSON Features',
                'description': 'A collection of point and polygon features',
                'links': [
                    {
                        'rel': 'items',
                        'href': 'http://localhost:5000/collections/features/items',
                        'type': 'application/geo+json'
                    }
                ]
            }
        ]
    })

# OGC API - Features: Items (Features) endpoint
@app.route('/collections/features/items', methods=['GET'])
def get_features():
    return jsonify(geojson_data)

# OGC API - Features: Single Feature endpoint
@app.route('/collections/features/items/<int:feature_id>', methods=['GET'])
def get_feature(feature_id):
    feature = next((f for f in geojson_data['features'] if f['properties']['id'] == feature_id), None)
    if feature:
        return jsonify(feature)
    else:
        return jsonify({'error': 'Feature not found'}), 404

# Buffer FeatureCollection endpoint
@app.route('/process/buffer', methods=['POST'])
def buffer_features():
    data = request.get_json()

    # Validate the input
    if 'features' not in data or 'buffer_distance' not in data:
        return jsonify({'error': 'Invalid input. Must contain "features" and "buffer_distance".'}), 400
    
    buffer_distance = data['buffer_distance']
    feature_collection = data['features']

    if feature_collection['type'] != 'FeatureCollection':
        return jsonify({'error': 'Input must be a FeatureCollection'}), 400

    buffered_features = []

    # Apply buffer to each feature's geometry
    for feature in feature_collection['features']:
        geom = shape(feature['geometry'])
        buffered_geom = geom.buffer(buffer_distance)

        buffered_feature = {
            'type': 'Feature',
            'geometry': mapping(buffered_geom),
            'properties': feature['properties']
        }
        buffered_features.append(buffered_feature)

    buffered_feature_collection = {
        'type': 'FeatureCollection',
        'features': buffered_features
    }

    return jsonify(buffered_feature_collection), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
