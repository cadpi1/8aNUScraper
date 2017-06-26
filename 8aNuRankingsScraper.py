from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from urllib.request import urlopen
import time
import re
import csv

Rankings_URL = "https://www.8a.nu/Scorecard/Ranking.aspx?CountryCode=GLOBAL"


class Scraper:


    def __init__(self):
        self.driver = webdriver.Chrome()
        self.link_regex = re.compile("'../User/Profile.aspx?UserId=[0-9]+'")
    
    def ScrapeWebsite(self):
        sport_climbing_profiles = []
        bouldering_profiles = []

        sport_climbers_profiles_urls = []
        boulderes_profiles_urls = []

        driver = webdriver.Chrome()

        page = None
        
        pages_scraped = 0

        while not pages_scraped == 1:

            page = self.ReadNextSportRankingsPage(page)
            
            sport_urls = self.GetListOfSportUrls(page)
            
            sport_climbers_profiles_urls.extend(sport_urls)
            
            #boulderes_profiles_urls.append(boulderer_urls)
        
            pages_scraped = pages_scraped+1
            time.sleep(2)

        sport_climbing_profiles = self.ExtractDataFromUrls(sport_climbers_profiles_urls)

        self.SaveDataAsCSV(sport_climbing_profiles, "sport_climbers.csv")


    def ReadNextSportRankingsPage(self, current_page):
        global Rankings_URL
        if (current_page == None):
            self.driver.get(Rankings_URL)
            return self.driver.page_source
        
        else:
            self.FindAndClickNextSportButton()
            return self.driver.page_source

    def GetListOfSportUrls(self, page):
        soup = BeautifulSoup(page, "html.parser")
        sport_climbing_links = self.GetAllLinksInSection(soup, "GridViewRankingRoute")
        
        return sport_climbing_links

    def GetAllLinksInSection(self, soup, section_id):
        section = soup.find(id = section_id)
        links = soup.find_all("a")
        profile_ids = self.FilterProfileLinks(links)
        return profile_ids

    def FilterProfileLinks(self, links):
        profiles = []
        for link in links:
            href = link.attrs["href"]
           
            if "User/Profile.aspx" in href:
                
                profiles.append(int(href.replace("../User/Profile.aspx?UserId=", "")))
        return profiles

    def ExtractDataFromUrls(self, links):
        data = []
        print("Preparing to fetch links : number of links "+str(len(links)))
        #for link in links:
        data.append(self.ExtractDataFromUrl(links[0]))
        data.append(self.ExtractDataFromUrl(links[1]))
        time.sleep(1)
        return data
    
    def ExtractDataFromUrl(self, url): 
        url= "https://www.8a.nu/User/Profile.aspx?UserId="+str(url)
        data = urlopen(url)
        climber_info = self.ExtractClimberInfo(data.read())
        return climber_info
    
    def ExtractClimberInfo(self, source):
        soup = BeautifulSoup(source, "html.parser")
        print(soup)
        name = soup.find(id="LabelUserName")
        print(name)
        dob = soup.find(id="LabelUserDataBirth")
        height = soup.find(id="LabelUserDataHeight")
        weight = soup.find(id="LabelUserDataWeight")
        started_climbing = soup.find(id="LabelUserDataStartedClimbing")
        occupation = soup.find(id="LabelUserDataOccupation")
        interests = soup.find(id="LabelUserDataInterrests")
        best_result = soup.find(id="LabelUserDataBestResult")
        climbing_area = soup.find(id="LabelUserDataBestClimbingArea")
        sponsors = soup.find(id="LabelUserDataLinks")

        return (name if name else "Nan", dob if dob else "Nan", height if height else "Nan", weight if weight else "Nan",
         started_climbing if started_climbing else "Nan", occupation if occupation else "Nan", interests if interests else "Nan",
          best_result if best_result else "Nan", climbing_area if climbing_area else "Nan", sponsors if sponsors else "Nan")

    def SaveDataAsCSV(self, data, name):
        with open(name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            writer.writerow(['Name', 'Date of Birth', 'Height', 'Weight', 'Started Climbing', 'Occupation', 'Interests', 'Best Result', 'Climbing Area', 'Sponsors'])  
            for line in data:
                writer.writerow(line)

    def FindAndClickNextSportButton(self):
        print( self.driver.find_element_by_link_text("Next 100"))
        self.driver.find_element_by_link_text("Next 100").click()

        
Scraper().ScrapeWebsite()