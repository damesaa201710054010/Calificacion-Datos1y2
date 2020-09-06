# -*- coding: utf-8 -*-
from glob import glob
import os
import time
import sys
import fnmatch
import numpy

#sudo apt-get install calibre
#Calibre includes ebook-convert tool


def findFiles(pattern, path):
    """Encuentra archivos recursivamente dentro de una carpeta"""
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

def encontrarNombrePareja(usuarios, usuarioPareja):
    """Encuentra el nombre de la pareja"""
    if usuarios.has_key(usuarioPareja):
        nombrePareja = usuarios[usuarioPareja][4]
    else:
        nombrePareja = usuarioPareja
    return nombrePareja


def actualizarGits(trabajos, pull):
    """Actualiza todos los repositorios, es decir, hace git pull"""
    archivo = open("usuariosYRepos.dat", "r")
    usuarios = eval(archivo.read())
    archivo.close()
    if pull == True:
        for elUsuario, valores in usuarios.iteritems():
                    curso, grupo, codigo, usuarioPareja, nombre = valores
                    grupo = grupo[1:] #quitar al grupo un cero inicial
                    for usuario in [elUsuario, usuarioPareja]:
                        folderGitHub = trabajos+curso+"/0"+grupo+"/"+usuario+"/"+"ST024"+("5" if curso == "ED1" else "7")+"-0"+grupo
                        print folderGitHub
                        if os.path.exists(folderGitHub):
                                currentPath = os.getcwd()
                                os.chdir(folderGitHub)
                                os.system("git remote set-url origin git@github.com:"+usuario+"/"+"ST024"+("5" if curso == "ED1" else "7")+"-0"+grupo+".git")
                                os.system("git pull https://github.com/"+usuario+"/"+"ST024"+("5" if curso == "ED1" else "7")+"-0"+grupo)                                 
                                os.chdir(currentPath)                
    return usuarios

def calificarTalleresUsuario(usuario, valores):
    """Califica los talleres a un usuario"""
    curso, grupo, codigo, usuarioPareja, nombre = valores
    #grupo = grupo[1:] #quitar al grupo un cero inicial
    respuestas = [0]*numTalleres
    gr = ["01", "02", "03"]
    for grupo in gr:
        folderGitHub = trabajos+curso+"/0"+grupo+"/"+usuario+"/"+"ST024"+("5" if curso == "ED1" else "7")+"-0"+grupo 
        folder = folderGitHub+"/talleres"
        for i in range(1,numTalleres+1):
                archivos = []
                for extension in [".java", ".cpp", ".h", ".c", ".py", ".rb", ".pdf", ".doc"]:
                        archivos += findFiles("*"+extension,folder+"/taller%02d/" % (i,))            
                if len(archivos) > 0:
                        respuestas[i-1] = int(1)
        if 1 in respuestas: #me saca ceros si no hizo el ultimo taller, verificar y cambiar
            return respuestas                   
    return respuestas
       
def calificarTalleres(trabajos, usuarios):
        """Califica los talleres a todos los usuarios"""
        archivo = open("talleres.csv", "w")        
        archivo.write("Curso,Grupo,Codigo,Nombre,Pareja,Usuario,"+ ','.join("Taller"+str(i) for i in range(1,numTalleres+1)) + "\n" )
        for usuario, valores in usuarios.iteritems():
            curso, grupo, codigo, usuarioPareja, nombre = valores
            grupo = grupo[1:] #quitar al grupo un cero inicial
            respuestas = calificarTalleresUsuario(usuario, valores)
            respuestasPareja = calificarTalleresUsuario(usuarioPareja, valores)
            nombrePareja = encontrarNombrePareja(usuarios, usuarioPareja)            
            for i in range(len(respuestas)):
                respuestas[i] = respuestas[i] or respuestasPareja[i]   #Nota suya o de su pareja
            archivo.write(curso+","+grupo+","+codigo+","+nombre+","+nombrePareja+","+usuario+','+','.join(str(i) for i in respuestas)+"\n")
        archivo.close()


