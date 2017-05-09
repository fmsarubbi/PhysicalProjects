import urllib2
import json

def get_dole_whip_facebook_data():
    page_id = "912537128798380" # username or id
    access_token = "221133108379544|-WfTq25JN4GOJb8PIlo4i9JdSKY"  # Access Token
    api_endpoint = "https://graph.facebook.com/v2.9/"
    fb_graph_url = api_endpoint+page_id+"?fields=id,fan_count,posts.limit(1){created_time,story,id,likes.limit(0).summary(true)},photos.limit(1){created_time,likes.limit(0).summary(true)}&access_token="+access_token


    try:
        api_request = urllib2.Request(fb_graph_url)
        api_response = urllib2.urlopen(api_request)

        try:
            return json.loads(api_response.read())
        except (ValueError, KeyError, TypeError):
            return "JSON error"

    except IOError, e:
        if hasattr(e, 'code'):
            return e.code
        elif hasattr(e, 'reason'):
            return e.reason
def collect_dole_whip_info(raw_info):
    dole_whip_info = {}
    dole_whip_info['favorites'] = raw_info['fan_count']
    
    dole_whip_info['last_post_time'] = raw_info['posts']['data'][0]['created_time']
    dole_whip_info['last_post_likes'] = raw_info['posts']['data'][0]['likes']['summary']['total_count']
    dole_whip_info['last_photo_time'] = raw_info['photos']['data'][0]['created_time']
    dole_whip_info['last_photo_likes'] = raw_info['photos']['data'][0]['likes']['summary']['total_count']
    return dole_whip_info

def main():
    # display some lines
    print "in Main!!!"
    raw_info = get_dole_whip_facebook_data()
    print raw_info
    dole_whip_info = collect_dole_whip_info(raw_info)
    print dole_whip_info

    

if __name__ == "__main__": main()
