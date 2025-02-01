import pandas as pd
import create_graph
import articleparser




def addToDB(input_dict):
    """

    NOT TESTED


    Takes in a dictionary which should have the URI as the Key, and the full article as the value.
    Using full article, gets output from articleparser.parse_article() which will return:
    - Summary of article
    - Credibility of article

    Should call another function to find any related articles that are currently stored in the DB.
    
    Adds the article and details to the DB
    
    """

    for uri in input_dict.keys():
        article = input_dict[uri]
        
        # Gets summary, credibility and related articles
        summary, credibility = articleparser.parse_article(article, uri)
        
        # Maybe can add a function call to find any related articles to the current article being processed
        
        # Connect to DB and add it to the table
        

        # Most likely need to handle ',"
        article = article.replace("\\", "\\\\")
        article = article.replace('"', "'")
        # Possible Statement
        columns = 'link, fullarticle, summary, credibility, related'
        values = f""""{uri}", "{article}", {summary}, {credibility}, NULL"""
        sql_statement = f"INSERT INTO ARTICLES ({columns}) VALUES ({values})"
        
        

    # def testprocessing(input_file):
    # """

    # Currently only able to handle CSV file format

    # articles_dict stores LINK:LIST mapping, where:
    # - LIST[0] contains the article
    # - LIST[1] contains Source Credibility
    # - LIST[2] contains List of tuples, with entity relations
    # - LIST[3] contains 

    # """

    # articles_dict = dict()

    # # Takes in a CSV and reads the information
    # file_path = input_file
    # df = pd.read_excel(file_path, skiprows=1)

    # print(df.columns)

    # for index, row in df.iterrows():
    #     articleLink = row[0]  # First column
    #     articleText = row[1]  # Second column

    #     if articleLink not in articles_dict.keys():
    #         articles_dict[articleLink] = [articleText, 0]
    #     else:
    #         articles_dict[articleLink][0] += articleText
    

    # # All articles should be added into the dictionary by now

    # # Do News Credibility check, add it to index 1

    # # print(articles_dict)


    # # # Do article parsing
    # # for link in articles_dict.keys():
    # #     article = articles_dict[link][0]
    # #     print(article)

    # #     # Article parsing

    # #     relationship = articleparser.parse_article(article)

    # #     articles_dict[link].append(relationship)

    # #     # Generate graph
    # #     create_graph.generate_graph(articles_dict[link][2], link)

    # print("[!] DONE")



def processing(input_file):
    """
    Need to be able to handle all the different approved file types

    Returns a dictionary with URI:Article
    """






def testprocessing(input_file):
    """
    Hardcoded function to handle 'news_excerpts_parsed.xlsx'
    Returns .sql file that can be imported to a DB.
    """

    articles_dict = dict()

    # Takes in a CSV and reads the information
    file_path = input_file
    df = pd.read_excel(file_path, skiprows=1)

    for index, row in df.iterrows():
        articleLink = row[0]  # First column
        articleText = row[1]  # Second column

        if articleLink not in articles_dict.keys():
            articles_dict[articleLink] = articleText
        else:
            articles_dict[articleLink] += articleText

    
    # Step 2: Define the table name
    table_name = 'ARTICLES'  # Replace with your actual table name
    # Step 3: Open the .sql file for writing
    sql_file = 'output.sql'

    with open(sql_file, 'w') as outfile:
        for thing in articles_dict.keys():
            columns = 'link, fullarticle, articlename, summary, credibility, tags, related'
            text = articles_dict[thing]
            text = text.replace("\\", "\\\\")
            text = text.replace('"', "'")
            thing = thing.replace("\\", "\\\\")
            values = f""""{thing}", "{text}", NULL, NULL, NULL, NULL, NULL"""

            sql_statement = f"INSERT INTO {table_name} ({columns}) VALUES ({values});\n"
            outfile.write(sql_statement)
        



if __name__ == "__main__":
    testprocessing(input_file='../news_excerpts_parsed.xlsx')