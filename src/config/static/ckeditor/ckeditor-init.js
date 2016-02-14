(function() {
  var djangoJQuery;
  if (typeof jQuery == 'undefined' && typeof django == 'undefined') {
    console.error('ERROR django-ckeditor missing jQuery. Set CKEDITOR_JQUERY_URL or provide jQuery in the template.');
  } else if (typeof django != 'undefined') {
    djangoJQuery = django.jQuery;
  }

  var $ = jQuery || djangoJQuery;
  $(function() {
    initialiseCKEditor();
    initialiseCKEditorInInlinedForms();

    function initialiseCKEditorInInlinedForms() {
      try {
        $(document).on("click", ".add-row a, .grp-add-handler", function () {
          initialiseCKEditor();
          return true;
        });
      } catch (e) {
        $(document).delegate(".add-row a, .grp-add-handler", "click",  function () {
          initialiseCKEditor();
          return true;
        });
      }
    }

    function initialiseCKEditor() {
      $('textarea[data-type=ckeditortype]').each(function(){
        if($(this).data('processed') == "0" && $(this).attr('id').indexOf('__prefix__') == -1){
          $(this).data('processed',"1");
          $($(this).data('external-plugin-resources')).each(function(){
              CKEDITOR.plugins.addExternal(this[0], this[1], this[2]);
          });
          CKEDITOR.replace($(this).attr('id'), $(this).data('config'));

          CKEDITOR.on('instanceReady', function(ev) {
                var jqScript = document.createElement('script');
                var bsScript = document.createElement('script');

                jqScript.src = 'https://code.jquery.com/jquery-2.2.0.min.js';
                bsScript.src = 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js';

                var editorHead = ev.editor.document.$.head;
                editorHead.appendChild(jqScript);
                editorHead.appendChild(bsScript);
            });

        }
      });
    }
  });
}());

