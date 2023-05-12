#!/usr/bin/python3

#  Copyright 2020-2023 Robert Bosch Car Multimedia GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ******************************************************************************
#
# File: git-tag.py
#
# Initialy created by Tran Duy Ngoan / Jan 2023
#
# This tool helps to tag git repos via REST APIs of git server.
#
# History:
# 
# Jan 2023:
#  - initial OSS version
#
# May 2023:
#  - add configurable information `infix_tag` for string to be inserted into tag
#  - implement commandline arguments verifications
# 
# ******************************************************************************

from abc import ABCMeta, abstractmethod
import requests
import urllib.parse
import json
from jsonschema import validate
import os
import argparse

VERSION = "0.1.0"
VERSION_DATE = "10.05.2023"

PREFIX_INTERMEDIATE_TAG = "dev/"
PREFIX_RELEASED_TAG = "rel/"

CONFIG_SCHEMA = {
   "type": "object",
   "properties": {
      "github": {
         "$ref": "#/$defs/git-server"
      },
      "gitlab": {
         "$ref": "#/$defs/git-server",
         "required" : ["base_url"]
      },
      "bitbucket": {
         "$ref": "#/$defs/git-server",
         "required" : ["base_url"]
      },
   },
   "$defs" : {
      "git-server" : {
         "type": "object",
         "properties" : {
            "project": {
               "type": "string"
            },
            "repos": {
               "type": "object"
            },
            "base_url": {
               "type" : "string"
            },
            "infix_tag": {
               "type" : "string"
            }
         },
         "required" : ["project", "repos"],
         "additionalProperties": False,
      }
   },
   "additionalProperties": False,
   "anyOf": [
      {"required": ["github"]},
      {"required": ["gitlab"]},
      {"required": ["bitbucket"]}
   ],
}

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
   def tag_api_url(self, tag_name=None, tag=True, ref=True):
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
         err_msg(f"not supported git server type '{git_type}'")

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

class Bitbucket(GitServer):
   
   _GIT_SERVER_TYPE = "bitbucket"

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

def __process_commandline():

   str_desc = """git-tag tool helps to tag git repos via REST APIs of git server.
Tool support 3 types of git server: Github, Gitlab and Bitbucket.
Due to security, the credentials (PAT: Personal Access Token) to access the 
repos should be set as environment variables: <git-server-type>_PAT (upper case).
E.g: GITHUB_PAT, GITLAB_PAT and BITBUCKET_PAT"""

   str_sample_config="""
Schema for config *.json file:
{
   "<repo-type>" : {
      "base_url" : "<base-git-server-url>",  //not require for Github
      "project"  : "<project-space>",
      "infix_tag": "<string-to-be-inserted-into-tag>",  // optional
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
      "base_url" : "https://gitlab.com",
      "project" : "robotframework-aio",
      "infix_tag": "aio/"  // 'rel/0.0.0.1' tag will be transformed to 'rel/aio/0.0.0.1'
      "repos"   : {
         "build": "", //tag will refer to latest commit on default branch
         "config": "09fa34e57cc09a227b68b11a4a89f6b2d52cec33"
      }
   }
}
   """

   cmdlineparser=argparse.ArgumentParser(prog="git-tag", description=str_desc,
                                         formatter_class=argparse.RawTextHelpFormatter)
   cmdlineparser.add_argument('-v', '--version', action='version', 
                              version=f'v{VERSION} ({VERSION_DATE})',
                              help='version of git-tag tool')
   cmdlineparser.add_argument('tag_name', type=str, 
                              help='tag name which is used for tagging repos.'+\
                              '\nE.g: rel/0.5.2.1.')
   cmdlineparser.add_argument('config_file', type=str,
                              help='config *.json file which contains the repos information.'+\
                              str_sample_config)
   return cmdlineparser.parse_args()

if __name__=="__main__":
   repo_conf = None

   args = __process_commandline()
   tag_name  = args.tag_name
   conf_file = args.config_file

   if (not tag_name.startswith(PREFIX_RELEASED_TAG)) and (not tag_name.startswith(PREFIX_INTERMEDIATE_TAG)):
      err_msg(f"Only tag with prefix '{PREFIX_RELEASED_TAG}' or '{PREFIX_INTERMEDIATE_TAG}' is allowed for tagging")

   with open(conf_file) as f:
      repo_conf = json.load(f)

   try:
      validate(repo_conf, CONFIG_SCHEMA)
   except Exception as reason:
      err_msg(f"Given config *.json file '{conf_file}' is not valid.\n{reason}")

   for git_type, repo_data in repo_conf.items():
      base_url = "https://api.github.com"
      PAT = None
      infix_tag = ""
      if 'infix_tag' in repo_data:
         infix_tag = repo_data['infix_tag']

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

         # Change tag name to <rel|dev>/<infix_tag>/<version> if configured
         # Inserted infix_tag string into tag due to information in config file
         released_tag = tag_name.replace(
                                 PREFIX_INTERMEDIATE_TAG, f"{PREFIX_INTERMEDIATE_TAG}{infix_tag}"
                                 ).replace(
                                 PREFIX_RELEASED_TAG, f"{PREFIX_RELEASED_TAG}{infix_tag}")

         git.tag(released_tag, commit_sha)