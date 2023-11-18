#!/usr/bin/python

import sys
import datetime
import json
import requests
import subprocess as sb
from requests.auth import HTTPBasicAuth

def generate_new_entry(filename, date, title, content, url):
  with open('content/timeline/generated-' + filename, 'a') as f:
    f.write('---\n')
    f.write('title: ' + title + '\n')
    f.write('draft: false\n')
    f.write('type: "timeline"\n')
    f.write('date: ' + date + '\n')
    f.write('---\n')
    f.write(content[0:250] + '\n\n[Read more](' + url + ')')

def generate_new_milestone(milestone, issues, milestoneNo):
  if (len(issues) > 0):
    with open('content/roadmap/generated-milestone-' + milestone + '.md', 'a') as f:
        f.write('---\n')
        f.write('title: Milestone ' + milestone + '\n')
        f.write('draft: false\n')
        f.write('type: "roadmap"\n')
        f.write('date: ')
        f.write(str(datetime.datetime.now().year))
        f.write('-')
        f.write(str(datetime.datetime.now().month))
        f.write('-')
        f.write(str(datetime.datetime.now().day))
        f.write('\n')
        f.write('---\n')
        f.write('Milestone ![**' + milestone + '**](https://github.com/KaotoIO/kaoto-next/milestone/' + milestoneNo + ') ')
        
        open_issues = 0;
        for issue in issues:
          if (issue['state'] != 'closed'):
            open_issues += 1;
            
        progress = str(round(100*(len(issues) - open_issues)/len(issues)));
        f.write('![](https://geps.dev/progress/');
        f.write(progress);
        f.write('?dangerColor=800000&warningColor=ff9900&successColor=006600)\n\n');
        
        for issue in issues:
          f.write(' - *')
          f.write(issue['state'])
          f.write('* ')
          if (issue['state'] == 'closed'):
            f.write('~~')
          f.write('[')
          f.write(issue['title'])
          f.write('](')
          f.write(issue['html_url'])
          f.write(')')
          if (issue['state'] == 'closed'):
            f.write('~~')
          f.write('\n')


authentication = HTTPBasicAuth( sys.argv[1],  sys.argv[2])
stargazers = []
mergedprs = 0
forks = 0
contributors = []
milestones = {}
milestoneNumbers = {}

repositories = requests.get('https://api.github.com/orgs/KaotoIO/repos', auth = authentication)
print("Processing repositories...")
for repo in repositories.json():
  print("Processing " + repo['full_name'])
  
  # we are atm only interested in releases and milestones of Kaoto-Next
  if (repo['full_name'] == 'KaotoIO/kaoto-next'):
    #releases
    data = requests.get('https://api.github.com/repos/' + repo['full_name'] + '/releases', auth = authentication)
    for release in data.json():
        if (not (release['published_at'] is None)):
          generate_new_entry('release-' + release['published_at'] + '.md', release['published_at'], release['name'], release['body'], release['html_url'])
          
    #milestones
    data = requests.get('https://api.github.com/repos/' + repo['full_name'] + '/milestones', auth = authentication)
    for milestone in data.json():
      if (milestone['state'] == "open"):
        msTitle = milestone['title']
        msNumber = str(milestone['number'])
        if msTitle not in milestones: 
           milestones[msTitle] = []
        if msTitle not in milestoneNumbers:
           milestoneNumbers[msTitle] = msNumber
        issues = requests.get('https://api.github.com/repos/' + repo['full_name'] + '/issues?state=all&milestone=' + msNumber, auth = authentication)
        for issue in issues.json():
            milestones[msTitle].append(issue)

  # but we want to aggregate the remaining stats from all repos in the org

  # followers
  data = requests.get('https://api.github.com/repos/' + repo['full_name'] + '/stargazers', auth = authentication)
  for stargazer in data.json():
      if stargazer['login'] not in stargazers: 
         stargazers.append(stargazer['login'])
      
  # merged pr
  data = requests.get('https://api.github.com/search/issues?q=repo:' + repo['full_name'] + '+is:pr+is:merged', auth = authentication)
  mergedprs = mergedprs + data.json()['total_count']
  
  # forks
  data = requests.get('https://api.github.com/repos/' + repo['full_name'] + '/forks?per_page=100', auth = authentication)
  forks = forks + len(data.json())
  
  # contributors
  data = requests.get('https://api.github.com/repos/' + repo['full_name'] + '/contributors', auth = authentication)
  for contributor in data.json():
      if contributor['id'] not in contributors: 
         contributors.append(contributor['id'])

for milestone, issues in milestones.items(): 
   print("Processing Milestone " + milestone)
   msNumber = milestoneNumbers[milestone]
   print("Milestone # " + msNumber)
   generate_new_milestone(milestone, issues, msNumber)

with open('content/timeline/_index.md', 'a') as f:
  f.write('\n\n ## Some Cross-Project statistics')
  f.write('\n\nForks: ' + str(forks))
  f.write('\n\nMerged Pull Requests: ' + str(mergedprs))
  f.write('\n\nTotal number of unique followers: ' + str(len(stargazers)))
  f.write('\n\n ## Timeline')

with open('content/timeline/generated-contributor-total.md', 'w') as f:
    f.write('---\n')
    f.write('title: Total number of contributors\n')
    f.write('draft: false\n')
    f.write('type: "timeline"\n')
    f.write('date: ')
    f.write(str(datetime.datetime.now()))
    f.write('\n')
    f.write('---\n')
    f.write('\nWe have ')
    f.write(str(len(contributors)))
    f.write(' individuals contributing to Kaoto.\n\n')
    
