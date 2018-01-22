
# Billion Acts Suggests

*David Keeling*

## Context

1 Billion Acts of Peace is a web app by the PeaceJam Foundation that collects large and small "acts of peace" from people and organizations around the world, connecting and inspiring people to work together toward world peace. Each act belongs to 1 or more of the 10 focus areas -- social issues critical to achieving world peace as selected by PeaceJam's board of Nobel Peace Laureates.

## Problem Statement

Billion Acts Suggests uses machine learning to improve the "More acts like this" recommendations that appear at the bottom of each act of peace page. The status quo method to find these suggestions is to select one of the current act's focus areas at random and pull up acts tagged with that focus area in whatever order the datastore query returns them. This tends to give results that are only tenuously connected to the current act, and even worse, creates infinite loops where the user keeps seeing the same suggestions. Two strategies are employed to improve on this:

1. **Topic modeling** on the text content of the acts.
2. **Collaborative filtering**, if a known user is signed in.

## Technical Details

#### Topic modeling

First, <a href="https://spacy.io/">spaCy</a> converts the text content to lemmas, which are fed to Scikit-learn to create a <a href="http://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html">term frequency</a> matrix and perform topic analysis with <a href="http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.LatentDirichletAllocation.html">latent Dirichlet allocation</a>. To find similar acts, the text content of an act is passed to these trained models and transformed into the same vector space, and <a href="http://scikit-learn.org/stable/modules/generated/sklearn.neighbors.NearestNeighbors.html#sklearn.neighbors.NearestNeighbors">neighbors</a> are found with cosine similarity as the distance metric.

#### Collaborative Filtering

Billion Acts does not support user ratings of acts of peace, so the collaborative model uses a binary system of measuring a user's interests. The data for each user consists of acts of peace they "loved" or created. Act similarities are calculated using Jaccard set similarity, meaning acts rated by the same users will have a high similarity score, and if another user has rated one but not another of those acts, the unrated act is likely to appear as a recommendation.

In context, each prediction request to this model will include the act currently being viewed, so to bolster the recommendations and make them more contextually relevant, it is assumed that the user is interested in that act. The model is trained on the fly with this added data, which is possible because the training time for the model is very short. This allows for better recommendations in the case where the user has rated few or no acts but the current act has been rated by other users. As the data scales up, this per-request model training will become too costly, but at that point there will be enough data that the added data point will make less of a difference. However, a pre-trained model will need a new strategy to address the cold-start problem, and will also need a strategy to contextualize each request and avoid a closed loop of recommendations.

## History

The first iteration of this project attempted to improve the experience of browsing acts of peace by focus area. This method of browsing pulls up any and all acts of peace that were tagged with that focus area, which is the expected behavior but leaves something to be desired -- acts tagged with many focus areas, correctly or erroneously, often appear above more relevant content, and some acts are not tagged accurately, typically because they were logged from web APIs or content dumps and were bulk-tagged because the focus area tags are idiosyncratic to Billion Acts. The goal was to address these issues and show content more intelligently by modeling the text content of the acts and matching them to text analyses of the focus areas themselves. However, the latent topics found by the algorithm did not match well with the focus area tags. That is, the acts were grouped by features like their vocabulary (e.g., created by grade-school children) or setting (e.g., school vs. NGO) rather than their underlying social issues, which were not always featured prominently in the text.

## Motivation

Before enrolling in Galvanize's Data Science Immersive, I worked for several years as lead developer on the 1 Billion Acts of Peace project. Searching and browsing on the site often caused some frustration for me as I tried to stay abreast of the content our users were creating, so I wanted to use my new skills to make one more contribution to Billion Acts. BASuggests is meant to make the browsing experience more fun and useful, and is designed to scale well as the user base grows.
