#!/usr/bin/python3
from abc import ABCMeta, abstractmethod
import requests
import urllib.parse
import json
import sys
import os

PREFIX_INTERMEDIATE_TAG = "dev/"
PREFIX_RELEASED_TAG = "rel/"

USAGE = """Usage: git-tag.py <tag_name> <tag_repos.json>

git-tag tool helps to tag git repos via REST APIs of git server.
Currently, tool support 3 type of git server: Github, Gitlab and Socialcoding (Bitbucket).
Due to security, the credentials (PAT: Personal Access Token) to access the repos 
should be set as environment variables: <git-server-type>_PAT

positional arguments:
   <tag_name>         tag name which is used for tagging repos. E.g: rel/0.5.2.1.
   <tag_repos.json>   config *.json file which contains the repos information.

                      Schema for config *.json file:
                      {
                         "<repo-type>" : {
                            "base_url" : "<base-git-server-url>",  //not require for Github
                            "project"  : "<project-space>",
                            "repos"    : {
                               "<repo-name-1>" : "<sha-commit-for-reference>",
                               "<repo-name-2>" : "<sha-commit-for-reference>"
                               ...
                            }
                         }
                         ...
                      }
                      
                      Example:
                      {
                         "github" : {
                            "project" : "test-fullautomation",
                            "repos"   : {
                               "python-jsonpreprocessor": "85ac674b0de60629b8860acd6810bc7b679967ab",
                               "robotframework": "" //tag will refer to latest commit on default branch
                            }
                         },
                         "gitlab" : {
                            "base_url" : "https://gitlab-apertispro.boschdevcloud.com",
                            "project" : "robotframework-aio/main",
                            "repos"   : {
                               "ci-mirroring": "", //tag will refer to latest commit on default branch
                               "config": "09fa34e57cc09a227b68b11a4a89f6b2d52cec33"
                            }
                         }
                      }
"""

def log_msg(msg=""):
   print(msg)

def err_msg(msg, fatal=True):
   log_msg(f">>> ERROR: {msg}")
   if fatal:
      exit(1)

class GitServer(object):
   __metaclass__ = ABCMeta
   _GIT_SERVER_TYPE = "NotSupported"

   def __init__(self, repo, project, PAT, base_url):
      self.url     = base_url
      self.project = project
      self.repo    = repo
      self.PAT     = PAT
      
      if not self.PAT:
         err_msg(f"No provided {self._GIT_SERVER_TYPE.upper()}_PAT")
      self.token_type = "Bearer"

   @staticmethod
   def encode_url(param):
      return urllib.parse.quote_plus(param)

   @property
   def request_header(self):
      return {
         "Content-Type"  : "application/json",
         "Accept"        : "application/json",
         "Authorization" : f"{self.token_type} {self.PAT}"
      }

   @property
   @abstractmethod
   def repo_api_url(self):
      return ""

   @property
   @abstractmethod
   def default_branch(self):
      return ""

   @abstractmethod
   def tag_api_url(self):
      pass

   @abstractmethod
   def _tag_payload(self, tag_name, sha, ref=True):
      return None

   @abstractmethod
   def _commit_sha_from_reponse(self, res_data):
      return None

   def _tag_message(self, tag_name):
      if tag_name.startswith(PREFIX_INTERMEDIATE_TAG):
         return f"intermediate version {tag_name.replace(PREFIX_INTERMEDIATE_TAG, '')}"
      elif tag_name.startswith(PREFIX_RELEASED_TAG):
         return f"released version {tag_name.replace(PREFIX_RELEASED_TAG, '')}"
      
      return ""

   def _successful_get_request(self, url):
      res = self._get_request(url)
      
      if res.status_code == 200:
         return True
      return False

   def is_existing_repo(self):
      return self._successful_get_request(self.repo_api_url)

   def is_existing_tag(self, tag_name):
      return self._successful_get_request(self.tag_api_url(tag_name))

   def _get_request(self, url):
      return requests.get(url, headers=self.request_header)

   def _post_request(self, url, json_data):
      return requests.post(url, json=json_data, headers=self.request_header)

   def _create_tag_obj(self, tag_name, sha):
      # This method is only overwritten by the implementation of Github class
      # otherwise return the commit sha
      return sha

   def _create_tag_ref(self, tag_name, sha):
      res = self._post_request(self.tag_api_url(tag_name=None, tag=False), 
                               self._tag_payload(tag_name, sha, ref=True))

      if (res.status_code == 201) or (res.status_code == 200):
         log_msg("create tag reference successfully")
      else:
         err_msg(res.text)

   def _reference_to_tag(self):
      return self.latest_commit_sha()

   def latest_commit_sha(self):
      res = self._get_request(f"{self.repo_api_url}/commits/{self.default_branch}")
      
      if res.status_code == 200:
         return self._commit_sha_from_reponse(res.text)
      else:
         err_msg(res.text)

   def tag(self, tag_name, sha):
      if not sha:
         sha = self._reference_to_tag()
         # print(f"debug: {sha}")
      
      log_msg(f"{self._GIT_SERVER_TYPE}.{self.repo}: creating new tag {tag_name}")
      ref_sha = self._create_tag_obj(tag_name, sha)
      self._create_tag_ref(tag_name, ref_sha)

