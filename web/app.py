from elasticsearch import Elasticsearch, exceptions
import os
import time
from flask import Flask, jsonify, request, render_template
import sys
import requests
import json

es = Elasticsearch(host='es')

app = Flask(__name__)

def load_data_in_es():
    """ creates an index in elasticsearch """
    file = "./sample_data.json"
    with open(file) as f:
        data = json.load(f)

    print("Loading data in elasticsearch ...")
    for id, truck in enumerate(data):
        res = es.index(index="sfdata", doc_type="truck", id=id, body=truck)

def safe_check_index(index, retry=3):
    """ connect to ES with retry """
    if not retry:
        print("Out of retries. Bailing out...")
        sys.exit(1)
    try:
        status = es.indices.exists(index)
        return status
    except exceptions.ConnectionError as e:
        print("Unable to connect to ES. Retrying in 5 secs...")
        time.sleep(5)
        safe_check_index(index, retry-1)

def format_fooditems(string):
    items = [x.strip().lower() for x in string.split(":")]
    return items[1:] if items[0].find("cold truck") > -1 else items

def check_and_load_index():
    """ checks if index exits and loads the data accordingly """
    if not safe_check_index('sfdata'):
        print("Index not found...")
        load_data_in_es()

###########
### APP ###
###########
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/debug')
def test_es():
    resp = {}
    try:
        msg = es.cat.indices()
        resp["msg"] = msg
        resp["status"] = "success"
    except:
        resp["status"] = "failure"
        resp["msg"] = "Unable to reach ES"
    return jsonify(resp)

@app.route('/search')
def search():
    key = request.args.get('q')
    if not key:
        return jsonify({
            "status": "failure",
            "msg": "Please provide a query"
        })
    try:
        res = es.search(
                index="sfdata",
                body={
                    "query": {"match": {"fooditems": key}},
                    "size": 750 # max document size
              })
    except Exception as e:
        return jsonify({
            "status": "failure",
            "msg": "error in reaching elasticsearch"
        })

    hits = res["hits"]["hits"].__len__()

    return jsonify({
        "SearchTerm": key,
        "hits": hits
    })

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("DEBUG", False)
    check_and_load_index()
    app.run(host='0.0.0.0', port=5000, debug=ENVIRONMENT_DEBUG)
