build_folder = cython_files

all: build docs

rebuild: clean build

build: 
	python setup.py build_ext --inplace
	mv build $(build_folder)/build

docs: 
	-mkdir $(build_folder)/docs
	-cython -a $(build_folder)/*.pyx
	-mv $(build_folder)/*.html $(build_folder)/docs

clean: 
	-rm -r $(build_folder)/build
	-rm -r $(build_folder)/docs
	-rm *.so
	-rm $(build_folder)/*.c
	-rm $(build_folder)/*.cpp
	
