#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import os
import sys
import subprocess
import re
import shlex


# "environmentVariables": [
#    {
#      "name": "PROVIDER_HOSTNAME",
#      "value": "<ONEDATA_PROVIDER_IP>"
#    },
#    {
#      "name": "ONEDATA_TOKEN",
#      "value": "xxxxxxxx"
#    },
#    {
#      "name": "ONEDATA_SPACE",
#      "value": "<path>"
#    },
#    {
#      "name": "INPUT_FILENAME",
#      "value": "<input filename --> coincindes with amber-job-01 OUTPUT_FILENAME>"
#    },
#    {
#      "name": "OUTPUT_PROTOCOL",
#      "value": "http(s)|ftp(s)|S3|Swift|WebDav"
#    },
#    {
#      "name": "OUTPUT_URL",
#      "value": "<output URL>"
#    },
#    {
#      "name": "OUTPUT_CREDENTIALS",
#      "value": "{valid json}"
#    },
#    {
#      "name": "OUTPUT_PATH",
#      "value": "<path>" --> e.g. /<bucket-name>/<object-name>
#    }
#


allowed_protocols=['http', 'https', 'webdav', 'webdavs', 's3', 'swift+keystone']

import json

def str2json (s):
  #s = "{'muffin' : 'lolz', 'foo' : 'kitty'}"
  json_acceptable_string = s.replace("'", "\"")
  return json.loads(json_acceptable_string)


def run_command(cmd, env=None):
    """
    Execute the external command and get its exitcode, stdout and stderr.
    """
    args = shlex.split(cmd)
    print args
 
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    out, err = proc.communicate()
    exitcode = proc.returncode
    #
    return exitcode, out, err

class FileUploader(object):


    def __init__(self, filename, protocol, url, path, credentials):
           
        if os.path.isfile(filename):
           self.filename=filename
        else:
           raise ValueError('"%(path)s" is not a valid file.' % {'path': filename})

        self.url=url
        self.outpath=path
        
        self.protocol=protocol.lower()
        if self.protocol not in allowed_protocols:
           raise ValueError('Protocol not supported. Allowed protocols: %s' % allowed_protocols) 

        self.credentials=credentials

    def upload(self):

        if ( re.match('^(http|webdav)s?', self.protocol)  ):
           self._curlUpload();
           
        if ( self.protocol == 's3' ):
           self._s3Upload();

        if ( self.protocol == 'swift+keystone'):
           self._swiftUpload();
           

    def _curlUpload(self):
        creds = str2json(self.credentials)
        try:
          username=creds['USERNAME']
          password=creds['PASSWORD'] 
        except KeyError as e:
          print "Invalid credentials field: ", e
          sys.exit(1)
        
        cmd = "curl -k -u %s:%s -X PUT %s/%s -T %s" % (username, password, self.url, self.outpath, self.filename) 

        exitcode, out, err = run_command(cmd)
        print out
        print err
        sys.exit(exitcode)

        

    def _s3Upload(self):
        #aws --endpoint-url http://cloud.recas.ba.infn.it:8080/ s3 cp ./main.py s3://container/main.py        
        creds = str2json(self.credentials)
        try:
          accessKey=creds['AWS_ACCESS_KEY_ID']
          secret=creds['AWS_SECRET_ACCESS_KEY']
        except KeyError as e:
          print "Invalid credentials field ", e
          sys.exit(1)

        env = os.environ.copy() 
        env['AWS_ACCESS_KEY_ID']=accessKey
        env['AWS_SECRET_ACCESS_KEY']=secret

        path=self.outpath.strip('/')
        
        #outpath="container/tesfile.zip"
        cmd = "aws --no-verify-ssl --endpoint-url %s s3 cp %s s3://%s" % (self.url, self.filename, path)
       
        exitcode, out, err = run_command(cmd, env)
        print out
        print err
        sys.exit(exitcode)


    def _swiftUpload(self):
        creds = str2json(self.credentials)
        try:
          username=creds['USERNAME']
          password=creds['PASSWORD']
          tenant=creds['TENANT']
          authUrl=creds['AUTH_URL']
        except KeyError as e:
          print "Invalid credentials field ", e
          sys.exit(1)

        env = os.environ.copy()
        env['OS_USERNAME']=username
        env['OS_TENANT_NAME']=tenant
        env['OS_PASSWORD']=password
        env['OS_AUTH_URL']=authUrl

       # outpath="container/prova/tesfile.zip"
        path=self.outpath.strip('/')
        container, objectname = path.split("/",1)
        cmd = "swift --insecure upload %s %s --object-name %s" % (container, self.filename, objectname)

        exitcode, out, err = run_command(cmd, env)
        print out
        print err
        sys.exit(exitcode)
        



def main(args=None):
  try:
    filename=os.environ["INPUT_FILENAME"]
    protocol=os.environ["OUTPUT_PROTOCOL"]
    url=os.environ["OUTPUT_URL"]
    path=os.environ["OUTPUT_PATH"]
    credentials=os.environ["OUTPUT_CREDENTIALS"]

    fu=FileUploader(filename, protocol, url, path, credentials)
    fu.upload()

  except KeyError as e:
       print "Please set the environment variable ", e
       sys.exit(1)
  except ValueError as e:
       print "Invalid value: ", e
       sys.exit(1) 


if __name__ == '__main__':
    main()