def calificarDoc(archivos):
        #Califica la doc HTML con un valor 1000/errores
        errores = 0
        for archivo in archivos:                
                os.system("checkstyle -c javadoc.xml "+archivo+" > temp.txt")
                elArchivo = open("temp.txt", "r")
                texto = elArchivo.readlines()
                if not "Must specify files to process" in texto[-1]:
                    if not texto[-1].strip("\n") == "Audit done." and not "found 0" in texto[-1]:
                        print texto[-1]
                        errores += int(texto[-1].split(" ")[3])
                elArchivo.close()
        if errores == 0:
                return 1000.0
        else:
                return 1000.0/(errores/len(archivos))
        
def calificarPDF(nombreArchivo):
        #Califica los puntos opcionales 5, 6 y 7 de un laboratorio
        os.system("ebook-convert "+nombreArchivo.replace(" ","\\ ")+" "+"tempPDF.txt")
        archivo = open("tempPDF.txt", 'r')
        texto = archivo.read()
        archivo.close()
        punto5, punto6, punto7 = 0,0,0 # Lectura, equipo, Inglés
        if "Lectura recomendada" in texto or "Recommended reading" in texto:            
            punto5 = 1
        if "Trabajo en Equipo y Progreso Gradual" in texto or "Team work and gradual progress" in texto:    
            punto6 = 1
        if "DEPARTMENT OF INFORMATICS AND SYSTEMS" in texto or "SCHOOL OF ENGINEERING" in texto :
            punto7 = 1
        return punto5, punto6, punto7

def obtenerArchivosDeUnaCarpetaProyecto(folder,carpeta):
    #Obtiene los nombres de archivos disponibles en una carpeta Lab
    pdfs = findFiles("*.pdf",folder+"/"+carpeta)
    docs = findFiles("*.doc",folder+"/"+carpeta)
    docxs = findFiles("*.docx",folder+"/"+carpeta)
    xlss = findFiles("*.xls",folder+"/"+carpeta)
    xlsxs = findFiles("*.xlsx",folder+"/"+carpeta)
    todos = pdfs + docs + docxs + xlss + xlsxs 
    return todos

def obtenerArchivosDeUnaCarpetaLab(folder,i,carpeta):
    #Obtiene los nombres de archivos disponibles en una carpeta Lab
    pdfs = findFiles("*.pdf",folder+"/lab0"+str(i)+"/"+carpeta)
    docs = findFiles("*.doc",folder+"/lab0"+str(i)+"/"+carpeta)
    docxs = findFiles("*.docx",folder+"/lab0"+str(i)+"/"+carpeta)
    xlss = findFiles("*.xls",folder+"/lab0"+str(i)+"/"+carpeta)
    xlsxs = findFiles("*.xlsx",folder+"/lab0"+str(i)+"/"+carpeta)
    todos = pdfs + docs + docxs + xlss + xlsxs 
    return todos

def copiarInformeDeLab(i, folder, carpeta, semestre, curso, grupo, nombre):
    #Copia todos los archivos tipo informe de un laboratorio a la carpeta correspondiente
    todos = obtenerArchivosDeUnaCarpetaLab(folder,i,carpeta)
    for index,archivo in enumerate(todos):
        if "archivo.txt" not in archivo:            
            os.system("cp "+archivo.replace(" ","\\ ").replace("(","\(").replace(")","\)")+" "+"Labs/Informes-"+semestre+"/"+curso+"/0"+grupo+"/Lab"+str(i)+"/"+nombre.replace(" ","-")+str(index)+"."+archivo.split(".")[-1])

def copiarInformeDeProyecto(folder, carpeta, semestre, curso, grupo, entrega, nombre):
    #Copia todos los archivos tipo informe de un proyecto a la carpeta correspondiente
    todos = obtenerArchivosDeUnaCarpetaProyecto(folder,carpeta)
    for index,archivo in enumerate(todos):
        if "archivo.txt" not in archivo:
            os.system("cp "+archivo.replace(" ","\\ ").replace("(","\(").replace(")","\)")+" "+"Proyecto/Informes-"+semestre+"/"+curso+"/0"+grupo+"/Entrega"+str(entrega)+"/"+nombre.replace(" ","-")+str(index)+"."+archivo.split(".")[-1])


