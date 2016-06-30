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


allowed_protocols=['http', 'https', 'webdav', 'webdavs', 's3', 'swift+keystone']


def run_command(cmd, env=None):
    """
    Execute the external command and get its exitcode, stdout and stderr.
    """
    args = shlex.split(cmd)

    if "DEBUG" in os.environ:
       print args
    
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    out, err = proc.communicate()
    exitcode = proc.returncode
    #
    if exitcode != 0:
       raise RuntimeError("Command failed with exit code %s. %s" % (exitcode, err))
    
    return out

###
# Class FileUploader implements functions for uploading files to
# - http(s), webdav(s)
# - swift+keystone
# - s3
# using proper user credentials
###
class FileUploader(object):


    def __init__(self):
        
        #read mandatory env variables
        self.path=os.environ["UPLOAD_DIR"]
        self.filenames=os.environ["OUTPUT_FILENAMES"].split(",")
        self.protocol=os.environ["OUTPUT_PROTOCOL"].lower()
        self.url=os.environ["OUTPUT_ENDPOINT"]
        self.outpath=os.environ["OUTPUT_PATH"]
        self.username=os.environ["OUTPUT_USERNAME"]
        self.password=os.environ["OUTPUT_PASSWORD"]
        
        #read optional env variables
        try:
          self.tenant=os.environ["OUTPUT_TENANT"]
        except KeyError as e:
          self.tenant = ""
        try:
          self.region=os.environ["OUTPUT_REGION"]
        except KeyError as e:
          self.region = ""

        # check file existence        
        for filename in self.filenames:
           if not os.path.isfile(self.path+filename):
              raise ValueError('"%(path)s" is not a valid file.' % {'path': self.path+filename})

        # check supported protocol
        if self.protocol not in allowed_protocols:
           raise ValueError('Protocol not supported. Allowed protocols: %s' % allowed_protocols) 

    # call the proper upload method depending on the protocol
    def main(self):

        if ( re.match('^(http|webdav)s?', self.protocol)  ):
           self._httpUpload();
           
        if ( self.protocol == 's3' ):
           self._s3Upload();

        if ( self.protocol == 'swift+keystone'):
           self._swiftUpload();
           
    # method for uploading using web protocols (http/webdav)
    def _httpUpload(self):
        
        for filename in self.filenames:
            print "[INFO] Uploading File %s" % self.path+filename
            cmd = "curl -k -u %s:%s --write-out %%{http_code} --silent --output /dev/null -X PUT %s/%s/%s -T %s" % (self.username, self.password, self.url, self.outpath, filename, self.path+filename) 
            out = run_command(cmd)
           
            if out[0:2] != '20':
               raise RuntimeError("Upload failed with HTTP code %s" % out)
               

    # method for uploading using S3 protocol    
    def _s3Upload(self):
        #aws --endpoint-url http://cloud.recas.ba.infn.it:8080/ s3 cp ./main.py s3://container/main.py        
        #aws --endpoint-url https://s3.amazonaws.com --region us-east-1 s3 cp ./main.py s3://container/main.py

        env = os.environ.copy() 
        env['AWS_ACCESS_KEY_ID']=self.username
        env['AWS_SECRET_ACCESS_KEY']=self.password
        
        options=""
        if self.region != "":
           options = "--region " + self.region
        
        bucket=self.outpath.strip('/')
        
        for filename in self.filenames:
           print "[INFO] Uploading File %s" % self.path+filename
           cmd = "aws --no-verify-ssl --endpoint-url %s %s s3 cp %s s3://%s/%s" % (self.url, options, self.path+filename, bucket, filename)
           out = run_command(cmd, env)
           print out


    # method for uploading using Swift protocol
    def _swiftUpload(self):

        env = os.environ.copy()
        env['OS_USERNAME']=self.username
        env['OS_PASSWORD']=self.password
        env['OS_AUTH_URL']=self.url
        
        if self.tenant != "":
           env['OS_TENANT_NAME']=self.tenant
        if self.region != "":
           env['OS_REGION_NAME']=self.region

        container=self.outpath.strip('/')
        
        for filename in self.filenames:
           print "[INFO] Uploading File %s to container %s with object name %s" % (self.path+filename, container, filename)
           cmd = "swift --insecure upload %s %s --object-name %s" % (container, self.path+filename, filename)
           out = run_command(cmd, env)
           print out 

def main(args=None):
  try:

    FileUploader().main()
    print "Data upload ENDED successfully!"

  except KeyError as e:
       print "[ERROR] Please set the environment variable ", e
       sys.exit(1)
  except ValueError as e:
       print "[ERROR] Invalid value: ", e
       sys.exit(1) 
  except RuntimeError as e:
       print "[ERROR] ", e
       sys.exit(1)
  except:
       print "Unexpected error:", sys.exc_info()[0]
       raise


if __name__ == '__main__':
    main()
