import numpy as np
from scipy import sparse

class CollaborativeActRecommender(object):

    def __init__(self, neighborhood_size):
        self.neighborhood_size = neighborhood_size


    def fit(self, loves):
        """
        Takes a numpy array with column 0 = projectID, 1 = userID.
        """
        self.loves = loves
        ratings, item_sim_mat, neighborhoods, users, acts = \
            self._process_for_fit(loves)
        self.ratings = ratings
        self.users = users
        self.acts = acts
        self.n_users = self.ratings.shape[1]
        self.n_items = self.ratings.shape[0]
        self.item_sims = item_sim_mat
        self.neighborhoods = neighborhoods


    def _process_for_fit(self, loves):
        """
        Returns the objects needed to calculate predicted ratings and find
        the corresponding act IDs
        """
        users = loves['userID'].unique()
        acts = loves['projectID'].unique()
        ratings = self._get_ratings_mat(loves, users, acts)
        item_sims = np.array(jaccard_similarities(ratings.T))
        neighborhoods = self._get_neighborhoods(item_sims)
        return ratings, item_sims, neighborhoods, users, acts


    def _get_ratings_mat(self, loves, users, acts):
        """
        Takes a numpy array with column 0 = projectID, 1 = userID.
        Initializes a sparse matrix where the rows are users and columns
        are acts. For every row in the input array, assigns 1.0 as in the
        corresponding cell of the sparse matrix
        """
        ratings = sparse.lil_matrix((users.shape[0], acts.shape[0]))
        for love in loves.iterrows():
            user_index = np.where(users == love[1]['userID'])[0][0]
            act_index = np.where(acts == love[1]['projectID'])[0][0]
            ratings[user_index-1, act_index-1] = 1.0
        return ratings


    def _get_self_fit(self):
        return self.ratings, self.item_sims, self.neighborhoods, \
            self.users, self.acts


    def _get_fit(self, user_id, act_id):
        """
        For many recommendation requests we use a temporary ratings matrix
        where the act currently being viewed is added as a liked act for the
        user. This bolsters predictions in cases where the act is known but the
        user is either unknown or has very few known ratings.

        Calculating a new ratings matrix on the fly may become unfeasible as
        the dataset grows.
        """
        if not bool(user_id):
            user_id = 'temp'
        num_acts_rated_by_user = 0
        act_index = self.act_id_to_index(act_id)
        user_index = self.user_id_to_index(user_id)
        if act_index == -1:
            if user_index == -1:
                # user and act are both unknown. Can't make any predictions
                return None
            # act is unknown. No use to impute it as a liked act for the user
            # because there will not be any similar acts to it
            return self._get_self_fit()

        loves = None
        if user_index != -1:
            # user is known
            num_acts_rated_by_user = self.ratings[user_index].getnnz()
            if num_acts_rated_by_user > 10:
                # user is known and has rated enough acts to not need to
                # impute the current act as a liked act. This is the standard
                # situation for collaborative filtering, and has the fastest
                # computation time
                return self._get_self_fit()
            # user is known, but only has a few ratings
            loves = self.loves.copy()
        else:
            # user is unknown:
            loves = self.loves.copy()
            user_index = -1
        # Include this act as a liked act temporarily:
        loves = loves.append([{
            'userID': user_id,
            'projectID': act_id
        }])
        return self._process_for_fit(loves)


    def _get_neighborhoods(self, item_sims):
        least_to_most_sim_indexes = np.argsort(item_sims, 1)
        return least_to_most_sim_indexes[:, -self.neighborhood_size:]


    def predict_user(self, user_index, ratings, neighborhoods, item_sims):
        """
        Finds users who have rated acts in common with the given user,
        and for all acts those users have rated that this one has not,
        predicts their rating. Acts for which there isn't sufficient
        information get a rating of -1.
        """
        n_items = ratings.shape[0]
        acts_liked_by_user = ratings[user_index].nonzero()[1]
        out = np.zeros(n_items)
        for item_to_rate in range(n_items):
            relevant_items = np.intersect1d(
                neighborhoods[item_to_rate],
                acts_liked_by_user,
                assume_unique=True
            )
            if len(relevant_items) == 0:
                out[item_to_rate] = -1
                continue
            out[item_to_rate] = ratings[user_index, relevant_items] * \
                item_sims[item_to_rate, relevant_items] / \
                item_sims[item_to_rate, relevant_items].sum()
        out = np.nan_to_num(out)
        return out


    def predict_all_users(self, ratings, neighborhoods, item_sims):
        """
        Predicts all user ratings that are possible to make predictions on.
        """
        all_ratings = [
            self.predict_one_user(user_id, ratings, neighborhoods, item_sims)
            for user_id in range(self.n_users)
        ]
        return np.array(all_ratings)


    def top_recs(self, user_id, act_id, n=3, likes=[]):
        """
        First calls self.predict_user to calculate predicted ratings for all
        acts there is enough information for, then sorts these ratings and
        gets the top n. These indices are used to find the encoded string ids
        of the acts in self.acts.
        """
        fit = \
            self._get_fit(user_id, act_id)
        if fit is None:
            return None
        ratings, item_sims, neighborhoods, users, acts = fit
        user_index = self.user_id_to_index(user_id, users)
        pred_ratings = self.predict_user(user_index, ratings, neighborhoods, \
            item_sims)
        item_index_sorted_by_pred_rating = list(np.argsort(pred_ratings))
        items_rated_by_this_user = ratings[user_index].nonzero()[1]
        unrated_items_by_pred_rating = [
            item for item in item_index_sorted_by_pred_rating
            if item not in items_rated_by_this_user
        ]
        unrated_act_ids = acts[unrated_items_by_pred_rating]
        unrated_act_ids = [act_id for act_id in list(unrated_act_ids) if act_id not in likes]
        return unrated_act_ids[-n:]


    def user_id_to_index(self, user_id, users=None):
        """
        Finds the index of user_id in self.users.
        """
        if user_id is None:
            return -1
        if users is None:
            users = self.users
        user_index = np.where(users == user_id)[0]
        if user_index.shape[0] == 0:
            return -1
        return user_index[0]


    def act_id_to_index(self, act_id, acts=None):
        """
        Finds the index of act_id in self.acts.
        """
        if acts is None:
            acts = self.acts
        act_index = np.where(acts == act_id)[0]
        if act_index.shape[0] == 0:
            return -1
        return act_index[0]



# credit to http://na-o-ys.github.io/:
def jaccard_similarities(mat):
    cols_sum = mat.getnnz(axis=0)
    ab = mat.T * mat
    aa = np.repeat(cols_sum, ab.getnnz(axis=0)) # for rows
    bb = cols_sum[ab.indices] # for columns
    similarities = ab.copy()
    similarities.data /= (aa + bb - ab.data)
    return similarities.todense()
