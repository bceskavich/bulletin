import json
import requests

def trove_channel_search(devkey, story_url):
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
def trove_query(devkey, channels):
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
            # Populates list with info on each related story found
            related_stories.append({
                'story_title':items[i]['displayName'],
                'story_source':items[i]['source']['displayName'],
                'story_url':items[i]['url']
                })
            # Figures out prevalance of channels among the related stories,
            # but only if there are related channels present.
            # Sorts by ID for later usage in requery
            if 'relatedChannels' in items[i].keys():
                for channel in items[i]['relatedChannels']:
                    if channel['id'] not in common_channels.keys():
                        common_channels[channel['id']] = {'name':channel['displayName'],'frequency':1}
                    else:
                        common_channels[channel['id']]['frequency'] += 1

    return related_stories, common_channels

# Returns top three most common channels based on value frequency
def top_channels(channels):
    top_channels = {}
    tuples = channels.items()
    sorted_channels = sorted(tuples, key = lambda tuples: tuples[1]['frequency'], reverse=True)
    # Creates dictionary to match format of trove_query()
    for i in sorted_channels[:3]:
        top_channels[i[0]] = {'name':i[1]['name']}

    return top_channels

if __name__ == '__main__':
    developer_key = 'EE272629-4004-4A46-B003-4992DF29BFEE'

    url = 'http://qz.com/190379/us-fishermen-throw-back-20-of-their-catch-often-after-the-fish-are-already-injured-or-dead/'

    channels = trove_channel_search(developer_key, url)
    related_stories, common_channels = trove_query(developer_key, channels)

    # Requeries based on top channels
    top = top_channels(common_channels)
    related_stories = trove_query(developer_key, top)[0]
    print str(len(related_stories)) + ' stories found related to top three tags!'
    print json.dumps(related_stories, indent=1)
