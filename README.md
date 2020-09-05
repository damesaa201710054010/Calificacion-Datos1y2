# Monitoria Datos - EAFIT

Repository holding all the tools used by the teachers and teaching assistants of the Data Structures and Algorithms class at EAFIT University.

## Usage

After cloning the repository to your own machine, run the `build_grading_env.sh` script. That will create the *Grading_Environment* directory, in which all the grading tools will be located. Make sure that the *UsuarioGitPreexistentes.csv* file is in your *Grading_Environment* folder (if not, then out it there yourself).

- To download the student's repositories, run the `Grading_Environment/git-downloader.py` script (with python 2.7). That will put every repo inside the *Trabajos20xx-x* directory.

- To grade the activities, run the `Grading_Environment/git-calificador.py` script (with python 2.7). That will update the *Talleres.csv* and *Proyecto.csv* files.

- To update the remote google drive grades, run the `Grading_Environment/update_grades.py` script (with python 3), with the course, group and number of the activity to be updated, as arguments. (e.g. python3 update_grades.py ed1 33 6). **FIRST TIME RUNNING THIS SCRIPT:** if you are running the script for the first time, you will be promted to authorize it to access the spreadsheets on your google account. Please, sign in to your google account, click *advanced* and then click *go to quickstart*. **Trust me, nothing bad will happen, you can read the source code if you don't believe me**. After you do this the first time, you won't have to do it again.

Please **DO NOT CHANGE** anything **OUTSIDE** the *Grading_Environment* directory unless you are developing a new tool or changing an existing one.

## Dependencies

- Python (version 2.7 and version 3.x).
- Calibre.