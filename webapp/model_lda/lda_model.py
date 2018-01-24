import numpy as np
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import NearestNeighbors

class TopicModelActRecommender(object):
    def __init__(self):
        self.vectorizer = CountVectorizer(
            ngram_range=(1, 3),
            min_df=2,
            max_df=.95
        )
        self.lda = LatentDirichletAllocation(
            n_components=10,
            learning_method='batch'
        )
        self.neighbors = NearestNeighbors(
            n_neighbors=3,
            radius=1.0,
            metric='cosine'
        )

    def random_suggestion(self, suggestions):
        upper = len(self.projectIDs)
        random_suggestion = np.random.randint(0, upper)
        while random_suggestion in suggestions:
            random_suggestion = np.random.randint(0, upper)
        return self.projectIDs[random_suggestion]

    def top_recs(self, act, n=3, likes=[]):
        description = act['description']
        act_word_counts = self.vectorizer.transform([description])
        modeled_act = self.lda.transform(act_word_counts)
        suggestion_indices = self.neighbors.kneighbors(
            X=modeled_act,
            # fetch enough neighbors that we can remove any that the user has
            # has already liked (param likes) and still return at least n:
            n_neighbors=20,
            return_distance=False
        )
        suggestions = self.projectIDs[suggestion_indices]
        suggestions = [s for s in list(suggestions[0]) if s not in likes]
        return suggestions[:n]

    def fit(self, acts, original_acts):
        self.acts = original_acts
        self.projectIDs = np.array(acts['projectID'])
        act_word_counts = self.vectorizer.fit_transform(acts['text'])
        modeled_acts = self.lda.fit_transform(act_word_counts)
        self.neighbors.fit(modeled_acts)
