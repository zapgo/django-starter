fab_create:
	conda env create -f etc/fab_environment.yml;

fab_update:
	conda env update -f etc/fab_environment.yml;

fab:
	@if make fab_create; then\
        echo "Fabric environment created";\
    else\
    	make fab_update;\
    	echo "Fabric environment updated";\
    fi
