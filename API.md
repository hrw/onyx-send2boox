# Table of API calls (incomplete)

Each call starts with "/api/1/".


 name                      | method | present in code? | description
---------------------------|--------|------------------|-------------
cloud/docs/by/recently     |  GET   |    no    |
cloud/pc/docs/struct       |  GET   |    no    |
config/buckets             |  GET   |    yes   | get cloud information
config/stss                |  GET   |    yes   | get cloud access keys and security token
im/getSig                  |  GET   |    yes   | no idea
push/message               |  GET   |    yes   | get list of files in BooxDrop service
push/message               |  GET   |    yes   | get list of screensavers (with extra "sourceType": 100 argument)
push/message/batchDelete   |  POST  |    no    | mass remove of files (by their ids)
push/rePush/bat            |  POST  |    no    | force push file again to e-reader
push/saveAndPush           |  POST  |    yes   | send file
users/getDevice            |  GET   |    yes   | get device information
users/me                   |  GET   |    yes   | get account information
users/sendMobileCode       |  GET   |    yes   | request verification code
users/signupByPhoneOrEmail |  POST  |    yes   | login to service
users/syncToken            |  GET   |    no    |
webpage/bat/del            |  POST  |    no    | remove webpages from list
webpage/list               |  GET   |    no    | get list of stored webpage URLs
webpage/url                |  POST  |    no    | send webpage URL (for PushRead app)
writeTemplates             |  GET   |    no    |