def calificarLaboratoriosUsuario(usuario, valores, carpetas,semestre):
    #Califica los laboratorios a un usuario
    curso, grupo, codigo, usuarioPareja, nombre = valores
    grupo = grupo[1:] #quitar al grupo un cero inicial
    respuestas = numpy.zeros(shape=(5,6))
    losArchivos = [[]]*5
    folderGitHub = trabajos+curso+"/0"+grupo+"/"+usuario+"/"+"ST024"+("5" if curso == "ED1" else "7")+"-0"+grupo
    folder = folderGitHub+"/laboratorios"             
    for i in range(1,5+1):
            losArchivos[i-1] = [0]*6
            for idx, carpeta in enumerate(carpetas):                                                                 
                    extensiones = [  [".java", ".cpp", ".h", ".c", ".py", ".rb", ".txt"], [".java", ".cpp", ".h", ".c", ".py", ".rb", ".txt"], [".pdf", ".doc", ".docx"]]
                    archivosEstudiante = []
                    for extension in extensiones[idx]: #Se miran los archivos con extensiones válidas, obvio no txt ni word
                            archivosEstudiante += findFiles("*"+extension,folder+"/lab0"+str(i)+"/"+carpeta)
                    if len(archivosEstudiante) >= 1: # Si el estudiante entregó archivos en esa carpeta
                            respuestas[i-1][idx] = 1 # Por defecto el criterio es 1
                            if carpeta == "ejercicioEnLinea/":
                                respuestas[i-1][idx] = len(archivosEstudiante) #El num de archivos
                                archivosJava = findFiles("*.java",folder+"/lab0"+str(i)+"/"+carpeta)
                                if len(archivosJava) > 0:  #Si es código java                                          
                                            respuestas[i-1][idx] = calificarDoc(archivosJava)                          
                            if carpeta == "codigo/":
                                respuestas[i-1][idx] = len(archivosEstudiante) #Si no es Java, el num de archivos
                                archivosJava = findFiles("*.java",folder+"/lab0"+str(i)+"/"+carpeta)
                                if len(archivosJava) > 0:  #Si es código java, un puntaje según su JavaDoc                                          
                                            respuestas[i-1][idx] = calificarDoc(archivosJava)                                                        
                            if carpeta == "informe/": #Califica los puntos extras del informe pdf
                                            copiarInformeDeLab(i, folder, carpeta, semestre, curso, grupo, nombre)
                                            puntos5, puntos6, puntos7 = 0, 0, 0
                                            for archivo in archivosEstudiante:
                                                puntos5a, puntos6a, puntos7a =  calificarPDF(archivo)
                                                puntos5 += puntos5a
                                                puntos6 += puntos6a
                                                puntos7 += puntos7a
                                            respuestas[i-1][3] = puntos5
                                            respuestas[i-1][4] = puntos6 
                                            respuestas[i-1][5] = puntos7
                                                
                    losArchivos[i-1][idx] = map(lambda x: x.split("/")[-1], archivosEstudiante)
    return respuestas

       
def calificarLabs(trabajos, usuarios, semestre):
        #Califica los laboratorio a los usuarios
        archivos = [0]*5
        for i in range(0,5):
                archivos[i] = open("Labs/lab"+str(i+1)+".csv", "w")
                archivos[i].write("Laboratorio"+str(i+1)+",,,,,,,,,,,,\n" )
                archivos[i].write("Curso,Grupo,Codigo,Nombre,Pareja,Juez,Codigo,Informe, Lectura, Trabajo Equipo, English\n")#Juez,Codigo,Doc,Preguntas,Complejidad,Simulacro,Lectura,Equipo\n" )        
        carpetas = ['ejercicioEnLinea/','codigo/','informe/']
        for usuario, valores in usuarios.iteritems():
            curso, grupo, codigo, usuarioPareja, nombre = valores
            grupo = grupo[1:] #quitar al grupo un cero inicial
            respuestas = calificarLaboratoriosUsuario(usuario, valores, carpetas, semestre)
            respuestasPareja = calificarLaboratoriosUsuario(usuarioPareja, valores, carpetas, semestre)            
            nombrePareja = encontrarNombrePareja(usuarios, usuarioPareja)                
            for i in range(len(respuestas)):                
                for idx in range(len(carpetas)+3): #Son 3 criterios pero en el último se califican también 3 opcionales
                    respuestas[i][idx] = respuestas[i][idx] or respuestasPareja[i][idx] # Funciona como el máximo
                archivos[i].write(curso+","+grupo+","+codigo+","+nombre+","+nombrePareja+","+str(respuestas[i][0])+","+str(respuestas[i][1])+","+str(respuestas[i][2])+","+str(respuestas[i][3])+","+str(respuestas[i][4])+","+str(respuestas[i][5])+"\n")                                   
        for i in range(0,5):
                archivos[i].close()

              

