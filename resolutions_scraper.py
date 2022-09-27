# ASK:
# # I'm looking for Title, Action Date, and Action 
# # for all resolutions in 2006, 2007, 2008, 2010, 2011, 2013, 2016, and 2017. 
# # actually now we want the info displayed after the Show Details button is selected in the row:
# # # # fields: Title, Language, Notice Date, Action Date, Action, Sponsor, Cosponsors, moved by, second, votes, student_votes
import time
import re
import pandas as pd
from datetime import datetime
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file_path', type=str, required=False, help='path to file')

YEARS_WANTED = [2006,2007,2008,2010,2011,2013,2016,2017]
URL = 'https://dnnlt3f.pcifmhosting.com/fmi/webd/RESOLUTIONS'
DATE = datetime.now().strftime('%Y-%m-%d')
OUTPUT_FILE_NAME = f'{DATE}_Abby_resolutions_LAUSD'
args = parser.parse_args()
if args.file_path:
    FILE_PATH = args.file_path
    # Grab already read info:
    # FILE_PATH = "2022-08-21_Abby_resolutions_LAUSD.txt"
    existing_data = pd.read_csv(FILE_PATH,sep="\t")
    existing_xpaths = list(existing_data.SEARCH_xpath_details_button_id.unique())
    existing_resolutions = existing_data.to_dict('records')
else:
    existing_xpaths = []
    existing_resolutions = []

chrome_options = Options()
# chrome_options.add_argument("--headless") # un-comment out if you want to see the scraper in action
service = Service(ChromeDriverManager().install())
print("Opening browser...\n")
chrome_browser = webdriver.Chrome(options=chrome_options,service=service)
chrome_browser.get(URL)
time.sleep(3)

print("Going to show all results page...\n")
# find show all button --> gets us all the results on the page after selection
action = ActionChains(chrome_browser)
show_all_button = chrome_browser.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/div/div[2]/div/div/div[2]/div/div/div[2]/div/div[37]/button")
show_all_button.click()
time.sleep(3)

