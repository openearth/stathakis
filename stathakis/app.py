#!/usr/bin/env python3

import connexion

if __name__ == '__main__':
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.add_api('swagger.yaml', arguments={'title': 'This API allows you to retrieve realtime and historic measurements. It is a frontend for measurements from other sources. It is intended for stations or gridded timeseries.'})
    app.run(port=8080)
