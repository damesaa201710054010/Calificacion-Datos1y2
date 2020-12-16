# Monitoria Datos - EAFIT

## Instrucciones de uso

- Antes de ejecuccion se debe actualizar el archivo con los datos de los estudiantes y ponerlo en la carpeta `Grading_Environment`

- Ejeuctamos `main.py`, seguimos las instrucciones del programa, segun la opcion descargara (y actualizara) los repositorios, luego se escoge la actividad a calificar (En la presente version solo califica talleres y entregas 1 y 2)

- Una vez calificada la actividad, se deben de actualizar las key de las hojas de calculo en `update_grades.py`, luego ejecutamos `update_grades.py` nos pedira nuevamente los datos del grupo y actividad, este programa actualizara la hoja de Google por lo tanto nos pedira ir al navegador y dar permiso desde la cuenta de Google que tiene acceso a la hoja de calculo, una vez damos los permisos el programa terminara de ejecutarse y mostrara en pantalla el numero de celdas actualizadas

Notas: no se deben de modificar otras carpetas, solo las que estan en `Grading_Environment`, las versiones de los programas fueron actualizadas, y ejecutan con python 3 sin problemas

## Dependencias

- Python (version 3.x).
- Calibre.