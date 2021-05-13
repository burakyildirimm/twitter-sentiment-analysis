from textblob import TextBlob
import twint
import datetime
import json
import os
import re
import asyncio
import nest_asyncio
nest_asyncio.apply()


def controlTwitterFile():
    if os.path.exists('twitter.json'):
        os.remove('twitter.json')
    return


async def formatData():
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
    controlTwitterFile()

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(1)
    now = datetime.datetime.now().strftime("%H:%M:%S")

    c = twint.Config
    c.Search = 'bitcoin'
    c.Lang = 'tr'
    c.Limit = 5
    c.Output = 'twitter.json'
    c.Since = str(yesterday)+" 23:59:00"
    c.Until = str(today)+ " " + str(now)
    c.Store_json = True

    await twint.run.Search(c)
    await formatData()



async def cleanTweets(tweets):
    response = []
    for tweet in tweets:
        if len(re.findall('@', tweet)) > 0:
            cleaned =  re.sub('@[0-9]*[A-Za-z]*[0-9]*', '', tweet)
            cleaned =  re.sub('#[0-9]*[A-Za-z]*[0-9]*', '', cleaned)
            cleaned =  re.sub('https://[0-9]*[A-Za-z]*[0-9]*', '', cleaned)
            cleaned =  re.sub('http://[0-9]*[A-Za-z]*[0-9]*', '', cleaned)
            cleaned =  re.sub('[0-9]*[A-Za-z]*[0-9]*@+[0-9]*[A-Za-z]*[0-9]*\.[a-z]*', '', cleaned, flags=re.S)
            response.append(cleaned)

    return response
    

async def getTweets():
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
        return result
    except:
        print('Error occured while cleaning data..')


def analysis(tweets):
    if tweets == None:
        print("Analysis could not be done!")
        return
    polarity = 0
    positive = 0
    neutral = 0
    negative = 0
    print("lenght : " + str(len(tweets)))
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
    await fetchData()
    tweets = await getTweets()
    analysis(tweets)


    

if __name__ == '__main__':
    asyncio.run(main())