
import pandas as pd
import _pickle as pickle

from lda_model import TopicModelActRecommender
from data.load_acts import load_tokenized_acts, load_cleaned_acts

if __name__ == '__main__':
    tokenized_acts = load_tokenized_acts()
    cleaned_acts = load_cleaned_acts()
    acts = pd.DataFrame({
        'text': tokenized_acts,
        'projectID': cleaned_acts['projectID']
    })
    acts = acts[acts['text'] != '']

    lda_model = TopicModelActRecommender()
    lda_model.fit(acts, cleaned_acts)
    with open('model_lda/model.pkl', 'wb') as file:
        pickle.dump(lda_model, file)
