# Usage: python linkedout.py $linkedin_email $linkedin_password $linkedin_search_company $email_format

import sys
import re
from robobrowser import RoboBrowser
import bs4
from requests import Session

if len(sys.argv) < 5:
	print("Usage: python linkedout.py $linkedin_email $linkedin_password $linkedin_search_company $email_format\n\nemail format schema:\nfirstmiddlelast@domain.com\nfmiddlelast@domain.com\nfml@domain.com\nfmlast@domain.com\nflast@domain.com\n\n")
	sys.exit(0)

session = Session()

collected = 0
username = sys.argv[1]
password = sys.argv[2]
company_search = sys.argv[3]
email_format = sys.argv[4]

real_format = email_format.split("@")

# Browse to Genius
browser = RoboBrowser(parser='html.parser',session=session,user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:49.0) Gecko/20100101 Firefox/49.0')
browser.open('https://www.linkedin.com/uas/login?session_redirect=https://www.linkedin.com/vsearch/p?company=' + company_search + '&openAdvancedForm=true&companyScope=C&fromSignIn=true&trk=uno-reg-join-sign-in')

form = browser.get_form(action="https://www.linkedin.com/uas/login-submit")

form['session_key'].value = username
form['session_password'].value = password
browser.submit_form(form)

while str(browser.parsed).find("Next") != -1:
	str_src = str(browser.parsed)

	if str_src.find("you’ve reached the commercial use limit on") != -1:
		print("\n\n\nREKKKKKT Rate Limited\n\nGathered Total: [" + str(collected) + "]\n\n\n")
		sys.exit(0)

	pattern = re.compile('(?<="fmt_name":")(.*?)(?=",)')
	results = pattern.findall(str_src)

	collected += len(results)
	print("\n\nCollected: [" + str(collected) + "] - " + company_search + " Employees...\n\n")

	for person in results:
		if person.find("LinkedIn Member") == -1:
			person = person.replace("\u002d", "-")
			names = re.findall('\w+', person)
			
			if real_format[0] == "firstmiddlelast":
				file_str = ''.join(names)
			elif real_format[0] == "fmiddlelast":
				file_str = min(names)[0]
				if len(names) == 3:
					file_str += names[1]
				file_str += max(names)
			elif real_format[0] == "fml":
				file_str = min(names)[0]
				if len(names) == 3:
					file_str += names[1][0]
				file_str += max(names)[0]
			elif real_format[0] == "fmlast":
				file_str = min(names)[0]
				if len(names) == 3:
					file_str += names[1][0]
				file_str += max(names)
			elif real_format[0] == "flast":
				file_str = min(names)[0] + max(names)

		print(file_str + "@" + real_format[1])

		with open(company_search + ".txt", "a") as f:
		    f.write(file_str + "@" + real_format[1] + "\n")

	# for debugging
	# with open("src.html", "w") as f:
	#     f.write(str_src)

	next_page = re.compile('(?<=isCurrentPage":true,"pageURL":")(.*?)(?=","pageNum")')
	next_url = next_page.findall(str_src)

	page_num = int(next_url[0].split("page_num=")[1])
	page_num += 1

	goto_url = next_url[0].split("page_num=")[0] + "page_num=" + str(page_num)

	browser.open('https://www.linkedin.com' + goto_url)