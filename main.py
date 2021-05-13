from textblob import TextBlob
import twint
import datetime
import json
import os
import re
import asyncio
import nest_asyncio
nest_asyncio.apply()    # a plugin for asyncio to work properly with (twint)

# Setting up Global variables

SEARCH_TERM = ['rich', 'bitcoin']
SEARCH_LANG = 'en'
SEARCH_COUNT = 30
OUPUT_FILE = 'twitter.json'

# Setting up functions

async def controlTwitterFile():
    # This function check if the file exists

    if os.path.exists('twitter.json'):
        os.remove('twitter.json')
    return


async def copyToTweetsPage():
    # We extract the data that need to be analyzed here

    tweets = {}
    tweets["tweets"] = []
    try:
        with open('twitter.json', 'r+') as file:
            datas = file.readlines()

            for data in datas:
                info = json.loads(data)
                tweet = info["tweet"]
                tweets["tweets"].append(tweet)

            file.close()
    except:
        print('Can not open file for formatting!')
        return


    try:
        with open('tweets.json', 'w+') as newFile:
            json.dump(tweets, newFile, indent=4, ensure_ascii=False)
            newFile.close()
    except:
        print('Can not open file for writing')

async def fetchData():
    # Let's fetch the our target tweets with twint!

    await controlTwitterFile()

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(1)
    now = datetime.datetime.now().strftime("%H:%M:%S")
    
    c = twint.Config
    c.Search = SEARCH_TERM
    c.Lang = SEARCH_LANG
    c.Limit = SEARCH_COUNT
    c.Output = OUPUT_FILE
    c.Since = str(yesterday)
    c.Until = str(today)+ " " + str(now)
    c.Store_json = True

    await twint.run.Search(c)
    await copyToTweetsPage()



async def cleanTweets(tweets):
    # This function clears all unwanted data

    response = []
    for tweet in tweets:
        if len(re.findall('@', tweet)) > 0:
            cleaned = await re.sub('@[0-9]*[A-Za-z]*[0-9]*', '', tweet)
            cleaned = await re.sub('#[0-9]*[A-Za-z]*[0-9]*', '', cleaned)
            cleaned = await re.sub('https://[0-9]*[A-Za-z]*[0-9]*', '', cleaned)
            cleaned = await re.sub('http://[0-9]*[A-Za-z]*[0-9]*', '', cleaned)
            cleaned = await re.sub('[0-9]*[A-Za-z]*[0-9]*@+[0-9]*[A-Za-z]*[0-9]*\.[a-z]*', '', cleaned, flags=re.S)
            response.append(cleaned)

    return response
    

async def getTweets():
    # let's we take all tweets as an array!

    result = []
    try:
        with open('tweets.json', 'r') as file:
            datas = json.load(file)["tweets"]
            for data in datas:
                result.append(data)
                
            file.close()
    except:
        print('Can not open file')
    
    try:
        result = await cleanTweets(result)
    except:
        print('Error occured while cleaning data..')
        print('Regex async problem, waiting for to be fixed!')

    return result


def analysis(tweets):
    # Now we can analyze sentiment

    if tweets == None:
        print("Analysis could not be done!")
        return
    polarity = 0
    positive = 0
    neutral = 0
    negative = 0
    print("tweets count : " + str(len(tweets)))
    for tweet in tweets:
        analysis = TextBlob(tweet)
        tweetPolarity = analysis.polarity
        print(str(tweetPolarity)+" ****")
        if tweetPolarity > 0.0:
            positive += 1
        elif tweetPolarity == 0.0:
            neutral += 1
        elif tweetPolarity < 0.0:
            negative += 1

        polarity += tweetPolarity

         
    print(f'Positive tweets: {positive}')
    print(f'Neutral tweets: {neutral}')
    print(f'Negative tweets: {negative}')
    print(f'Total: {polarity}')

async def main():
    # main flow

    await fetchData()
    tweets = await getTweets()
    analysis(tweets)


    

if __name__ == '__main__':
    asyncio.run(main())