import sys
sys.path.append('model_collab')
sys.path.append('model_lda')
sys.path.append('data')

import os
from flask import Flask, request, jsonify, render_template, \
    abort, redirect, session, url_for
from flask_oauthlib.client import OAuth
import pymongo
import numpy as np
import json
import _pickle as pickle

from load_acts import load_cleaned_acts
from tokenize_acts import ActTokenizer
from lda_model import TopicModelActRecommender
from collaborative_model import CollaborativeActRecommender
from collaborative_model_build import get_loves


app = Flask(__name__)
app.config['GOOGLE_ID'] = os.environ['GOOGLE_ID']
app.config['GOOGLE_SECRET'] = os.environ['GOOGLE_SECRET']
app.debug = True
app.secret_key = os.environ['WEBAPP_SECRET_KEY']

oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=app.config.get('GOOGLE_ID'),
    consumer_secret=app.config.get('GOOGLE_SECRET'),
    request_token_params={
        'scope': 'email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

collection = None

with open('model_lda/model.pkl', 'rb') as file:
    lda_model = pickle.load(file)
collab_model = CollaborativeActRecommender(neighborhood_size=100)
loves = get_loves()
collab_model.fit(loves)

tokenizer = ActTokenizer()

acts = load_cleaned_acts()

def get_user_likes(googleID):
    doc = collection.find_one({'googleID': googleID})
    if doc is None:
        return []
    act_data = [get_act_data(projectID) for projectID in doc['likes']]
    act_data = [json.loads(act.to_json()) for act in act_data if act is not None]
    return act_data

def update_user_likes(googleID, likes):
    collection.find_one_and_replace(
        filter={'googleID': googleID},
        replacement={'googleID': googleID, 'likes': likes},
        upsert=True
    )

def get_act_data(projectID):
    act = acts[acts['projectID'] == projectID]
    if act.shape[0] != 1:
        return None
    act = act.iloc[0]
    return act

def recommend_collab(user_id, act_id, description=None):
    act_index = collab_model.act_id_to_index(act_id)
    if act_index == -1 and bool(description):
        # act is unknown to collaborative model. Try to find an act that has
        # similar text content that is known, and use that one instead.
        print('=============\nGetting similar acts to ' + act_id)
        similar_acts_ids = lda_model.top_recs(
            { 'description': description },
            n=10
        )
        for similar_act_id in similar_acts_ids:
            if collab_model.act_id_to_index(similar_act_id) != -1:
                act_id = similar_act_id
                break
        if act_id == -1:
            abort(400, 'Unknown act and no known similar acts')
            return

    return collab_model.top_recs(user_id, act_id)


def recommend_lda(description):
    return lda_model.top_recs({
        'description': description
    })


@app.route('/recommend/<recommender>', methods=['GET', 'POST'])
def suggest(recommender):
    likes = request.form.get('likes')
    googleID = request.form.get('googleID')
    if bool(likes) and bool(googleID):
        likes = json.loads(likes)
        update_user_likes(googleID, likes)

    if recommender == 'lda':
        description = request.form.get('description')
        if not bool(description):
            abort(400, 'Param "description" is required')
            return
        description = tokenizer.tokenize_act(description)
        act_ids = recommend_lda(description)
    elif recommender == 'collab':
        user_id = request.form.get('userID')
        act_id = request.form.get('projectID')
        description = request.form.get('description')
        act_ids = recommend_collab(user_id, act_id, description)
    elif recommender == 'random':
        act_indices = np.random.randint(0, acts.shape[0], 3)
        act_ids = list(acts.iloc[act_indices]['projectID'].values)
    else:
        return 'Recommender must be "lda", "collab", or "random"'
    return jsonify(act_ids)


@app.route('/act/<projectID>', methods=['GET'])
def get_act(projectID):
    act_json = get_act_data(projectID)
    if act_json is None:
        return 'act not found'
    return act_json.to_json()

@app.route('/', methods=['GET'])
def index():
    user = None
    if 'google_token' in session:
        user = google.get('userinfo').data
        if user and user.get('id'):
            likes = get_user_likes(user.get('id'))
            user['likes'] = likes
        else:
            user = None
    return render_template('index.html', user=json.dumps(user))

@app.route('/login', methods=['GET'])
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect('/')

@app.route('/login/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    return redirect('/')

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

if __name__ == '__main__':
    mongo_client = pymongo.MongoClient()
    db = mongo_client.mydb2
    collection = db.likes
    app.run(host='0.0.0.0', port=3000, debug=True)
    # app.run(host='0.0.0.0', port=8105, threaded=True)
