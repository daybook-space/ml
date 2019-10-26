import argparse

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

from scipy.special import expit

from .generic_words import DISALLOWED_WORDS

##########################
##    IMPLEMENTATION    ##
##########################

# Some constants to help with entity filtering
EVENT_TYPE = enums.Entity.Type.EVENT
PERSON_TYPE = enums.Entity.Type.PERSON
LOCATION_TYPE = enums.Entity.Type.LOCATION
OTHER_TYPE = enums.Entity.Type.OTHER

ALLOWABLE_LABELS = [enums.DependencyEdge.Label.DOBJ,
                    #enums.DependencyEdge.Label.NSUBJ,
                    #enums.DependencyEdge.Label.NSUBJPASS,
                    enums.DependencyEdge.Label.IOBJ,
                    enums.DependencyEdge.Label.POBJ]

# Calculates single metric from sentiment from score and magnitude
# Uses sigmoid function to push scores to either 1 or -1
# @requires -1 <= score and score <= 1
def sm_fun(score, magnitude):
    return (expit(score * 10) - 0.5) * 2 * magnitude

# Splits list of items into items with no intersections between names
# @requires input to be a list of items of form (name, score, magnitude)
# @ensures all pairwise word intersections will be empty set
def collapse_items(items):
    done = [False] * len(items)
    new_items = []

    for i, item in enumerate(items):
        if done[i]:
            continue
        done[i] = True
        cnt = 1
        name = set(item[0].split(" "))
        sum_1 = item[1]
        sum_2 = item[2]

        for j, i2 in enumerate(items):
            if done[j]:
                continue

            ns = set(i2[0].split(" "))
            if name & ns:
                done[j] = True
                sum_1 += i2[1]
                sum_2 += i2[2]
                cnt += 1

        new_items.append((item[0], sum_1 / cnt, sum_2))

    return new_items

# Process entities from initial Google NLP analysis
def process_entities(annotations, syntax):
    events = []
    people = []
    locations = []
    other = []

    offset_label_map = {tok.text.begin_offset: tok.dependency_edge.label for tok in syntax.tokens}

    for keyword in annotations.entities:
        word_type = keyword.type
        entity_obj = (keyword.name, keyword.sentiment.score, keyword.sentiment.magnitude)
        if keyword.name in DISALLOWED_WORDS:
            continue

        if keyword.type == EVENT_TYPE:
            events.append(entity_obj)

        elif keyword.type == PERSON_TYPE:
            people.append(entity_obj)

        elif keyword.type == LOCATION_TYPE:
            locations.append(entity_obj)

        elif keyword.type == OTHER_TYPE:
            allowable = False

            for mention in keyword.mentions:
                content = mention.text.content
                offset = mention.text.begin_offset

                for word in content.split(" "):
                    try:
                        if offset_label_map[offset] in ALLOWABLE_LABELS:
                            allowable = True
                    except:
                        print("Missed word somehow")
                    offset += (len(word) + 1)

            if allowable:
                other.append(entity_obj)

    events = collapse_items(events)
    people = collapse_items(people)
    locations = collapse_items(locations)
    other = collapse_items(other)

    events.sort(key=lambda x: -sm_fun(x[1], x[2]))
    people.sort(key=lambda x: -sm_fun(x[1], x[2]))
    locations.sort(key=lambda x: -sm_fun(x[1], x[2]))
    other.sort(key=lambda x: -sm_fun(x[1], x[2]))

    return (events, people, locations, other)

# Analyzes journal for entity sentiment and overall sentiment
# Returns tuple of (doc_sentiment, entity_dict)
# entity_dict == {'events': ___, 'people': ___, 'locations': ___, 'other': ___}
def analyze_journal(journal_content):
    client = language.LanguageServiceClient()

    document = types.Document(
        content=journal_content,
        type=enums.Document.Type.PLAIN_TEXT)

    annotations = client.analyze_entity_sentiment(document=document,
                                                  encoding_type="UTF8")
    syntax = client.analyze_syntax(document=document, encoding_type="UTF8")
    sentiment = client.analyze_sentiment(document=document,
                                         encoding_type="UTF8")

    events, people, locations, other = process_entities(annotations, syntax)

    sent = sentiment.document_sentiment
    doc_sentiment = sm_fun(sent.score, sent.magnitude)

    entity_dict = {
        'events': events,
        'people': people,
        'locations': locations,
        'other': other
    }

    return (doc_sentiment, entity_dict)
