Fantasy Cricket
local development branch for redesigning the lambda frontend 
to work in a distributed architecture. 
eventually this will be deployed in aws prod 

to launch a new zappa deployment: 
1) activate virtual env 
2) install zappa inside it (pip install zappa) 
2.1) pip install -r requirements.txt 
3) zappa init  
4) modify the zappa_settings.json to include python3.7 
5) zappa deploy dev 
this will fail. 
go to aws console and add the environment variables manually 
6) zappa udpate dev 
this should work.  


===== to update code/ deployment ==== 
1. make sure zappa is installed via pip
2. run `zappa update dev` 
