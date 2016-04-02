import os

# Check if debug variable is there to determine whether loaded
env_vars_loaded = os.environ.get('DEBUG', '')

# fallback for when env variables are not loaded:
if not env_vars_loaded:
    try:
        print('Loading keys from file...')
        current_directory = os.path.dirname(__file__)
        parent_directory = os.path.split(current_directory)[0]
        parent_directory = os.path.split(parent_directory)[0]
        parent_directory = os.path.split(parent_directory)[0]

        file_path = os.path.join(parent_directory, '.env_local')
        with open(file_path, 'r') as f:
            output = f.read()
            output = output.split('\n')

        for var in output:
            k, v = var.split('=', maxsplit=1)

            os.environ.setdefault(k, v)
    except FileNotFoundError:
        print('environmental variables file not found')
        pass

# config
DEBUG = os.environ.get('SECRET_KEY', 'kjmYm9VFG~vC47dh[OwYwCpnEA#}L#+yBUVQm6#GcrBJYfhz$jB|W)zyb=MM%">')


# secrets
SECRET_KEY = os.environ.get('SECRET_KEY', 'kjmYm9VFG~vC47dh[OwYwCpnEA#}L#+yBUVQm6#GcrBJYfhz$jB|W)zyb=MM%">')

