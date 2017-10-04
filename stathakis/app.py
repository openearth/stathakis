#!/usr/bin/env python3

import connexion
import flask_cors


def make_app():
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.add_api('swagger.yaml', arguments={'title': 'This API allows you to retrieve realtime and historic measurements. It is a frontend for measurements from other sources. It is intended for stations or gridded timeseries.'})
    # add CORS to the app, should not have any secure api's
    flask_cors.CORS(app.app)
    return app
