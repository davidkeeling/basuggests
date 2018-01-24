import pandas as pd
import _pickle as pickle

from collaborative_model import CollaborativeActRecommender


def get_loves():
    # Acts that users "loved":
    loves = pd.read_csv('data/dl_loves.csv')
    loves.drop('created', inplace=True, axis=1)

    # Acts that users created:
    acts = pd.read_csv('data/dl_acts.csv')
    acts['userID'] = acts['userID'].fillna('')
    acts = acts[acts['userID'] != ''][['userID', 'projectID']]
    acts = acts.reset_index().drop('index', axis=1)

    # Remove acts created by admin accounts. Most of these were logged in bulk
    # so the admin accounts will have hundreds or thousands of liked acts,
    # muddying the model.
    flags = pd.read_csv('data/content_flags.csv')
    admin_ids = flags[flags['field'] == 'admin_id']['value']
    for admin_id in admin_ids:
        acts = acts[acts['userID'] != admin_id]
    acts = acts[['projectID', 'userID']]

    loves = loves.append(acts)
    return loves

if __name__ == "__main__":
    cf_recommender = CollaborativeActRecommender(neighborhood_size=100)
    loves = get_loves()
    cf_recommender.fit(loves)
    with open('model_collab/model.pkl', 'wb') as file:
        pickle.dump(cf_recommender, file)
