import pandas as pd
import create_graph
import articleparser


def main(input_file):
    """

    articles_dict stores LINK:LIST mapping, where:
    - LIST[0] contains the article
    - LIST[1] contains Source Credibility
    - LIST[2] contains List of tuples, with entity relations

    """

    articles_dict = dict()

    # Takes in a CSV and reads the information
    file_path = input_file
    df = pd.read_excel(file_path, skiprows=1)

    print(df.columns)

    for index, row in df.iterrows():
        column1_value = row[0]  # First column
        column2_value = row[1]  # Second column

        if column1_value not in articles_dict.keys():
            articles_dict[column1_value] = [column2_value, 0]
        else:
            articles_dict[column1_value][0] += column2_value

    # All articles should be added into the dictionary by now

    # Do News Credibility check, add it to index 1


    # Do article parsing
    for link in articles_dict.keys():
        article = articles_dict[link][0]
        # print(article)

        # Article parsing

        articles_dict[link].append(articleparser.parse_article(article))

        # Generate graph
        create_graph.generate_graph(articles_dict[link][2], link)




if __name__ == "__main__":
    main(input_file='news_excerpts_parsed.xlsx')