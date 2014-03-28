import json
import requests

def troveChannelSearch(key, story_url):
    # TroveAPI URL
    url = 'http://api.washingtonpost.com/trove/v1/items'
    params = {'url':story_url, 'key':key}

    # Query Trove
    response = requests.get(url, params=params)
    encoded = json.loads(response.content)
    print json.dumps(encoded, indent=1)
    """
    data = encoded['items'][0] # Actual response data

    # Code 200 is the only response we're interested in
    if encoded['status']['code'] != 200:
        print 'Ah snap, something went wrong!'
        channels = None
    # Populates channel dictionary based on app-wide convention:
    # { [name]: { source: (Trove/NYT), name: (tag/channel name), (frequency:
    # int), (id: TroveID), (type: NYT tag type) }
    elif 'relatedChannels' in encoded['items'][0].keys():
        channels = {}
        for item in data['relatedChannels']:
            channels[item['displayName']] = {'source':'Trove', 'id':item['id']}
    else:
        print 'No related channels found for this story!'
        channels = None

    return channels
    """

def troveQuery(key, channels, story_search=False, channel_search=False):
    related_stories = [] # For final related stories
    common_channels = {} # For common channels across queries

    channel_ids = [item['id'] for item in channels.values()]

    # Iterates thru each given channel
    for cid in channel_ids:
        # Constructions URL & requests info based on specific channel ID
        url = 'http://api.washingtonpost.com/trove/v1/channels/' + str(cid) + '/result'
        params = {'key':key}
        resp = requests.get(url, params=params)
        encoded = json.loads(resp.content)
        items = encoded['result']['items'] # Content we care about

        # Iterates thru response content
        for i in range(len(items)):
            if story_search:
                # Populates list with info on each related story found
                related_stories.append({
                    'story_title':items[i]['displayName'],
                    'story_source':items[i]['source']['displayName'],
                    'story_url':items[i]['url']
                    })
            if channel_search:
                # Figures out prevalance of channels among the related stories,
                # but only if there are related channels present.
                if 'relatedChannels' in items[i].keys():
                    for channel in items[i]['relatedChannels']:
                        if channel['displayName'] not in common_channels.keys():
                            common_channels[channel['displayName']] = {'source':'Trove', 'id':channel['id'], 'frequency':1}
                        else:
                            common_channels[channel['displayName']]['frequency'] += 1

    if story_search:
        return related_stories
    elif channel_search:
        return common_channels

# Returns top three most common channels based on value frequency
def topChannels(channels):
    # Initiates top channels dictionary
    top_channels = {}

    # Sorts thru & orders channel by frequency
    # Could be useful for other parts of the app, but not used currently
    tuples = channels.items()
    sorted_channels = sorted(tuples, key = lambda tuples: tuples[1]['frequency'], reverse=True)

    # Finds Top Channel(s) (multiple if tied)
    max_frequency = sorted_channels[0][1]['frequency']
    for item in sorted_channels:
        if item[1]['frequency'] == max_frequency:
            top_channels[item[0]] = {'source':'Trove', 'id':item[1]['id'], 'frequency':item[1]['frequency']}

    return top_channels

# NEEDS START DATE FROM POCKET STORY
def searchTimesArticles(key, channels, story_search=False, tag_search=False):
    related_stories = [] # For final related stories
    common_tags = {} # For common channels across queries

    # Grabs all query names from Trove channel input, assumes could be multiple
    queries = [name for name in channels.keys()]
    url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json'

    for q in queries:
        # Makes a request and loads in actual information
        params = {'q':q, 'api-key':key}
        response = requests.get(url, params=params)
        encoded = json.loads(response.content)
        items = encoded['response']['docs']

        # Populates related stories array if method called for that purpose
        if story_search:
            for item in items:
                related_stories.append({
                    'story_title':item['headline']['main'],
                    'story_source':'New York Times',
                    'story_url':item['web_url']
                    })

        # Populates tag frequency dictionary if method called for that purpose
        if tag_search:
            for item in items:
                for tag in item['keywords']:
                    if tag['value'] not in common_tags.keys():
                        common_tags[tag['value']] = {'source':'NY Times','type':tag['name'], 'frequency':1}
                    else:
                        common_tags[tag['value']]['frequency'] += 1

    if story_search:
        return related_stories
    elif tag_search:
        return common_tags

# Simply combines related searches from Trove & NY Times
def combineRelatedStories(related_trove_stories, related_times_stories):
    related_stories = related_trove_stories + related_times_stories
    return related_stories

# Simply combines tag dictionaries from Trove ('channels') &
# NY Times (sometimes called 'keywords')
def combineTopTags(common_trove_channels, common_times_tags):
    all_common_tags = dict(common_trove_channels.items() + common_times_tags.items())
    return all_common_tags

if __name__ == '__main__':
    trove_key = 'E767C55D-0941-4993-BB3A-1CB81FD2B9E9'
    article_search_key = 'b2f1032fbec2cb261c1e153ab6b5a6b8:13:69075429'

    example_url = 'http://www.publicintegrity.org/2014/03/21/14433/wireless-companies-fight-their-futures'

    # Gets original channel & finds common channels
    troveChannelSearch(trove_key, example_url)
    """
    common_channels = troveQuery(trove_key, channels, channel_search=True)

    # Finds related stories based upon top channel(s) (multiple if tied)
    top_channels = topChannels(common_channels)
    related_trove_stories = troveQuery(trove_key, top_channels, story_search=True)

    # Finds common tags & stories based upon Trove grunt work
    common_tags = searchTimesArticles(article_search_key, top_channels, tag_search=True)
    related_times_stories = searchTimesArticles(article_search_key, top_channels, story_search=True)

    # COMBINES
    all_tags = combineTopTags(common_channels, common_tags)
    print 'Total Topics:', str(len(all_tags.keys()))

    related_stories = combineRelatedStories(related_trove_stories, related_times_stories)
    print 'Total Related Stories:', str(len(related_stories))
    print '------'
    print json.dumps(related_stories, indent=1)
    """








