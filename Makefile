build: build-slides build-demos

build-slides:
	quarto render .

build-demos:
	python _demos.py build

serve:
	python -m http.server --directory _build 9898

# make serve-file FILE=slides/3_feature-based/ice.qmd
serve-file:
	quarto preview $(FILE) --no-watch-inputs --no-browser --port 5303

serve-file-reload:
	quarto preview $(FILE) --no-browser --port 5303

clean-demos:
	python _demos.py clean

quarto-setup:
	quarto install extension quarto-ext/fontawesome
