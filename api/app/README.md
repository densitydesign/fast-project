# API doc

## Requirements
- The app is based on Python Flask 
- Just type `pip install requirements.txt`
- I recommend to use a virtual env (https://virtualenv.pypa.io/en/stable/)

## Endpoints

- `/` or `/brands` -> List of brands
- `/posts/:brand_id` -> List of posts of `brand_id`
- `/posts/:brand_id/limit/n` -> List of n posts of `brand_id`

## Swagger docs

- Once the api is running, simply go to `/apidocs`
