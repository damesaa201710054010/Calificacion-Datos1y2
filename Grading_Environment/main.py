import downloader
import calificador

#Datos necesarios
semestreActual = ""
lineaInicial = ""
curso=""
numGrup = 0
grupos = []



respuesta = ""
print("Descargar repositorios (si|no): ")
respuesta: input()


def download():
    usuarios = downloader.processCSV()
    downloader.download(usuarios)

def update():
   
    trabajos = calificador.trabajos
    calificador.semestre = semestreActual
    usuarios  = calificador.actualizarGits(trabajos, False)
    print("Digiste t para talleres, l para laboratorios o p para el proyecto:")
    respuesta = input()
    if respuesta == "t":
        calificador.calificarTalleres(trabajos, usuarios)
    elif respuesta == "l":
        calificador.calificarLabs(trabajos, usuarios, semestreActual)
    elif respuesta == "p":
        print("Digite 1 o 2 segun la entrega: ")
        respuesta = int(input())
        calificador.calificarProyectos(trabajos, respuesta , usuarios, semestreActual)
    else:
        print("Ninguna opcion coincide")


if respuesta == "si" or respuesta == "SI":
    print("Semestre Actual (ejemplo: 2017-2):")
    semestreActual = input()
    print("linea en el archivo csv para el semestre(de acuerdo al CSV descargado): ")
    lineaInicial = input()
    print("¿Que curso es?")
    curso = input()
    print("¿Cuantos grupos?")
    numGrup = int(input())
    print("Ingrese los grupos en orden (menor a mayor(033, 034, etc)):")
    for i in range(numGrup):
         grupos.append(input())
    downloader.semestre = semestreActual
    downloader.lineaInicialParaElSemestre = lineaInicial
    downloader.initialize(curso, grupos)
    download()
    update()
else:
    print("Semestre Actual (ejemplo: 2017-2):")
    semestreActual = input()
    update()
    