resolution_count_element = chrome_browser.find_element(By.ID,"b0p2o50i0i0r1")
total_resolutions = int("".join(re.findall('\d+', resolution_count_element.text)))
new_xpaths = []
resolutions_info = []
all_xpaths = []
print("Grabbing results...")
print(f"\nAdding existing results before looking for new ones:\n  *Previous xpaths: {len(existing_xpaths)}\n  *Previous resolutions: {len(existing_resolutions)}")
resolutions_info.extend(existing_resolutions)
while len(all_xpaths) < total_resolutions:
    table = chrome_browser.find_element(By.XPATH, '//*[@id="c0layoutcontainer"]/div/div[2]/div/div/div[2]/div/div/div[1]/div/div/div[1]/div/div[2]/div[1]/table/tbody')
    tmp_rows = table.find_elements(By.CLASS_NAME,"v-table-cell-content")
    middle_row_num = len(tmp_rows)/2
    middle_row = tmp_rows[int(middle_row_num)]
    print(f"Scrolling to middle of table to be safe...: row - ",middle_row.text.split("\n")[1])
    action.move_to_element(middle_row).perform() # otherwise we get stuck with initial results
    time.sleep(1)
    print(f"\nTotal rows in df currently at: {len(all_xpaths)}")
    if all_xpaths == []:
        all_xpaths.extend(existing_xpaths)
        xpath_index = 1
        if len(existing_xpaths) > 0:
            max_xpath_index = int(len(existing_xpaths))
            for i in range(xpath_index,max_xpath_index,15):
                iteration_xpath_index = i
                iteration_xpath_row_id = f'b0p1o0i{iteration_xpath_index}i0r1'
                print(f"Scrolling... to row [{iteration_xpath_index}]:{iteration_xpath_row_id}\n")
                row = table.find_element(By.XPATH,f'//*[@id="{iteration_xpath_row_id}"]')
                action.move_to_element(row).perform() # otherwise we get stuck with initial results
                time.sleep(1)
            xpath_index = max_xpath_index
    else:
        xpath_index = len(all_xpaths) + 1
        # every 5 rows, let's save our progress:
        if len(all_xpaths) % 5 == 0:
            print("Saving progress thus far..")
            df = pd.DataFrame(resolutions_info)
            df.to_csv(f"{OUTPUT_FILE_NAME}.txt", header=list(resolutions_info[0].keys()), index=False, sep='\t', mode='w')
    xpath_row_id = f'b0p1o0i{xpath_index}i0r1'
    details_button_id = f'b0p1o62i{xpath_index}i0r1'
    print(f"Scrolling... to row [{xpath_index}]:{xpath_row_id}\n")
    row = table.find_element(By.XPATH,f'//*[@id="{xpath_row_id}"]')
    action.move_to_element(row).perform() # otherwise we get stuck with initial results
    time.sleep(1)
    internal_id = row.id
    listing_row = row.text.split("\n")
    time.sleep(2)
    if xpath_row_id not in all_xpaths:
        details_button = chrome_browser.find_element(By.XPATH, f'//*[@id="{details_button_id}"]')
        details_button.click()
        time.sleep(3)
        votes_list = chrome_browser.find_element(By.XPATH, f'//*[@id="b0p1o50i0i0r1"]').text.split("\n")
        student_votes_list = chrome_browser.find_element(By.XPATH, f'//*[@id="b0p1o75i0i0r1"]').text.split("\n")
        cosponsors_list = chrome_browser.find_element(By.XPATH, f'//*[@id="b0p1o54i0i0r1"]').text.split("\n")
        if any(votes_list):
            print(votes_list)
            if len(votes_list) % 2 == 0:
                votes_dict = {votes_list[i]: votes_list[i + 1] for i in range(0, len(votes_list), 2)}
            else:
                new_votes_list = votes_list[:-1]
                votes_dict = {new_votes_list[i]: new_votes_list[i + 1] for i in range(0, len(new_votes_list), 2)}
                votes_dict[votes_list[-1]] = None
        else:
            votes_dict = None
        if any(student_votes_list):
            print(student_votes_list)
            if len(student_votes_list) % 2 == 0:
                student_votes_dict = {student_votes_list[i]: student_votes_list[i + 1] for i in range(0, len(student_votes_list), 2)}
            else:
                new_student_votes_list = student_votes_list[:-1]
                student_votes_dict = {new_student_votes_list[i]: new_student_votes_list[i + 1] for i in range(0, len(new_student_votes_list), 2)}
                student_votes_dict[student_votes_list[-1]] = None
        else:
            student_votes_dict = None
        resolution_details = {
            'SEARCH_action_date' : listing_row[0],
            'SEARCH_title' : listing_row[1],
            'SEARCH_resolution_number' : listing_row[-2],
            'SEARCH_internal_element_id' : internal_id,
            'SEARCH_xpath_details_button_id' : xpath_row_id,
            'DETAIL_title' : chrome_browser.find_element(By.XPATH, f'//*[@id="b0p1o4i0i0r1"]').text if chrome_browser.find_element(By.XPATH, f'//*[@id="b0p1o4i0i0r1"]').text != '' else None,
            'DETAIL_language' : chrome_browser.find_element(By.XPATH, f'//*[@id="b0p1o8i0i0r1"]').text if chrome_browser.find_element(By.XPATH, f'//*[@id="b0p1o8i0i0r1"]').text != '' else None,
            'DETAIL_notice_date' : chrome_browser.find_element(By.XPATH, f'//*[@id="b0p1o30i0i0r1"]').text if chrome_browser.find_element(By.XPATH, f'//*[@id="b0p1o30i0i0r1"]').text != '' else None,
            'DETAIL_action_date' : chrome_browser.find_element(By.XPATH, f'//*[@id="b0p1o28i0i0r1"]').text if chrome_browser.find_element(By.XPATH, f'//*[@id="b0p1o28i0i0r1"]').text != '' else None,
            'DETAIL_action' : chrome_browser.find_element(By.XPATH, f'//*[@id="b0p1o49i0i0r1"]').text if chrome_browser.find_element(By.XPATH, f'//*[@id="b0p1o49i0i0r1"]').text != '' else None,
            'DETAIL_sponsor' : chrome_browser.find_element(By.XPATH, f'//*[@id="b0p1o33i0i0r1"]').text if chrome_browser.find_element(By.XPATH, f'//*[@id="b0p1o33i0i0r1"]').text != '' else None,
            'DETAIL_cosponsors' : cosponsors_list if cosponsors_list != [''] else None,
            'DETAIL_votes' : votes_dict,
            'DETAIL_moved_by' : chrome_browser.find_element(By.XPATH, f'//*[@id="b0p1o45i0i0r1"]').text if chrome_browser.find_element(By.XPATH, f'//*[@id="b0p1o45i0i0r1"]').text != '' else None,
            'DETAIL_seconded' : chrome_browser.find_element(By.XPATH, f'//*[@id="b0p1o47i0i0r1"]').text if chrome_browser.find_element(By.XPATH, f'//*[@id="b0p1o47i0i0r1"]').text != '' else None,
            'DETAIL_student_votes' : student_votes_dict}
        print(resolution_details)
        resolutions_info.append(resolution_details)
        list_return_button = chrome_browser.find_element(By.XPATH, '//*[@id="b0p0o87i0i0r1"]')
        list_return_button.click()
        time.sleep(2)
        all_xpaths.append(xpath_row_id)

# print(f"""
# Length of:

# All_rows : {len(all_rows)}
# Total_resolutions : {total_resolutions}
# Resolutions : {len(resolutions)}
# """)

chrome_browser.quit()

df = pd.DataFrame(resolutions_info)
df.to_csv(f"{OUTPUT_FILE_NAME}.txt", header=list(resolutions_info[0].keys()), index=True, sep='\t', mode='w')
