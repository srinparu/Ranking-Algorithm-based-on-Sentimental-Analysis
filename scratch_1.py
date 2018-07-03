import os, json
from pprint import pprint
import pandas as pd
from datetime import date
import datetime
from textblob import TextBlob
import numpy as np

#Performing sentimental analysis
def sentiment_analysis(review):
    #Using TextBlob for the sentimental analysis
    try:
        blob = TextBlob(review)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        #Checking whether the review is positive or negative or neutral
        if polarity < 0:
            senti_score = polarity - subjectivity
            sentiment = "NEGATIVE"
            if abs(senti_score) > 1:
                senti_score = polarity
        elif polarity > 0:
            senti_score = polarity + subjectivity
            sentiment = "POSITIVE"
            if abs(senti_score) > 1:
                senti_score = polarity
        elif polarity == 0:
            senti_score = 0.0
            sentiment = "NEUTRAL"
        return sentiment, senti_score
    except Exception as e:
        return "NA", "NA"

#Main method which performs map and reduce.
def main():
    #Time at which data was collected from amazon
    maxUnixTime = 1406073600
    #Empty list that stores asin (product id )of all products
    asin = []
    '''Specifying the path to JSON file
    '''
    path_to_json = 'C:\\Users\\saipa\\.PyCharmCE2017.2\\config\\scratches'
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

    #Getting all the JSON files present in the specific location pointed

    print(json_files)

    #Loading the JSON file i,e creating the dictionary for the data present and printing the data

    data = json.load(open('Sam.json'))
    pprint(data)
    # Empty arrays
    review = []
    helpful=[]
    overall=[]
    unixReviewTime=[]
    music=[]
    later=[]
    totalReviews=[]
    # Empty Data frames
    product_pos_reviews = {}
    product_score = {}
    product_total_reviews = 200
    product_list = []
    product_launch_date = {}
    category_cluster = {}
    category = {}
    sales_rank = {}
    product_details = {}
    # Getting all the review texts and storing them in an array using the 'append' method
    for i in range(0, len(data['reviews'])):
        #print(i)
        reviewText = (data['reviews'][i]['reviewText'])
        a= (data['reviews'][i]['asin'])
        h= (data['reviews'][i]['helpful'])
        o= (data['reviews'][i]['overall'])
        u= (data['reviews'][i]['unixReviewTime'])
        m= (data['reviews'][i]['Music'])
        c= (data['reviews'][i]['CNT'])
        asin.append(a)
        helpful.append(h)
        overall.append(o)
        unixReviewTime.append(u)
        music.append(m)
        review.append(reviewText)
        totalReviews.append(c)
    #Printing all the reviews to check

        #print(review[i])
        #print(helpful[i])
        #print(overall[i])
        #print(unixReviewTime[i])
        sentiment, senti_score = sentiment_analysis(review[i])
        print(sentiment)
        print(senti_score)

        if sentiment == 'NA' or senti_score == 'NA':
            sentiment = "NA"
            senti_score = 0.0
        print(sentiment)
        print(senti_score)

    #Calculating Helpful Quotient and also using the "delta function

        helpful_value = helpful[i]
        helpful_vote = helpful_value[0]
        total_vote = helpful_value[1]
        if total_vote > 0:
            helpful_factor = 1 + (float(helpful_vote) / float(total_vote))
        else:
            helpful_factor = 1
        if (total_vote > 10 and total_vote <= 20):
            helpful_factor = helpful_factor * 1.3
        elif (total_vote > 20 and total_vote <= 30):
            helpful_factor = helpful_factor * 1.5
        elif (total_vote > 30 and total_vote <= 40):
            helpful_factor = helpful_factor * 1.7
        elif (total_vote > 40):
            helpful_factor = helpful_factor * 1.9
        print(helpful_factor)
        #REVIEW AGE FACTOR
        reviewTime = int(unixReviewTime[i])
        review_age_factor = 1 + (float(reviewTime) / float(maxUnixTime))
        print(review_age_factor)
        Review_Score = senti_score * helpful_factor * review_age_factor
        print(Review_Score)
        later.append(Review_Score)
        #Reduce operation
        if sentiment != "NA":
            if asin[i] not in product_list:
                product_list.append(asin[i])
            if sentiment == 'POSITIVE':
                if asin[i]  not in product_pos_reviews:
                    product_pos_reviews[asin[i]] = 1
                else:
                    pos_count = product_pos_reviews[asin[i]]
                    pos_count = pos_count + 1
                    product_pos_reviews[asin[i]] = pos_count
            if asin[i] not in product_score:
                product_score[asin[i]] = later[i]
            else:
                cumulative_score = product_score[asin[i]]
                cumulative_score = cumulative_score + later[i]
                product_score[asin[i]] = cumulative_score
            if asin[i] not in product_launch_date:
                product_launch_date[asin[i]] = unixReviewTime[i]
            else:
                min_unix_time = product_launch_date[asin[i]]
                if unixReviewTime[i] < min_unix_time:
                    min_unix_time = unixReviewTime[i]
                    product_launch_date[asin[i]] = min_unix_time

            if asin[i] not in sales_rank:
                sales_rank[asin[i]] = music[i]
            if asin[i] not in category:
                category[asin[i]] = "music"

    #print(product_pos_reviews)
    #print(product_score)
    #print(sales_rank)
    #print(category)
    #print(product_list)
    #print(product_launch_date)
    #REDUCE OPERATION
    for p_id in product_list:
        overall_product_rank = {}
        pid_unixtime = product_launch_date[p_id]
        d0 = (datetime.datetime.fromtimestamp(int(pid_unixtime)).strftime('%Y, %m, %d'))
        d1 = (datetime.datetime.fromtimestamp(int(maxUnixTime)).strftime('%Y, %m, %d'))
        date0 = d0.split(",")
        date1 = d1.split(",")
        date_d0 = date(int(date0[0]), int(date0[1]), int(date0[2]))
        date_d1 = date(int(date1[0]), int(date1[1]), int(date1[2]))
        difference = date_d1 - date_d0
        num_days = difference.days
        print(difference)
        year = float(num_days) / 365
        if year <= 0.0:
            year = 1.0
        #calculaton of PRODUCT POPULARITY
        product_age = float(product_total_reviews) / float(year)
        #CALCULATION of positive review factor
        product_positive_factor = float(product_pos_reviews[p_id]) / float(product_total_reviews)
        # calculation of overall product score
        overall_product_score = product_score[p_id] * product_age * product_positive_factor
        category_name = category[p_id]
        print(overall_product_score)
        print(category_name)
        print(product_age)
        print(product_positive_factor)
        if category_name not in category_cluster:
            category_product_list = []
            category_product_list.append(p_id)
            category_cluster[category_name] = category_product_list
        else:
            list_of_products = category_cluster[category_name]
            list_of_products.append(p_id)
            category_cluster[category_name] = list_of_products
        print(category_cluster)
        overall_product_rank['totalReviews'] = product_total_reviews
        overall_product_rank['positiveReviews'] = product_pos_reviews[p_id]
        overall_product_rank['overallProductScore'] = overall_product_score
        overall_product_rank['productAge'] = str(year) + " years"
        overall_product_rank['category'] = "music"
        overall_product_rank['salesRank'] = sales_rank[p_id]
        product_details[p_id] = overall_product_rank
        pprint(product_details)

    details=[]

    for each_category in category_cluster:
        i = 1
        list_of_product_ids = category_cluster[each_category]
        print(".......................................................................")
        #print(list_of_product_ids)
        ranking_list = []
        n = len(list_of_product_ids)
        for each_prod_id in list_of_product_ids:
            ranking_list.append(product_details[each_prod_id]['overallProductScore'])

        ids = np.array(ranking_list).argsort()[::-1][:n]
        #print(ids)
        for each_ids in ids:
            overall_product_details = product_details[list_of_product_ids[each_ids]]
            overall_product_details['asin'] = list_of_product_ids[each_ids]
            overall_product_details['productRank'] = i
            i = i + 1
            details.append(overall_product_details)
        print (json.dumps(details))
        with open('output.json', 'w') as outfile:
            json.dump(details, outfile,indent=2)
    #print(ranking_list)
    #print(list_of_product_ids)



if __name__ == "__main__":
    main()
