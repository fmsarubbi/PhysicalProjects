#!/usr/bin/python

import argparse
import sys
import time
import datetime
import logging

from Adafruit_LED_Backpack import SevenSegment

parser = argparse.ArgumentParser(
    description='The code to run the clock.'
)
parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")

args = parser.parse_args()
if args.verbose:
    logging.basicConfig(level=logging.DEBUG)


# ===========================================================================
# Clock Example
# ===========================================================================

segment = SevenSegment.SevenSegment(address=0x70)
# Initialize the display. Must be called once before using the display.
segment.begin()

print "Press CTRL+C to exit"

errorCnt = 0
lastUpdate = time.time()-100
dole_whip_info = {}


def updateTime(now):
  hour = now.hour if now.hour <= 12 else now.hour - 12 
  hour = now.hour if now.hour > 0 else 12 
  minute = now.minute
  second = now.second

  segment.clear()
  # Set hours

  if hour >= 10 :
    segment.set_digit(0, int(hour / 10) )     # Tens
  segment.set_digit(1, hour % 10)          # Ones
  # Set minutes
  segment.set_digit(2, int(minute / 10))   # Tens
  segment.set_digit(3, minute % 10)        # Ones
  # Toggle colon
  segment.set_colon(second % 2)              # Toggle colon at 1Hz
  logging.info('Writing time %s:%s ' % {hour,minute})
  writeDisplay()

def writeDisplay():
  # Write the display buffer to the hardware.  This must be called to
  # update the actual display LEDs.
  try:
    segment.write_display()
    # Wait a quarter second (less than 1 second to prevent colon blinking getting$
    time.sleep(0.25)
  except (KeyboardInterrupt, SystemExit):
    raise
  except: # catch *all* exceptions
    e = sys.exc_info()
    errorCnt+=1
    print "%s Error %d: %s" % (now, errorCnt, e) 

def get_dole_whip_facebook_data():
  logging.info('Getting Facebook Info')
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

def collect_dole_whip_info():
  raw_info = get_dole_whip_facebook_data()
  dole_whip_info = {}
  dole_whip_info['favorites'] = raw_info['fan_count']
  
  dole_whip_info['last_post_time'] = raw_info['posts']['data'][0]['created_time']
  dole_whip_info['last_post_likes'] = raw_info['posts']['data'][0]['likes']['summary']['total_count']
  dole_whip_info['last_photo_time'] = raw_info['photos']['data'][0]['created_time']
  dole_whip_info['last_photo_likes'] = raw_info['photos']['data'][0]['likes']['summary']['total_count']
  
  logging.info(dole_whip_info)
  return dole_whip_info


def updatePost(now):
  segment.clear()
  
  if now.second % 5 == 0 :
    #POST
    segment.set_digit_raw(0, 0x73)
    segment.set_digit(1, 0)
    segment.set_digit(2, 5)
    segment.set_digit(3, 7)
  elif now.second % 5 < 2 :
    # write time of last post
    lastPostTime = dole_whip_info.get('last_post_time', 0)
    #if more than 9 days write OLD
    if (now - lastPostTime).days > 9 :
      logging.info('Writing OLD for post')
      segment.set_digit(1, 0)
      segment.set_digit_raw(0, 0x38)
      segment.set_digit(1, 'd')
    else :
      logging.info('Writing -%sd for post' % (now - last_photo_time).days)
      segment.set_digit(0,'-')
      segment.set_digit(1,(now - lastPostTime).days)
      segment.set_digit(2, 'd')
  else :
    ## Write Num posts
    likes = dole_whip_info.get('last_post_likes', '----')
    logging.info('Writing #%s for post' % likes)
    segment.print_number_str(likes)

  writeDisplay()

def updatePics(now) :
  segment.clear()
  
  if now.second % 5 == 0 :
    logging.info('Writing Pic')
    #PIC
    segment.set_digit_raw(0, 0x73)
    segment.set_digit(1, 1)
    segment.set_digit(2, 'c')
    
  elif now.second % 5 < 2 :
    # write time of last post
    last_photo_time = dole_whip_info.get('last_photo_time',0)
    #if more than 9 days write OLD
    if (now - last_photo_time).days > 9 :
      logging.info('Writing OLD for pic')
      segment.set_digit(1, 0)
      segment.set_digit_raw(1, 0x38)
      segment.set_digit(2, 'd')
    else :
      logging.info('Writing -%sd for pics' % (now - last_photo_time).days)
      segment.set_digit(0,'-')
      segment.set_digit(1,(now - last_photo_time).days)
      segment.set_digit(2, 'd')
  else :
    ## Write Num posts
    likes = dole_whip_info.get('last_photo_likes','----')
    logging.info('Writing #%s for pics' % likes)
    segment.print_number_str(likes)

  writeDisplay()


def main():
  # Continually update the time on a 4 char, 7-segment display
  while(True):
    now = datetime.datetime.now()
    if (now - lastUpdate).seconds > 60 :
      dole_whip_info = collect_dole_whip_info()
      lastUpdate = now
    
    if now.second % 30 < 10 :
      update_time(now)
    elif now.second % 30 < 20 :
      updatePost(now)
    else :
      updatePics(now)

      


if __name__ == "__main__": main()