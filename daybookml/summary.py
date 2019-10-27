from .analysis import sm_fun, collapse_items

def top_emotion_effectors(journal_sentiments):
    events = journal_sentiments['events']
    people = journal_sentiments['people']
    locations = journal_sentiments['locations']
    other = journal_sentiments['other']

    events = collapse_items(events)
    people = collapse_items(people)
    locations = collapse_items(locations)
    other = collapse_items(other)

    events.sort(key=lambda x: -sm_fun(x[1], x[2]))
    people.sort(key=lambda x: -sm_fun(x[1], x[2]))
    locations.sort(key=lambda x: -sm_fun(x[1], x[2]))
    other.sort(key=lambda x: -sm_fun(x[1], x[2]))

    event_sm = [(i[0], sm_fun(i[1], i[2])) for i in events]
    people_sm = [(i[0], sm_fun(i[1], i[2])) for i in people]
    locations_sm = [(i[0], sm_fun(i[1], i[2])) for i in locations]
    other_sm = [(i[0], sm_fun(i[1], i[2])) for i in other]

    return {
        'events': event_sm,
        'people': people_sm,
        'locations': locations_sm,
        'other': other_sm
    }

def is_suicidal(journal_sentiments):
    other = []

    for journal in journal_sentiments:
        other.extend(journal['other'])

    other = collapse_items(other)

    for word in other:
        if word[0] == 'life':
            sm_score = sm_fun(word[1], word[2])
            return sm_score < -2

    return False