class GitCommand(object):
   def __init__(self, git_type, *args, **kwargv):
      self.git_services = self._get_support_git()

      if git_type in self.git_services.keys():
         self.git_service = self.git_services[git_type](*args, **kwargv)
      else:
         err_msg(f"not supported git type '{git_type}'")

      if not self.git_service.is_existing_repo():
         err_msg(f"not existing repo '{git_type}.{self.git_service.repo}'")

   def _get_support_git(self):
      return {cls._GIT_SERVER_TYPE : cls for cls in GitServer.__subclasses__()}

   def tag(self, tag_name, sha=None):
      if self.git_service.is_existing_tag(tag_name):
         print(f"Tag {tag_name} is already existing on {self.git_service.repo}")
      else:
         # log_msg(f"Create new tag for {tag_name}")
         self.git_service.tag(tag_name, sha)

class Github(GitServer):
   
   _GIT_SERVER_TYPE = "github"

   def __init__(self, repo, project, PAT, base_url):
      super().__init__(repo, project, PAT, base_url)

      self.token_type = "token"

   @property
   def repo_api_url(self):
      return f"{self.url}/repos/{self.project}/{self.repo}"

   @property
   def default_branch(self):
      res = self._get_request(self.repo_api_url)
      
      if res.status_code == 200:
         return json.loads(res.text)['default_branch']
      else:
         err_msg(res.text)

   def _commit_sha_from_reponse(self, res_data):
      return json.loads(res_data)['sha']

   def tag_api_url(self, tag_name=None, tag=True, ref=True):
      url = self.repo_api_url+"/git"
      if ref:
         url += "/refs"
      if tag:
         url += "/tags"
      if tag_name:
         url += f"/{self.encode_url(tag_name)}"

      return url

   def _tag_payload(self, tag_name, sha, ref=False):
      # payload for create tag object
      if ref:
         return {
            "ref" : f"refs/tags/{tag_name}",
            "sha" : sha
         }
      else:
      # payload for create tag reference
         return {
            "tag"     : tag_name,
            "message" : self._tag_message(tag_name),
            "object"  : sha,
            "type"    : "commit"
         }
   
   def _create_tag_obj(self, tag_name, sha):
      # Github requires to create the tag object 
      # then create the refs/tags/[tag] reference for above tag object
      res = self._post_request(self.tag_api_url(tag_name=None, ref=False), 
                         self._tag_payload(tag_name, sha, ref=False))

      if res.status_code == 201:
         log_msg("create tag object successfully")
      else:
         err_msg(res.text)
      return json.loads(res.text)['sha']

