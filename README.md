<!--
<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://i.imgur.com/6wj0hh6.jpg" alt="Project logo"></a>
</p>
-->

<h3 align="center">Cinema web app</h3>

<div align="center">

  ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/jackroi/cinema-web-app/vm-tests?style=for-the-badge)
  [![GitHub last commit](https://img.shields.io/github/last-commit/jackroi/cinema-web-app?style=for-the-badge)](https://github.com/jackroi/cinema-web-app/commits/master)
  [![GitHub issues](https://img.shields.io/github/issues/jackroi/cinema-web-app?style=for-the-badge)](https://github.com/jackroi/cinema-web-app/issues)
  [![GitHub pull requests](https://img.shields.io/github/issues-pr/jackroi/cinema-web-app?style=for-the-badge)](https://github.com/jackroi/cinema-web-app/pulls)
  [![GitHub](https://img.shields.io/github/license/jackroi/cinema-web-app?style=for-the-badge)](/LICENSE)

</div>

---

<p align="center">
  Simple flask web app for a cinema
  <br>
</p>

## 📝 Table of Contents
- [About](#about)
- [Getting Started](#getting_started)
<!-- - [Deployment](#deployment) -->
- [Usage](#usage)
- [Built Using](#built_using)
- [TODO](./TODO.md)
- [Authors](#authors)
- [Acknowledgments](#acknowledgement)

## 🧐 About <a name = "about"></a>
Write about 1-2 paragraphs describing the purpose of your project.
Simple web app for a cinema. The web app is built using Flask, and interfaces with a Postgres database.
<br>
Documentation (italian language):
- [Project specifications](./docs/project-specifications.pdf)
- [Project documentation](./docs/project-documentation.pdf)

This project was realized for the Database course of Ca' Foscari University of Venice.
<br>
Note: the code is abundantly commented as required by the project specifications, and for future reference.

## 🏁 Getting Started <a name = "getting_started"></a>
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.
You can run the web app using Docker (recommended) or installing python and postgresql on your machine.

### With Docker
#### Prerequisites
- [Docker](https://www.docker.com/)

#### Installing
A step by step series of examples that tell you how to get a development env running.

1. Clone the repository:
```
git clone ...
cd cinema-web-app
```

2. Create `.env` file and complete the missing fields (in particular, select the passwords)
```bash
mv instance/.env.example .env
nano instance/.env
```

3. Build the docker image:
```bash
# Linux
./scripts/build-cinema-app-image.sh
# Windows
.\scripts\windows\build-cinema-app-image.bat
```

4. Launch the web app:
```bash
# Linux
./scripts/launch-all.sh
# Windows
.\scripts\windows\launch-all.bat
```

### Without Docker
TODO


End with an example of getting some data out of the system or using it for a little demo.



## 🔧 Running the tests <a name = "tests"></a>
Explain how to run the automated tests for this system.

### Break down into end to end tests
Explain what these tests test and why

```
Give an example
```

### And coding style tests
Explain what these tests test and why

```
Give an example
```

## 🎈 Usage <a name="usage"></a>
Add notes about how to use the system.

## 🚀 Deployment <a name = "deployment"></a>
Add additional notes about how to deploy this on a live system.

## ⛏️ Built Using <a name = "built_using"></a>
- [Python](https://www.python.org/) - Server Environment
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [PostgreSQL](https://www.postgresql.org/) - Database
- [Docker](https://www.docker.com/) - Container

## ✍️ Authors <a name = "authors"></a>
- [@davidguid](https://github.com/davidguid) - Implementation
- [@jackroi](https://github.com/jackroi) - Implementation

## 🎉 Acknowledgements <a name = "acknowledgement"></a>
- Database course professor for the project idea and specifications.
