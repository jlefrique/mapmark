#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from urllib import urlopen, urlencode

NOMINATIM_URL = "http://open.mapquestapi.com/nominatim/v1/search?format=json&%s"


class MapmarkException(Exception):
    pass


class Mapmark(object):

    def get_coordinates(self, place):
        """Returns the coordinates of the given location."""

        req = urlopen(NOMINATIM_URL % urlencode({'q': place}))
        geo_value = json.loads(req.read())
        if len(geo_value) == 0:
            raise MapmarkException('Coordinates not found.')

        return (float(geo_value[0]['lon']), float(geo_value[0]['lat']))

    def place_to_geojson(self, place):
        """Generates a GeoJSON object for the given place."""

        point = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [None, None]
            },
            "properties": {
                "name": place,
                'show_on_map': False}
        }

        try:
            (lon, lat) = self.get_coordinates(place)

            point["geometry"]["coordinates"] = [lon, lat]
            point["properties"]["show_on_map"] = True

        except MapmarkException:
            print("Unable to find coordinates.")

        return point

    def generate(self, input, output):
        """Generates a GeoJSON file from a text file containing locations."""

        features = []

        print("Converting locations to GeoJSON...")

        with open(input, 'r') as f:
            for place in f.readlines():
                features.append(self.place_to_geojson(place.rstrip()))

        geojson = {
                "type": "FeatureCollection",
                "features": features,
        }

        with open(output, 'w') as f:
            f.write(json.dumps(geojson, indent=4))

        print("done")


def main(input, output):

    Mapmark().generate(input, output)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
            description='Generates a GeoJSON file from a file containing\
                    locations.')
    parser.add_argument('-i', '--input', help='Input text file',
                        default='locations.txt')
    parser.add_argument('-o', '--output', help='Output file (GeoJSON)',
                        default='locations.geojson')

    args = parser.parse_args()

    main(** vars(args))
