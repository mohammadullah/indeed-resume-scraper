import urllib.request
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import json
import threading
from random import randint
from time import sleep
from math import ceil
import os
import argparse
from urllib.parse import quote_plus
import traceback
import sys

NUM_INDEED_RESUME_RESULTS = 50
INDEED_RESUME_BASE_URL = 'https://resumes.indeed.com/resume/'
INDEED_RESUME_SEARCH_BASE_URL = 'https://resumes.indeed.com/search/'

# RESUME SUBSECTIONS TITLE (in normal setting)
WORK_EXPERIENCE = 'Work Experience'
EDUCATION = 'Education'
SKILLS = 'Skills'
CERTIFICATIONS = 'Certifications'
ADDITIONAL_INFORMATION = 'Additional Information'

class Resume(object):
	def __init__ (self, idd, jobs=None, schools=None):
		self.id = idd
		self.jobs = jobs
		self.schools = schools

	def toJSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, 
			sort_keys=True, indent=2)


class Job(object):
	def __init__(self, title, company, work_dates, details):
		self.title = title
		self.company = company

		dates = work_dates.split(' to ')
		self.start_date = dates[0]
		self.end_date = '' if len(dates) == 1 else dates[1]

		self.details = details

class School(object):
	def __init__(self, degree, school_name, grad_date):
		self.degree = degree
		self.school_name = school_name
		self.start_date = ''
		self.end_date = ''

		if grad_date is not None:
			dates = grad_date.split(' to ')
			self.start_date = dates[0]
			self.end_date = '' if len(dates) == 1 else dates[1]

def gen_idds(url, driver):

	driver.get(url)

	resume_links = []
	try:
		resume_links = driver.find_elements_by_css_selector('.icl-TextLink.icl-TextLink--primary.rezemp-u-h4')
	except TimeoutException:
		# could not complete in time 
		resume_links = []
	finally:
		idds = [link.get_attribute('href') for link in resume_links]
		idds = [idd[idd.rfind('/')+1:idd.rfind('?')] for idd in idds]

	return idds

def produce_work_experience(worksection):
	work_experience = worksection.find_all('div', class_='rezemp-WorkExperience')
	jobs = []
	for experience in work_experience:
		job_title = experience.find('div', class_='rezemp-u-h4').get_text()
		company_and_dates = experience.find('div', class_='rezemp-WorkExperience-subtitle')

		company_name = company_and_dates.find('span', class_='icl-u-textBold').get_text()
		work_dates = company_and_dates.find('div', class_='icl-u-textColor--tertiary').get_text()
		job_details = []
		if len(experience.contents) == 3:
			# there are job details
			details = experience.contents[-1]
			job_details = [detail for detail in details.stripped_strings]

		jobs.append(Job(job_title, company_name, work_dates, job_details))
	return jobs

def produce_education(edusection):
	content = edusection.find('div', class_='rezemp-ResumeDisplaySection-content')
	schools = []
	for school in content.children:
		degree = school.find(class_ = "rezemp-ResumeDisplay-itemTitle")
		if degree is not None:
			degree = degree.get_text(' ', strip=True)
		university_details = school.find(class_="rezemp-ResumeDisplay-university")
		school_name = university_details.find('div', class_='icl-u-textBold')
		if school_name is not None:
			school_name = school_name.get_text()
		date = school.find(class_="rezemp-ResumeDisplay-date")
		if date is not None:
			date = date.get_text()
		schools.append(School(degree, school_name, date))
	return schools

def produce_skills():
	pass

def produce_certifications_license():
	pass

def produce_info():
	pass

