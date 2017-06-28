from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv


def Get8aNuProfileUrls():
    rankings_page = urlopen('https://www.8a.nu/Scorecard/Ranking.aspx?CountryCode=GLOBAL')
    page_soupy = BeautifulSoup(rankings_page)
    return GetProfileLinks(page_soupy)

def GetProfileLinks(page):
    sport_climbing_profiles = GetProfilesForSection(page.find(id='GridViewRankingRoute'))
    bouldering_profiles = GetProfilesForSection(page.find(id='GridViewBoulder'))
    return sport_climbing_profiles

def GetProfilesForSection(section):
    all_urls = section.find_all("a")
    profile_links = []
    for url in all_urls:
        if "/User/Profile.aspx" in url:
            profile_links.append(url)
    return profile_links


all_urls = Get8aNuProfileUrls()
for url in all_urls:
    try:
        print(url)
    except:
        pass