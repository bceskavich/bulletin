import json
import requests

def troveChannelSearch(devkey, story_url):
    # API Request URL
    url = 'http://api.washingtonpost.com/trove/v1/items'
    # API params (developer key + story url)
    params = {
        'key':devkey,
        'url':story_url
    }
    # Grab Data
    resp = requests.get(url, params=params)
    encoded = json.loads(resp.content)
    info = encoded['items'][0]
    # If HTTP request not successful
    if encoded['status']['code'] != 200:
        print 'Ah snap, something went wrong!'
        channels = None
    # If Trove Query returns related channel info
    elif 'relatedChannels' in info.keys():
        # Creates & populates dictionary -- {channel_name:channel_id}
        channels = {}
        channels[info['relatedChannels'][0]['id']] = {'name':info['relatedChannels'][0]['displayName']}
    else:
        print 'No related channels found for this story!'
        channels = None
    return channels

# NEED CHANNEL IDs TO PERFORM!
# Channels should be a dictionary list
def troveQuery(devkey, channels, story_search=False, channel_search=True):
    # Initializes content stores
    related_stories = [] # For final related stories
    common_channels = {} # For common channels across queries

    # Iterates thru each given channel
    for channel_id in channels.keys():
        # Constructions URL & requests info based on specific channel ID
        url = 'http://api.washingtonpost.com/trove/v1/channels/' + str(channel_id) + '/result'
        params = {'key':devkey}
        resp = requests.get(url, params=params)
        encoded = json.loads(resp.content)
        items = encoded['result']['items'] # this is the actual content we care about

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
                # Sorts by ID for later usage in requery
                if 'relatedChannels' in items[i].keys():
                    for channel in items[i]['relatedChannels']:
                        if channel['id'] not in common_channels.keys():
                            common_channels[channel['id']] = {'name':channel['displayName'],'frequency':1}
                        else:
                            common_channels[channel['id']]['frequency'] += 1

    if story_search:
        return related_stories
    elif channel_search:
        return common_channels
    else:
        return related_stories, common_channels

# Returns top three most common channels based on value frequency
def topChannel(channels):
    top_channel = {}
    tuples = channels.items()
    sorted_channels = sorted(tuples, key = lambda tuples: tuples[1]['frequency'], reverse=True)
    # Creates dictionary to match format of trove_query()
    for i in sorted_channels[:1]:
        top_channel[i[0]] = {'name':i[1]['name']}

    return top_channel

def searchTimesTags(key, query):
    params = {'query':query, 'api-key':key}
    url = 'http://api.nytimes.com/svc/suggest/v1/timestags'
    resp = requests.get(url, params=params)
    encoded = json.loads(resp.content)

    print json.dumps(encoded[1], indent=1)

# NEED START DATE FROM ORIGINAL POCKET ARTICLE
# Returns 10 by default, can then page thru
def searchTimes(key, query):
    print 'Query Term:', query
    params = {'q':query, 'api-key':key}
    url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json'
    resp = requests.get(url, params=params)
    encoded = json.loads(resp.content)

    return encoded

def searchTimesSemantic(key, query):
    params = {'query':query, 'fields':'all', 'api-key':key}
    url = 'http://api.nytimes.com/svc/semantic/v2/concept/name/nytd_des/United States Defense and Military Forces.json'
    #url = 'http://api.nytimes.com/svc/semantic/v2/concept/search.json'
    resp = requests.get(url, params=params)
    encoded = json.loads(resp.content)
    print json.dumps(encoded, indent=1)

if __name__ == '__main__':
    developer_key = 'EE272629-4004-4A46-B003-4992DF29BFEE'

    url = 'http://www.nytimes.com/2014/03/25/world/asia/malaysia-airlines-flight-370.html?gwh=5B2D80CFE408F6D48FDD2F5698C0C2E0&gwt=regi'

    channels = troveChannelSearch(developer_key, url)
    common_channels = troveQuery(developer_key, channels, channel_search=True)

    print json.dumps(common_channels, indent=1)

    # Requeries based on top channels
    top = topChannel(common_channels)
    print json.dumps(top, indent=1)

    """
    related_stories = troveQuery(developer_key, top, story_search=True)
    print str(len(related_stories)) + ' stories found related to top three tags!'
    print json.dumps(related_stories, indent=1)
    """

    article_search_key = 'b2f1032fbec2cb261c1e153ab6b5a6b8:13:69075429'
    semantic_api_key = 'f00917b36620aa064bf66847bfbd4661:7:69075429'
    tags_search_key = 'e696e34ed4c186684a5466a878cd9682:14:69075429'

    #searchTimesTags(tags_search_key, top.values()[0]['name'])
    nytimes = searchTimes(article_search_key, query=top.values()[0]['name'])
    #searchTimesSemantic(semantic_api_key, query=top.values()[0]['name'])

    print len(nytimes['response']['docs'])
    print json.dumps(nytimes['response']['docs'], indent=1)