def gen_resume(idd, driver):
	resume_url = INDEED_RESUME_BASE_URL + idd

	driver.get(resume_url)
	p_element = driver.page_source
	soup = BeautifulSoup(p_element, 'html.parser')

	resume_subsections = soup.find_all('div', attrs={"class":"rezemp-ResumeDisplaySection"})

	resume_details = {
		'jobs': None,
		'schools': None
	}
	for subsection in resume_subsections:
		children = subsection.contents
		subsection_title = children[0].get_text()
		if subsection_title == WORK_EXPERIENCE:
			resume_details['jobs'] = produce_work_experience(subsection)
		elif subsection_title == EDUCATION:
			resume_details['schools'] = produce_education(subsection)
		elif subsection_title == SKILLS:
			produce_skills()
		elif subsection_title == CERTIFICATIONS:
			produce_certifications_license()
		elif subsection_title == ADDITIONAL_INFORMATION:
			produce_info()
		else:
			print('ID', idd, '- Subsection title is', subsection_title)

	return Resume(idd, **resume_details)

def mine(filename, URL, override=True, search_range=None):
	driver = webdriver.Firefox()
	driver.implicitly_wait(10)

	if override:
		# implicitly empty file
		open(filename, 'w').close()

	search = search_range[0]
	end = search_range[1]

	try:
		while search < end:
			stri = URL + '&start=' + str(search)
			idds = gen_idds(stri, driver)
			# move to the next results irrespective
			search += NUM_INDEED_RESUME_RESULTS
			if(len(idds) == 0):
				time.sleep(2)
				continue

			with open(filename, 'a') as outfile:
				for idd in idds:
					outfile.write(gen_resume(idd, driver).toJSON() + "\n")

		# resumes = [gen_resume(idd).toJSON() for idd in idds] 
	except Exception as e:
		sys.stderr.write('Caught exception ' + str(e) + traceback.format_exc() + "\n")
	finally:
		driver.close()


def mine_multi(args, search_URL):
	thread_list = []
	names = []

	start = args.si
	end = args.ei
	tr = args.threads
	starting_points = list(range(start, end, (end - start) // tr))
	for idx, search_start in enumerate(starting_points):
		# Instantiates the thread
		filename = 'resume_output' + args.name + str(idx) + '.json'
		t = threading.Thread(
			target=mine,
			args=(filename, search_URL),
			kwargs={
				"override" : args.override,
				"search_range" : (search_start, end if idx + 1 == len(starting_points) else starting_points[idx + 1])
			}
		)
		# Sticks the thread in a list so that it remains accessible
		thread_list.append(t)
		names.append(filename)

	# Starts threads
	for thread in thread_list:
		thread.start()

	# This blocks the calling thread until the thread whose join() method is called is terminated.
	# From http://docs.python.org/2/library/threading.html#thread-objects
	for thread in thread_list:
		thread.join()

	consolidate_files(args.name, names, args.override)

def consolidate_files(name, names, override=True):
	mode = 'w' if override else 'a'
	file = open("resume_output_" + name + ".json", mode)
	for nam in names:
		with open(nam, 'r') as read:
			file.write(read.read())
		os.remove(nam)
			
	file.close()

def main(args):
	t = time.clock()
	# restrict search only to job titles skills and field of study
	search_URL= f"{INDEED_RESUME_SEARCH_BASE_URL}?q={args.q}&l={args.l}&searchFields=jt,skills,fos"
	search_URL = quote_plus(search_URL, safe='/:?&=')

	mine_multi(args, search_URL)
	print(time.clock() - t),

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Scrape Indeed Resumes', usage='python indeed-scraper.py <arguments>')
	parser.add_argument('-q', metavar='query', required=True, help='search query to run on indeed e.g software engineer')
	parser.add_argument('-l', default='Canada', metavar='location', help='location scope for search')
	parser.add_argument('-si', default=0, type=int, metavar='start', help='starting index (multiples of 50)')
	parser.add_argument('-ei', default=5000, type=int, metavar='end', help='ending index (multiples of 50)')
	parser.add_argument('--threads', default=8, type=int, metavar='threads', help='# of threads to run')
	parser.add_argument('--override', action='store_true', help='override existing result if any')
	parser.add_argument('--name', metavar='name', required=True, help='name of search (used to save files)')

	args = parser.parse_args()
	main(args)