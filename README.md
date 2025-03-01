# team-70-project: Wikipedle

## Creating and using a Python virtual environment (for Windows) in the backend
```
python -m venv .venv
```

```
.\.venv\Scripts\activate
```

### Install python dependencies using requirements.txt (inside .venv)
```
py -m pip install <path to requirements.txt>
```

## Optional to manually configure .venv:

### Manually install Django in .venv:
```
py -m pip install Django
```
### Manually install Pep8 in .venv:
```
py -m pip install pep8
```

### Manually install spaCy in .venv:
```
py -m pip install spacy
```

## Configuring Node.js Tools in the frontend (separate from .venv)
* --save-dev flag means that it is a development dependency only

### React:
npm install react react-dom

### ESlint:
npm install eslint --save-dev

### Jest:
npm install jest --save-dev

### SQLite:

