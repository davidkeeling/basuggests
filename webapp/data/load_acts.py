import pandas as pd
import numpy as np
import pickle
import re

def load_tokenized_acts(sample=0, filename='data/tokenized_acts.pkl', use_pickle=True):
    if use_pickle:
        try:
            with open(filename, 'rb') as file:
                acts = pickle.load(file)
                print('read tokenized acts from pickle')
                return acts
        except:
            print('tokenizing acts...')

    acts = load_cleaned_acts()
    if sample > 0:
        acts = acts.sample(sample)
    acts = acts['text']

    from data.tokenize_acts import ActTokenizer
    tokenizer = ActTokenizer()
    acts = tokenizer.tokenize_acts(acts)
    with open(filename, 'wb') as file:
        pickle.dump(acts, file)
    return acts

def load_cleaned_acts(filename='data/cleaned_acts.pkl', use_pickle=True):
    if use_pickle:
        try:
            with open(filename, 'rb') as file:
                acts = pickle.load(file)
                print('read cleaned acts from pickle')
                return acts
        except:
            print('loading acts from csv...')

    acts = pd.read_csv('data/dl_acts.csv')
    acts = clean_acts(acts)
    with open(filename, 'wb') as file:
        pickle.dump(acts, file)
    return acts

def get_flag_expr(content_flags, fieldname):
    """
    Construct regex string to identify acts that match the content flags
    """
    values = content_flags[content_flags['field'] == fieldname]['value']
    escaped_flags = [re.escape(m) for m in values]
    return '|'.join(escaped_flags)

def clean_acts(acts):
    """
    Removes certain acts from training set, performs date parsing, and
    concatenates text fields.
    """

    # Drop autogenerated acts that don't have individual content -- these
    # acts' text content is nearly identical for all instances, so they
    # don't add anything useful to the model. Flags to identify these acts
    # are stored separately in a git-ignored CSV to anonymize them.
    flags = pd.read_csv('data/content_flags.csv')
    title_flags = get_flag_expr(flags, 'name')
    description_flags = get_flag_expr(flags, 'description')
    acts.drop(
        labels=np.where(
            (acts['description'].str.contains(description_flags)) |
            (acts['name'].str.contains(title_flags))
        )[0],
        inplace=True
    )

    # Other autologged acts do have individual text content but also have
    # generic paragraph titles added to them. Strip these out:
    for structural_flag in flags[flags['field'] == 'structural']['value']:
        acts['description'] = acts['description'].str.replace(structural_flag, '')

    # The field 'focusAreas' is a concatenated list of focus area IDs.
    # Convert to boolean dummy variables with meaningful column names:
    acts['focusAreas'] = acts['focusAreas'].str.replace('10', '0')
    acts['education'] = acts['focusAreas'].str.contains('1')
    acts['environment'] = acts['focusAreas'].str.contains('2')
    acts['poverty'] = acts['focusAreas'].str.contains('3')
    acts['health'] = acts['focusAreas'].str.contains('4')
    acts['weapons'] = acts['focusAreas'].str.contains('5')
    acts['humanrights'] = acts['focusAreas'].str.contains('6')
    acts['endingracism'] = acts['focusAreas'].str.contains('7')
    acts['womenandchildren'] = acts['focusAreas'].str.contains('8')
    acts['water'] = acts['focusAreas'].str.contains('9')
    acts['conflictresolution'] = acts['focusAreas'].str.contains('0')
    del acts['focusAreas']

    acts['created'] = pd.to_datetime(acts['created'], infer_datetime_format=True)

    text_fields = ['name', 'description', 'issues', 'context', 'plan', 'accomplishments', 'callToAction']
    acts.fillna('', inplace=True)
    acts['text'] = acts[text_fields].apply(lambda x: ' '.join(x), axis=1)
    return acts