def calificarProyectoUsuario(usuario, valores, criterios, entrega, semestre):
    #Califica una Entrega de Proyecto a un usuario
    curso, grupo, codigo, usuarioPareja, nombre = valores
    grupo = grupo[1:] #quitar al grupo un cero inicial
    respuestas = [0]
    losArchivos = [[]]
    folderGitHub = trabajos+curso+"/0"+grupo+"/"+usuario+"/"+"ST024"+("5" if curso == "ED1" else "7")+"-0"+grupo
    folder = folderGitHub+"/proyecto"             
    respuestas = [0]*len(criterios)
    losArchivos = [0]*len(criterios)
    for idx, criterio in enumerate(criterios):                                                       
            if "informe" in criterio:
                    copiarInformeDeProyecto(folder, criterio, semestre, curso, grupo, entrega, nombre)                     
            extensiones = [  [".java", ".cpp", ".h", ".c", ".py", ".rb"], [".pdf", ".doc", ".docx"], [".pdf", ".doc", ".docx"]]
            archivosEstudiante = []
            for extension in extensiones[idx]:
                    archivosEstudiante += findFiles("*"+extension,folder+"/"+criterio)
            if len(archivosEstudiante) > 0:
                    respuestas[idx] = 1
                    losArchivos[idx] = map(lambda x: x.split("/")[-1], archivosEstudiante)
    return respuestas

def calificarProyectos(trabajos, entrega, usuarios, semestre):
        #Califica los proyectos de todos los usuarios para una entrega determinada y un semestre determinado
        archivo = open("Proyecto/proyecto-"+str(entrega)+".csv", "w")        
        criterios = ['codigo/','informe/entrega'+str(entrega)+'/', 'informe/']
        archivo.write("Curso,Grupo,Codigo,Nombre,Pareja,Codigo,Informe, Informe fuera de carpeta\n")
        for usuario, valores in usuarios.iteritems():
            curso, grupo, codigo, usuarioPareja, nombre = valores
            grupo = grupo[1:] #quitar al grupo un cero inicial
            respuestas = calificarProyectoUsuario(usuario, valores, criterios, entrega, semestre)
            respuestasPareja = calificarProyectoUsuario(usuarioPareja, valores, criterios, entrega,semestre)
            nombrePareja = encontrarNombrePareja(usuarios, usuarioPareja)                  
            for idx in range(len(criterios)): 
                    respuestas[idx] = respuestas[idx] or respuestasPareja[idx]# Funciona como el máximo
            archivo.write(curso+","+grupo+","+codigo+","+nombre+","+nombrePareja+","+str(respuestas[0])+","+str(respuestas[1])+","+str(respuestas[2])+"\n")       
        archivo.close()


#Constantes
numTalleres = 13

#Main
semestre = "2020-2" # Esto se cambia cada semestre, antes decia 2019-1 ahora dice 2019-2
path = os.getcwd()
trabajos = path+"/Trabajos"+semestre+"/"
usuarios = actualizarGits(trabajos, True) #False es no haga pull
#calificarProyectos(trabajos,1, usuarios, semestre )
calificarTalleres(trabajos, usuarios)
#calificarLabs(trabajos, usuarios, semestre)



#Para unir pdfs, por ejemplo, todos los informes de labs o de proyecto:
# pdfunite *.pdf all.pdf
