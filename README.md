# Sidewinder
Sidewinder is the Snakeroom’s new permanent backend.

It’s got all the useful features that we need every year built-in, and is extended as required for each year’s event.

## Development
```sh
# Setting up the environment
virtualenv env/
source env/bin/activate
pip install -r requirements.txt

# Set this environ.
export DJANGO_SETTINGS_MODULE=config.development
```