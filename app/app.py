from flask import Flask, render_template #, request
from app.galcat.core import *
import urllib.parse
import json
import os

app_portal = Flask(__name__)


# Redirect to the main page
@app_portal.route('/')
@app_portal.route('/index')
@app_portal.route('/index.html')
def app_home():
    db_name = os.environ.get('CATALOG_NAME')
    mongo_client = os.environ.get('SERVER_MONGO')

    db = Database(conn_string=mongo_client, mongo_db_name=db_name, collection_name='galaxies',
                  references_file='app/static/references.json')

    temp = db.query_table({})
    df = temp.to_pandas()
    df.drop('_id', axis=1, inplace=True)

    df['name'] = df['name'].apply(lambda x: '<a href="summary/{0}">{0}</a>'.format(x))

    return render_template('index.html', table=df.to_html(classes='display', index=False, escape=False))


@app_portal.route('/summary/<string:name>')
def app_summary(name):
    db = Database(conn_string='localhost', mongo_db_name='GalaxyCat', collection_name='galaxies',
                  references_file='static/references.json')

    name = urllib.parse.unquote_plus(name)

    doc = db.query({'name': name})
    if len(doc) != 1:
        raise RuntimeError

    doc = doc[0]
    del doc['_id']
    doc = db._recursive_json_reverse_fix(doc)

    nice_json = json.dumps(doc, indent=4, sort_keys=False)

    return render_template('summary.html', json=nice_json)