class Gitlab(GitServer):
   
   _GIT_SERVER_TYPE = "gitlab"

   def __init__(self, repo, project, PAT, base_url):
      super().__init__(repo, project, PAT, base_url)

      self.repo_id = self.encode_url(f"{self.project}/{self.repo}")

   @property
   def repo_api_url(self):
      return f"{self.url}/api/v4/projects/{self.repo_id}/repository/tree"

   @property
   def default_branch(self):
      res = self._get_request(f"{self.repo_api_url[:-5]}/branches")
      
      if res.status_code == 200:
         branches = json.loads(res.text)
         for branch in branches:
            if branch['default']:
               return branch['name']
      else:
         err_msg(res.text)

   def _commit_sha_from_reponse(self, res_data):
      return None

   def tag_api_url(self, tag_name=None, tag=True, ref=True):
      url = f"{self.repo_api_url[:-5]}/tags"
      if tag_name:
         url += f"/{self.encode_url(tag_name)}"
      return url

   def _tag_payload(self, tag_name, sha, ref=False):
      return {
         "tag_name" : tag_name,
         "ref"      : sha,
         "message"  : self._tag_message(tag_name)
      }

   def _reference_to_tag(self):
      return self.default_branch

class Socialcoding(GitServer):
   
   _GIT_SERVER_TYPE = "socialcoding"

   def __init__(self, repo, project, PAT, base_url):
      super().__init__(repo, project, PAT, base_url)

      self.is_personal_repo = False

   @property
   def repo_api_url(self):
      if self.is_personal_repo:
         return f"{self.url}/rest/api/1.0/users/{self.project}/repos/{self.repo}"
      else:
         return f"{self.url}/rest/api/1.0/projects/{self.project}/repos/{self.repo}"

   @property
   def default_branch(self):
      res = self._get_request(f"{self.repo_api_url}/branches/default")
      
      if res.status_code == 200:
         return json.loads(res.text)['displayId']
      else:
         err_msg(res.text)

   def tag_api_url(self, tag_name=None, tag=True, ref=True):
      url = f"{self.repo_api_url}/tags"
      if tag_name:
         url += f"/{tag_name}"
      return url

   def _tag_payload(self, tag_name, sha, ref=False):
      return {
         "name"       : tag_name,
         "startPoint" : sha,
         "message"    : self._tag_message(tag_name)
      }

   def _commit_sha_from_reponse(self, res_data):
      return json.loads(res_data)['id']

if __name__=="__main__":
   # repo_conf = {
   #    'github' : {
   #       'robotframework-testresultwebapptool': '',
   #       'robotframework-testresult2rqmtool': '90c3306952c0839bb7a008e1295ca72899ca347a'
   #    },
   #    'gitlab': {
   #       'build' : 'f3f7f56b3f5b8be3d8809a7ae6e4bd5b078746f0',
   #    },
   #    'socialcoding': {
   #       'export2gitlab' : '',
   #    }
   # }

   repo_conf = dict()

   if len(sys.argv) < 3:
      err_msg(f"Please provide tag-name and config *.json file.\n{USAGE}")
   tag_name=sys.argv[1]
   conf_file=sys.argv[2]

   # tag_name="rel/0.1.0.10"
   # conf_file="C:/MyData/4.RobotFramework/Robot-ws/My_repos/build/config/repositories/tag_repos.json"

   with open(conf_file) as f:
      repo_conf = json.load(f)

   # print(repo_conf)

   for git_type, repo_data in repo_conf.items():
      base_url = "https://api.github.com"
      PAT = None

      try:
         PAT = os.environ[f"{git_type.upper()}_PAT"]
      except Exception:
         err_msg(f"There is no environment variable ({git_type.upper()}_PAT) for Personal Access Token")

      if 'base_url' not in repo_data:
         if git_type != 'github':
            err_msg("'base_url' should be provided for git server other than Github.")
      else:
         base_url = repo_data['base_url']

      if not repo_data['project']:
         err_msg("'project' should be provided in the configuration *.json file.")

      for repo, commit_sha in repo_data["repos"].items():
         git = GitCommand(git_type, repo=repo, project=repo_data['project'], 
                          PAT=PAT, base_url=base_url)

         released_tag = tag_name
         # change tag name to <rel|dev>/aio/<version> for other than gitlab repos
         if git_type != "gitlab":
            released_tag = tag_name.replace(
                                             PREFIX_INTERMEDIATE_TAG, f"{PREFIX_INTERMEDIATE_TAG}aio/"
                                           ).replace(
                                             PREFIX_RELEASED_TAG, f"{PREFIX_RELEASED_TAG}aio/")

         git.tag(released_tag, commit_sha)