
# Billion Acts Suggests

*David Keeling*

## Context

1 Billion Acts of Peace is a web app by the PeaceJam Foundation that collects large and small "acts of peace" from people and organizations around the world, connecting and inspiring people to work together toward world peace. Each act belongs to 1 or more of the 10 focus areas -- social issues critical to achieving world peace as selected by PeaceJam's board of Nobel Peace Laureates.

## Problem Statement

There are several ways of exploring Billion Acts content:

- full text search
- browsing acts by proximity to a location
- browsing act by recently created acts
- browsing acts by focus area
- by following "More acts like this" suggestions at the bottom of each act page

This project concentrates on the last method. The status quo method to find these suggestions is to select one of the current act's focus areas at random and pull up acts tagged with that focus area in whatever order the datastore query returns them. This tends to give results that are only tenuously connected to the current act, and even worse, creates infinite loops where the user keeps seeing the same suggestions. Two strategies are employed to improve on this:

1. Topic modeling by the text content of the act.
2. Collaborative filtering, if a known user is signed in.

## Technical Details

#### Topic modeling

First, <a href="https://spacy.io/">spaCy</a> converts the text content to lemmas, which are fed to Scikit-learn to create a <a href="http://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html">term frequency</a> matrix and perform topic analysis with <a href="http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.LatentDirichletAllocation.html">latent Dirichlet allocation</a>. When finding acts similar to the act currently being viewed, the text content of the act is passed to these trained models and transformed into the same vector space, and <a href="http://scikit-learn.org/stable/modules/generated/sklearn.neighbors.NearestNeighbors.html#sklearn.neighbors.NearestNeighbors">neighbors</a> are found with cosine similarity as the distance metric.

#### Collaborative Filtering

Billion Acts does not support user ratings of acts of peace, so the collaborative model uses a binary system of measuring a user's interests. The data for each user consists of acts of peace they "loved" or created. Act similarities are calculated using Jaccard set similarity, meaning acts rated by the same users will have a high similarity score, and if another user has rated one but not another of those acts, the unrated act is likely to appear as a recommendation.

The use case for this model includes an act that is currently being viewed, so to bolster the recommendations and make them more contextually relevant, with each request it is assumed that the user is interested in that current act. The model is trained on the fly with this added data, which is possible because the training time for the model is very short. This allows for better recommendations in the case where user has rated few or no acts but the current act has been rated by other users.

## History

The first iteration of this project attempted to improve the experience of browsing by focus area. This method of browsing pulls up any and all acts of peace that were tagged with that focus area, which is the expected behavior but leaves something to be desired -- acts tagged with many focus areas (correctly or erroneously) often appear above more relevant content, and some acts are not tagged accurately (typically because they were logged from web APIs or content dumps and were bulk-tagged with focus areas because the focus area tags are idiosyncratic to Billion Acts). The goal was to address these issues and show content more intelligently by modeling the text content of the acts and matching them to text analyses of the focus areas themselves. However, the topic modeling algorithm tended to group the acts in ways that did not match with the focus areas, creating groups by the overall vocabulary in the act, or by their context (school vs NGO, for example) rather than the underlying issues, which were not always featured prominently in the acts' text, and so the browsing results were incongruous with the search terms. The top 3 latent topics are visualized below:

<img src="/img/topic1.png" />
<img src="/img/topic2.png" />
<img src="/img/topic3.png" />
