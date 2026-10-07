from bs4 import BeautifulSoup
import sys
def extract_case_details(html):
    soup = BeautifulSoup(html,"html.parser")
    #print(sys.executable)

    strong_tags = soup.find_all("strong")
    case_title = strong_tags[0].get_text(" ",strip=True)
    coram = None
    if len(strong_tags) > 1:
        maybecoram = strong_tags[1].get_text(" ",strip=True)

        if(maybecoram.startswith("Coram")):
            coram = maybecoram
        
    #------> Self note to me : coram contains the info about the judges who looked into the petitions <----------
    case_details_tag = soup.find("strong", class_= "caseDetailsTD")
    #self note --> here I am getting the whole tag and everything inside of it and now I will extract the details of the case <----

    data = {
        "case_title" : case_title,
        "coram" : coram
    }

    if case_details_tag:
        case_details  = case_details_tag.get_text(" ",strip = True)

        for item in case_details.split("|"):
            key,value = item.split(":",1)
            data[key.strip()] = value.strip()

        
    
    # Self Note to me : ---> splitting the string into two parts and then assigning the first part to key and the next part to value python shortcut <---

    return data 
    



