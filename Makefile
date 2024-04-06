test:
	bash ./test.sh
run:
	python3.10 parse.py
.PHONY: test

pack:
	rm -f xnguye28.zip
	rm -fr lexer/__pycache__ parser/__pycache__ common/__pycache__
	zip -r xnguye28.zip parser lexer common parse.py readme1.md readme1.pdf doc_imgs rozsireni
