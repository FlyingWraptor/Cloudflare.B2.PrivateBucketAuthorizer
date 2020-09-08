# Cloudflare.B2.PrivateBucketAuthorizer
Simple script to automatically update a cloudflare worker with a new download authorization code

## Schedule to run
```bash
crontab -e

*Enter:
0 0 */3 * * /bin/python /path/to/run.py

*Save
```


## Configuration
1. Copy and rename the config_example.json to config.json
2. Fill in the credentials


## Response additions
To modify the response from the worker you can create a file "response_additions.js" and write code to be executed right before returning the response (where the '//<\<ResponseAdditions\>>' lives in worker.js).