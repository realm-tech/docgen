# docgen (OCR)

## Installation
The version of WeasyPrint must be 52.5. 
we plan to completley remove `genalog` which causing some serious problems
```bash
python3 -m pip install -r requirements.txt
```

## How to use:
"dataset_generator.py" is the main file. 


"texts/example.txt" is the input text. 
"outputs/" is the output folder. 
"templates/" is the folder to store templates in jinja2.
"images/" is the images folder to use in the template.
"fonts/" is the fonts folder. poupulate some fonts
run "dataset_generator.py".
