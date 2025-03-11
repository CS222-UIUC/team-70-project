# team-70-project: Wikipedle

## Setting up Dependencies

Tech Stack:
* React for Frontend
* Django for Backend
* SQLite for Database

## Creating and using a Python virtual environment (for Windows) in the backend
```
python -m venv .venv
```

```
.\.venv\Scripts\activate
```

### Install python dependencies using requirements.txt (inside .venv in backend folder)
```
py -m pip install <path to requirements.txt>
```

*If you make changes to the environment dependencies, please use:

```
pip freeze > requirements.txt
```

To snapshot your requirements and push to git.

## Optional to manually configure .venv:

### Manually install Django in .venv:
```
py -m pip install Django
```

### Manually install Django AllAuth in .venv:
```
py -m pip install django-allauth
```

### Manually install Pep8 in .venv:
```
py -m pip install pep8
```

### Manually install spaCy in .venv:
```
py -m pip install spacy
```

### SQLite:

Django has built-in support for SQLite by default

## Configuring Node.js Tools in the frontend (in frontend folder separate from .venv)
* --save-dev flag means that it is a development dependency only

### React:
npm install react react-dom

### ESlint:
npm install eslint --save-dev

npm init @eslint/config@latest

### Husky:
Husky is a package for automating eslint for github commits

npm install husky --save-dev

### Jest:
npm install jest --save-dev


