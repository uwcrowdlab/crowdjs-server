crowdjs-server
==============

## Development configuration
- Download and install miniconda. http://conda.pydata.org/miniconda.html
- Create a conda environment. `conda create --name crowdjs python pip`
- Activate the conda environment. `source activate crowdjs`
- Load application dependencies by running `pip install -r requirements.txt`
- Install scipy. `conda install nomkl scipy`
- This repository contains git submodules. Run `git submodule init` and `git submodule update` to fetch these.
- Set up a MongoDB database. One option is to create a free Heroku instance with a MongoLab sandbox add-on.
- Install [zmdp](https://github.com/trey0/zmdp) as a submodule (see ZMDP readme for build instructions).
- Create a `.env` file in the root directory with the following lines (substitute `db_user`, `db_password`, `host`, and `port` with details of your development MongoDB connection; and substitute `zmdp` with the alias or location of the ZMDP solver. REQUEUE_INTERVAL is the number of seconds before the server will reassign abandoned questions.
```
MONGOLAB_URI=mongodb://db_user:db_password@host:port
APP_SETTINGS='config.DevelopmentConfig'
ZMDP_ALIAS=zmdp # or ./zmdp/bin/<os_name>/zmdp
REQUEUE_INTERVAL=600
```
- Create a production version `.production-env` that uses the production configuration. **This file should not include the details of your production database connections.**
```
APP_SETTINGS='config.Production'
```
- Set up a Redis instance. For Heroku, follow the instructions on https://devcenter.heroku.com/articles/heroku-redis
In your `.env` file, add:
```
REDIS_URL=redis://user:password@host:port
```

## Additional configuration
To set up Heroku, add the following buildpacks, using the toolbelt command `heroku buildpacks:add`:

2. https://github.com/uwcrowdlab/heroku-buildpack-zmdp.git
3. https://github.com/kennethreitz/conda-buildpack.git

## Run instructions
- Run the application using either `heroku local` (if using Heroku) or `./run.sh .env -b host:port`. Use the second option if you would like to see exceptions. 

## Documentation
Take a look at the `make_docs` script in the root directory. The documentation page will be saved to `docs/_build/html/index.html`

## Testing instructions
- **DO NOT RUN UNIT TESTS ON YOUR PRODUCTION DATABASE!!! IT WILL BE CLEARED!!!**
- Use `heroku local -f Procfile.test` (if using Heroku) or
- Be sure to run both `./run_tests.sh .env` AND `./run_tests.sh .production-env` to test both dev and production environments.
- The `test/` folder also contains folders with more tests that include end-to-end workflow tests as well as more unit tests. To run these, read the README inside the desired `*_workflow/` folder.

## Usage
- First, create an account and login by going to `server_url/register` and `server_url/login`. You will receive an API Token as well as a requester_id.
- Next, make a PUT request to `server_url/tasks` to insert your task (consisting of 1 or more questions) into the database. This step requires your credentials.
- To query the next question a worker should answer, make a GET request to `server_url/assign_next_question`.
- To insert an answer into the database, make a PUT request to `server_url/answers`.
- See the documentation for more details about how to make the requests.

