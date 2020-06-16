.PHONY: build
build:
	pyi-makespec --specpath=./spec -F -n drc-language-server \
		--exclude-module=Tkinter --exclude-module=pyi_rth__tkinter \
		main.py
	pyinstaller --distpath=./dist --workpath=./spec --clean -y ./spec/drc-language-server.spec