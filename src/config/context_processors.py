import os


def version_tag(request):
    return {
        'version': os.environ.get('RELEASE_TAG', '1'),
    }
