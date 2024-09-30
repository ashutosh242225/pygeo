import json
from pygeoapi.process.base import BaseProcess
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

class BufferProcess(BaseProcess):
    """Buffer Process"""
    
    def __init__(self, name, description, data, id_field):
        super().__init__(name, description, data, id_field)

    def execute(self, features, buffer_distance):
        """Buffer the input features"""
        buffered_features = []
        for feature in features:
            geom = shape(feature['geometry'])
            buffered_geom = geom.buffer(buffer_distance)
            buffered_features.append({
                'type': 'Feature',
                'geometry': mapping(buffered_geom),
                'properties': feature['properties']
            })
        return {'type': 'FeatureCollection', 'features': buffered_features}

# Register the process in your application
def register(app):
    app.add_process(BufferProcess)
