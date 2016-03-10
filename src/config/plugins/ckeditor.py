CKEDITOR_CONFIGS = {

    'default': {
        'allowedContent': True,
        'contentsCss': '/static/bower_components/bootstrap/dist/css/bootstrap.min.css',
        'skin': 'office2013',
        'toolbar_DSTACKToolbarConfig': [

            {'name': 'tools', 'items': ['Maximize', ]},
            {'name': 'document', 'items': ['Source', '-', 'Save', 'NewPage', 'Preview', 'Print', '-', 'Templates', ]},
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},

            '/',  # put this to force next toolbar on new line

            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter',
             'JustifyRight', 'JustifyBlock'],
            ['RemoveFormat', ],

            '/',  # put this to force next toolbar on new line

            {'name': 'forms', 'items': [
                'Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton', 'HiddenField',
            ]},
            {'name': 'links', 'items': ['-', 'Link', 'Unlink', 'Anchor']},
            {'name': 'insert', 'items': ['-', 'Image', 'Table', 'HorizontalRule', 'Iframe', 'Simplebox', 'Bstabs']},

        ],

        'toolbar': 'DSTACKToolbarConfig',  # put selected toolbar config here
        'toolbarCanCollapse': True,
        'tabSpaces': 4,

        'extraPlugins': ','.join(
            [
                'templates',
                'dialog',
                'dialogui',
                'widget',
                'div',
                'clipboard',
                'lineutils',
                'autolink',
                # 'autoembed',
                # 'embedsemantic',
                'autogrow',
                # 'devtools',
                'elementspath',
                'simplebox',
                'bstabs',
                'codemirror',
            ]),

        'removePlugins': 'stylesheetparser',

        'width': "1200px",
    }
}

# CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = 'pillow'
