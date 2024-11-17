try:
    import feedparser
except:
    import feedparser2.feedparser as feedparser

import re
# 指定 RSS feed 的 URL
feed_url = 'https://forum.monika.love/rss/d/3954'

# 解析 RSS feed
#feed = feedparser.parse(feed_url)

#print(f"{feed.entries}")

def set_ua(ver):
    feedparser.USER_AGENT = "MAICA_Blessland/{}".format(ver)    
html_tag_re = re.compile(r'<[^>]+>')

def remove_html_tags(text):
    return html_tag_re.sub('', text)
def get_log():
    global feedparser
    import traceback
    data = {
        "title": "",
        "content": [],
        "ver":0
    }
    try:
        feed = feedparser.parse(feed_url)
        for item in feed.entries:
            data["title"] = item['title']
            data["content"].append(remove_html_tags(item['summary']))
            data["ver"] = int(item['link'].split('/')[-1])
        
        return data
    except Exception as e: 
        data["title"] = "An Exception is occurred"
        data["content"].append(traceback.format_exc())
        data["ver"] = 0
    return data 



    
