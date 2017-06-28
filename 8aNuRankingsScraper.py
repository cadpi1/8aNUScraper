from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from urllib.request import urlopen
import time
import re
import csv

Rankings_URL = "https://www.8a.nu/Scorecard/Ranking.aspx?CountryCode=GLOBAL"


class EightANuScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.link_regex = re.compile("'../User/Profile.aspx?UserId=[0-9]+'")
    
    def ScrapeWebsite(self):
        
        self.ExtractSportClimbers()
        self.ExtractBoulderingProfiles()

    def ExtractSportClimbers(self):
        sport_climbing_profiles = []
        sport_climbers_profiles_urls = []
        pages_scraped = 0
        page = None
       
        #get 1000 names
        while not pages_scraped == 10:

            page = self.ReadNextRankingsPage(page, "sport")
            
            sport_urls = self.GetListOfProfileUrls(page, "sport")
            
            sport_climbers_profiles_urls.extend(sport_urls)

            pages_scraped = pages_scraped+1
            time.sleep(1)

        try:
            sport_climbing_profiles = self.ExtractDataFromUrls(sport_climbers_profiles_urls)
        except:
            print("an error occured erxtracting the profiles. saving what was extracted")

        self.SaveDataAsCSV(sport_climbing_profiles, "sport_climbers.csv")

    def ExtractBoulderingProfiles(self):
        bouldering_profiles = []
        bouldering_profiles_urls = []
        pages_scraped = 0
        page = None
        
        #get 1000 names
        while not pages_scraped == 10:

            page = self.ReadNextRankingsPage(page, "bouldering")
            
            boudlering_urls = self.GetListOfProfileUrls(page, "bouldering")
            
            bouldering_profiles_urls.extend(boudlering_urls)

            pages_scraped = pages_scraped+1
            time.sleep(1)
        
        try:
            bouldering_profiles = self.ExtractDataFromUrls(bouldering_profiles_urls)
        except:
            print("an error occured erxtracting the profiles. saving what was extracted")

        self.SaveDataAsCSV(bouldering_profiles, "boulderers.csv")

    def ReadNextRankingsPage(self, current_page, type):
        global Rankings_URL
        if (current_page == None):
            self.driver.get(Rankings_URL)
            return self.driver.page_source
        
        else:
            if type=="sport":
                self.FindAndClickNextSportButton()
            else:
                self.FindAndClickNextBoulderingButton()
            return self.driver.page_source

    def GetListOfProfileUrls(self, page, type):
        soup = BeautifulSoup(page, "html.parser")
        links = self.GetAllLinksInSection(soup, "GridViewRankingRoute" if type=="sport" else "GridViewBoulder")
        return links 

    def GetAllLinksInSection(self, soup, section_id):
        section = soup.find(id = section_id)
        links = section.find_all("a")
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
        cookie_name, session_id = self.GetSession()
        for link in links:
            try:
                data.append(self.ExtractDataFromUrl(link))
            except:
                #whatever could go wrong reading the data, skip that element 
                pass 

        time.sleep(1)
        return data

    def GetSession(self):
        page = urlopen("https://www.8a.nu")
        header = page.headers["Set-Cookie"]
        cookies = header.split(";")
        cookie_name, session_id = cookies[0].split("=")[0], cookies[0].split("=")[1]
        
        return (cookie_name, session_id)
    
    def ExtractDataFromUrl(self, url): 
        self.driver.get("https://www.8a.nu/User/Profile.aspx?UserId="+str(url))
        self.driver.switch_to_frame(self.driver.find_element_by_id("main"))
        climber_info = self.ExtractClimberInfo(self.driver.page_source)
        return climber_info
    
    def ExtractClimberInfo(self, source):
        soup = BeautifulSoup(source, "html.parser")
        name = soup.find(id="LabelUserName").text
        try:
            print( "added : "+ name)
        except:
            #avoid errors due to dodgy names
            pass
        dob = soup.find(id="LabelUserDataBirth").text
        height = soup.find(id="LabelUserDataHeight").text
        weight = soup.find(id="LabelUserDataWeight").text
        started_climbing = soup.find(id="LabelUserDataStartedClimbing").text
        occupation = soup.find(id="LabelUserDataOccupation").text
        interests = soup.find(id="LabelUserDataInterrests").text
        best_result = soup.find(id="LabelUserDataBestResult").text
        climbing_area = soup.find(id="LabelUserDataBestClimbingArea").text
        sponsors = soup.find(id="LabelUserDataLinks").text

        return (name if name else "Nan", dob if dob else "Nan", height if height else "Nan", weight if weight else "Nan",
         started_climbing if started_climbing else "Nan", occupation if occupation else "Nan", interests if interests else "Nan",
          best_result if best_result else "Nan", climbing_area if climbing_area else "Nan", sponsors if sponsors else "Nan")

    def SaveDataAsCSV(self, data, name):
        with open(name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            writer.writerow(['Name', 'Date of Birth', 'Height', 'Weight', 'Started Climbing', 'Occupation', 'Interests', 'Best Result', 'Climbing Area', 'Sponsors'])  
            for line in data:
                try:
                    writer.writerow(line)
                except:
                    #Dodgy endoging causes errors writing lines 
                    pass
            
    def FindAndClickNextSportButton(self):
        self.driver.find_element_by_link_text("Next 100").click()

    def FindAndClickNextBoulderingButton(self):
        self.driver.find_elements_by_link_text("Next 100")[1].click()
        
EightANuScraper().ScrapeWebsite()