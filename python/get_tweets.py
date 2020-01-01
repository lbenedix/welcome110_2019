# coding=utf-8
from twython import Twython
from difflib import get_close_matches
from collections import OrderedDict
import json
from datetime import timedelta

from dateutil.parser import *

APP_KEY = '***'
APP_SECRET = '***'
twitter = Twython(APP_KEY, APP_SECRET)
auth = twitter.get_authentication_tokens()
OAUTH_TOKEN = auth['oauth_token']
OAUTH_TOKEN_SECRET = auth['oauth_token_secret']

bezirke = ['CharlottenburgNord', 'Malchow', 'Altglienicke', 'Adlershof', 'Dahlem', 'Tiergarten', 'Hansaviertel',
           'FalkenhagenerFeld', 'Wilhelmstadt', 'Rahnsdorf', 'Tegel', 'Rosenthal', 'Britz', 'AltTreptow',
           'Charlottenburg', 'Heiligensee', 'Mitte', 'Buckow', 'Kreuzberg', 'Zehlendorf', 'Gesundbrunnen', 'Wannsee',
           'Nikolassee', 'Luebars', 'Haselhorst', 'Koepenick', 'Buckow2', 'Baumschulenweg', 'Wedding', 'Gruenau',
           'Blankenburg', 'Lichtenberg', 'Karlshorst', 'PrenzlauerBerg', 'Pankow', 'Bohnsdorf', 'Hermsdorf', 'Lankwitz',
           'Wartenberg', 'Plaenterwald', 'Neukoelln', 'Wilmersdorf', 'Moabit', 'Hakenfelde', 'Rudow', 'Marienfelde',
           'Wittenau', 'Reinickendorf', 'Kladow', 'Grunewald', 'Niederschoeneweide', 'Karow', 'Friedrichshain',
           'FranzoesischBuchholz', 'Frohnau', 'Mueggelheim', 'Niederschoenhausen', 'Oberschoeneweide', 'Lichterfelde',
           'Mariendorf', 'Wilhelmsruh', 'Konradshoehe', 'Biesdorf', 'Rummelsburg', 'Lichtenrade', 'Westend',
           'Waidmannslust', 'Halensee', 'Friedrichshagen', 'Buch', 'MaerkischesViertel', 'Falkenberg', 'Fennpfuhl',
           'Gropiusstadt', 'Tempelhof', 'NeuHohenschoenhausen', 'Blankenfelde', 'Johannisthal', 'Friedenau',
           'Heinersdorf', 'Gatow', 'Mahlsdorf', 'Hellersdorf', 'Kaulsdorf', 'Marzahn', 'Friedrichsfelde',
           'AltHohenschoenhausen', 'Weissensee', 'Steglitz', 'Spandau', 'Staaken', 'Schmoeckwitz', 'Schoeneberg',
           'Schmargendorf', 'Siemensstadt']

known_locations = {
    'ostbahnhof': 'Friedrichshain',
    'görli': 'Kreuzberg',
    'monbijoupark': 'Mitte',
    'saatwinklerdamm': 'Charlottenburg Nord',
    'olympiastadion': 'Westend',
    'kudamm': 'Charlottenburg',
    'fhain': 'Friedrichshain',
    'fehrbellinerpatz': 'Wilmersdorf',
    'ubhfkleistpark': 'Schöneberg',
    'savignyplatz': 'Charlottenburg',
    'hermannplatz': 'Neukölln',
    'schlachtensee': 'Zehlendorf',
    'sachsendamm': 'Schöneberg',
    'oberbaumbruecke': 'Kreuzberg',
    'oberbaumbrücke': 'Kreuzberg',
    'kotti': 'Kreuzberg',
    'ostkreuz': 'Friedrichshain',
    'alex': 'Mitte',
    'kulturbrauerei': 'Prenzlauer Berg',
    'xberg': 'Kreuzberg',
    'alexanderplatz': 'Mitte',
    'messedamm': 'Westend',
    'humboldthain': 'Gesundbrunnen',
    'pberg': 'Prenzlauer Berg',
    'prenzelberg': 'Prenzlauer Berg',
}

tweets = list()
all_hashtags = dict()
all_bezirke = dict()
done_ids = list()


for p in range(35):
    results = twitter.get_user_timeline(screen_name='polizeiberlin', count=100, include_rts=True, page=p, exclude_replies=False)

    if len(results) == 0: break

    for tweet in results:
        hash_tags = list()
        for h in tweet['entities']['hashtags']:
            hash_tags.append(h['text'])

        if 'welcome110' in hash_tags:  # and not tweet['in_reply_to_screen_name']:

            t = OrderedDict()
            t['bezirk'] = ''
            t['text'] = tweet['text']
            t['hashtags'] = hash_tags
            dt = parse(tweet['created_at']) + timedelta(hours=2)
            t['time'] = dt.strftime('%Y%m%d%H%M%S')
            t['id'] = tweet['id']
            t['url'] = 'https://twitter.com/{}/status/{}'.format('polizeiberlin', tweet['id'])
            if int(t['time'][:4]) < 2019:
                continue

            for h in hash_tags:

                if not h in ['24hPolizei', ]:
                    # known locations with missing hashtag
                    if h.lower() in known_locations:
                        h = known_locations[h.lower()]
                    b = get_close_matches(h, bezirke, n=1)

                    if len(b) == 1:
                        t['bezirk'] = b[0]
                        if b[0] in all_bezirke:
                            all_bezirke[b[0]] += 1
                        else:
                            all_bezirke[b[0]] = 1

                if h in all_hashtags:
                    all_hashtags[h] += 1
                else:
                    all_hashtags[h] = 1

            if t['id'] not in done_ids:
                tweets.append(t)
                done_ids.append(t['id'])
                t['hashtags'] = ';'.join(t['hashtags'])
                # else:
                #     print('duplicate:', t)
    print(p, len(tweets))

print(len(tweets))
json.dump(
    tweets,
    open('welcome110.json', 'w', encoding='utf8'),
    indent=2,
    ensure_ascii=False,
    sort_keys=False
)

# print(json.dumps(all_hashtags, indent=2, sort_keys=True))
