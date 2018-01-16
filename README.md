
# Billion Acts Suggests

*David Keeling*

## Context

1 Billion Acts of Peace is a web app by the PeaceJam Foundation that collects large and small "acts of peace" from people and organizations around the world, connecting and inspiring people to work together toward world peace. Each act belongs to 1 or more 10 focus areas, social issues critical to achieving world peace as selected by PeaceJam's board of Nobel Peace Laureates.

## Problem Statement

There are several ways of exploring Billion Acts content:

- full text search
- browsing acts by proximity to a location
- browsing act by recently created acts
- browsing acts by focus area

This project concentrates on the last method. Browsing by focus area pulls up any and all acts of peace that were tagged with that focus area, which is the expected behavior but leaves something to be desired -- acts tagged with many focus areas (correctly or erroneously) often appear above more relevant content, and some acts are not tagged accurately (typically because they were logged from web APIs or content dumps and were bulk-tagged with focus areas because the focus area tags are idiosyncratic to Billion Acts). Billion Acts Suggests aims to address these issues and show content more intelligently by modeling the text content of the acts and matching them to text analyses of the focus areas themselves.

## Technical Details

First, <a href="https://spacy.io/">spaCy</a> converts the text content to lemmas, which are fed to Scikit-learn to create a <a href="http://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html">term frequency-inverse document frequency</a> matrix and perform topic analysis with <a href="http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.LatentDirichletAllocation.html">latent Dirichlet allocation</a>. This trained pipeline then converts text descriptions of the focus areas into the same space. A selection of focus areas therefore represents a point in the same dimensional space as the acts of peace, and recommendations can be created by finding acts close to that point.
