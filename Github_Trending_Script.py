#!pip install requests 
#!pip install beautifulsoup4

#Improrting libs
import requests 
from bs4 import BeautifulSoup
import pprint
import pandas as pd
from datetime import datetime
from datetime import date


def get_trending_repositories():

    '''Call on the github trending repo landing page and tales all 
    the project links and splits the project name from the HTML link. '''

    url_to_call = "https://github.com/trending"
    response = requests.get(url_to_call, headers = {'User-Agent': "Mozilla/5.9"})
    response_code = response.status_code 
    if response_code != 200: 
        print("Error occured")
        return
    html_content = response.content 
    #print(html_content)
    dom = BeautifulSoup(html_content, 'html.parser')
    all_trending_repos = dom.select("article.Box-row h1")
    trending_repositories = []
    for each_trending_repo in all_trending_repos: 
        #print(each_trending_repo)
        href_link = each_trending_repo.a.attrs["href"]
        #print(href_link)
        name = href_link[1:] # this just removes the first dash 
        repo = {"label": name, 
                "link":"https://github.com/{}".format(href_link)}
        trending_repositories.append(repo)
    return trending_repositories



#Get number of commits
def get_commits(df):

    '''This function loops throught the column of links gathered from the github trending page, 
    finds an HTML class for the number of commits on the project page and return 
    the cleaned number into the dataframe'''


    df["commits"] = None
    for index, link in enumerate(df['link']):
        # make a GET request to the link
        response = requests.get(link, headers = {'User-Agent': "Mozilla/5.9"})
        # check the response status code
        if response.status_code != 200:
            print("Error occured while fetching the link:", link)
            continue
        # parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        stars_class = "ml-0 ml-md-3"
        commits = soup.find(class_=stars_class).text.strip()
        commits = commits.split("\n")[0]
        commits = int(commits.replace(",",""))
        df.at[index, "commits"] = commits
    return df

#Get the last commited date
def get_relative_date(df):

    '''This function scrapes the last date the code was 
    commited to the project and formats its into m/d/y'''

    df["last_commit_date"] = None
    for index, link in enumerate(df['link']):
        # make a GET request to the link
        response = requests.get(link, headers = {'User-Agent': "Mozilla/5.9"})
        # check the response status code
        if response.status_code != 200:
            print("Error occured while fetching the link:", link)
            continue
        # parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        relative_time = soup.select("relative-time.no-wrap")[0] #only want the most recent commit
        relative_time_datetime = relative_time.attrs["datetime"]
        datetime_object = datetime.strptime(relative_time_datetime, "%Y-%m-%dT%H:%M:%SZ")
        last_date = datetime_object.strftime("%m/%d/%y") #converting the datetime date into 1/25/23 format
        #print(last_date)
        df.at[index, "last_commit_date"] = last_date
    return df


#Create a new column for todays date 
def get_today_date(df):

    '''The below function simply returns today date when this data was scraped'''

    df["today_date"] = None 
    for index, link in enumerate(df["link"]):
        today_date = date.today()
        today_date = today_date.strftime("%m/%d/%y")
        df.at[index, "today_date"] = today_date
    return df


#Scraping the about section at the top 
def get_about_section(df):

    '''This function scrapes each about section from projects page and cleans the output '''

    df["Description"] = None
    for index, link in enumerate(df["link"]):
        # make a GET request to the link
        response = requests.get(link, headers = {'User-Agent': "Mozilla/5.9"})
        # check the response status code
        if response.status_code != 200:
            print("Error occured while fetching the link:", link)
            continue
        # parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        about = soup.select_one("div.BorderGrid-cell p")
        #about = about.text.strip()
        #print(about)
        df.at[index, "Description"] = about
        df["Description"]= df["Description"].astype(str) # converts object into string type
        df["Description"]= df["Description"].str.strip().str.replace('\n', '') # removes the /n space 
        df["Description"] = df["Description"].str.replace(r'<p.*?>', '').str.replace(r'<\/p>', '') #removes the p tag at the begging of the sentance 
    return df


# Number of forks 
def get_metrics(df):

    '''The below function scrapes the number of starts, watchers and forks the project has'''

    df["stars"] = None 
    df["watching"] = None
    df["forks"] = None
    for index, link in enumerate(df["link"]):
        # make a GET request to the link
        response = requests.get(link, headers = {'User-Agent': "Mozilla/5.9"})
        # check the response status code
        if response.status_code != 200:
            print("Error occured while fetching the link:", link)
            continue
        # parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        stars = soup.select("div.mt-2 a strong")[0].text.strip()
        watching = soup.select("div.mt-2 a strong")[1].text.strip()
        forks = soup.select("div.mt-2 a strong")[2].text.strip()
        #print(watching)
        df.at[index, "stars"] = stars
        df.at[index, "watching"] = watching
        df.at[index, "forks"] = forks
    return df


# Top 2 languages 
def get_languages(df):

    '''The goal is to scrape the top 2 languages used by the github 
    project and separate the language from the percent used'''

    df["language 1"] = None 
    df["language 2"] = None
    for index, link in enumerate(df["link"]):
        # make a GET request to the link
        response = requests.get(link, headers = {'User-Agent': "Mozilla/5.9"})
        # check the response status code
        if response.status_code != 200:
            print("Error occured while fetching the link:", link)
            continue
        # parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        #stars_class = "sr-only"
        #forks = soup.find(class_=stars_class).text.strip()
        #forks = soup.select("div.mt-2 a strong")
        lang = soup.select("li.d-inline")
        lang1 = "None"
        lang2 = "None"

        if len(lang) >  0:
            lang1 = lang[0].text.strip()
        if len(lang) > 1:
            lang2 = lang[1].text.strip()

        #lang2 = soup.select("div.mt-2 a strong")[1].text.strip()
        df.at[index, "language 1"] = lang1 or "None"
        df.at[index, "language 2"] = lang2 or "None"        
    return df


def split_columns(df, cols):
    for col in cols:
        df[f"{col}_language"] = df[col].apply(lambda x: x.split("\n")[0] if isinstance(x, str) and "\n" in x else x)
        df[f"{col}_percent"] = df[col].apply(lambda x: x.split("\n")[1] if isinstance(x, str) and "\n" in x else "None")
    return df


#Running the code
if __name__ == "__main__":
    print("Started scraping")
    trending_repos = get_trending_repositories()
    print("Scraping Trending Repo Links")
    df = pd.DataFrame.from_records(trending_repos)
    df = get_relative_date(df)
    print("Scraping last day commited")
    df = get_commits(df)
    print("Scraping number of commits")
    df = get_today_date(df)
    print("Scraping decriptions")
    df = get_about_section(df)
    print("Scraping metrics")
    df= get_metrics(df)
    print("Scraping languages")
    df = get_languages(df)
    print("Cleaning languages")
    df = split_columns(df, cols)
    df = df.drop(columns=["language 1", "language 2"]) #droping the initial columns
df.to_csv('Github_Trending.csv', mode='a', index=False, header=False)
print("Finished scraping :)")
df