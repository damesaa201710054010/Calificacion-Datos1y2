# -*- coding: utf-8 -*-
import os
import requests


path = os.getcwd()
semestre = "2020-2" # Esto se cambia cada semestre, antes decia 2019-1 ahora dice 2019-2
trabajos = path+"/Trabajos"+semestre+"/"
lineaInicialParaElSemestre = 381 #Esto se cambia cada semestre, antes decia 217 y es la linea donde empieza a leer, ahora dice 284

def system(s):
        """Llamado al comando system"""
        os.system(s)

def initialize():
        """Se crean las carpetas donde se guardarán los trabajos"""
        system("mkdir "+trabajos)
        system("mkdir "+trabajos+"ED1")
        system("mkdir "+trabajos+"ED1/032")        
        system("mkdir "+trabajos+"ED2")
        system("mkdir "+trabajos+"ED2/032")

def processCSV(lineaInicialParaElSemestre):
        """Se procesa la encuesta CSV y se crea un .dat con la información de los usuarios"""
        archivo = open("UsuarioGitPreexistentes.csv", 'r') # Este archivo se baja cada semestre de Google Drive y se actualiza, pues es la encuesta de usuarios
        lines = archivo.readlines()
        archivo.close()
        usuarios = dict()
        for linea in lines[lineaInicialParaElSemestre:]:
                line = linea.split(",")
                curso = line[6]
                grupo = line[7]
                codigo = line[8]
                usuarioPareja = line[9].replace("\"", "")
                nombre = line[10]
                usuario = line[11].replace("\r","").replace("\"", "").replace("\n","").replace(" ","")
                usuarios[usuario] = (curso, grupo, codigo, usuarioPareja, nombre) #Este es el formato del diccionario
        archivo = open("usuariosYRepos.dat", "w")
        archivo.write(str(usuarios))
        archivo.close()
        return usuarios

def download(usuarios):
        """Se descargan los repositorios de los usuarios y se guarda un archivo de quienes tuvieron problemas"""
        archivo = open("problematicos.csv", 'w')
        #usuariosConRepositorio = dict()
        for elUsuario, valores in usuarios.iteritems():
                curso, grupo, codigo, usuarioPareja, nombre = valores 
                grupo = grupo[1:] # Se le quita el cero inicial al grupo
                for usuario in [elUsuario]:# usuarioPareja]: # Se procesa tanto para el usuario como para su pareja                      
                        if " " in usuario or "https" in usuario or "@" in usuario or "/" in usuario or usuario == "": #No puede ser vacío ni un URL ni un EMAIL
                                archivo.write( "Problemas con: ," + curso + "," + grupo +"," + nombre + "\n")
                        else:                                
                                nuevoFolder = trabajos+curso+"/0"+grupo+"/"+usuario
                                if not os.path.exists(nuevoFolder): #Si no existe la carpeta usuario, se crea
                                        system("mkdir "+nuevoFolder)                                        
                                currentPath = os.getcwd() 
                                os.chdir(nuevoFolder) # Nos paramos en la carpeta del usuario
                                if not os.path.exists(nuevoFolder+"/"+"ST024"+("5" if curso == "ED1" else "7")+"-0"+grupo):
                                        system("git clone https://github.com/"+usuario+"/"+"ST024"+("5" if curso == "ED1" else "7")+"-0"+grupo)
                                        
                                if len(os.listdir("./")) == 0: #Si no hay archivos ni carpetas
                                        archivo.write ("No tiene repositorio: ," + curso + "," + grupo +"," + usuario + "\n")
                                #else:
                                #        usuariosConRepositorio[usuario] = (curso, grupo, codigo, usuarioPareja, nombre)
                                os.chdir(currentPath)
        archivo.close()
        #archivoUsuarios = open("usuariosYRepos.dat", "w")
        #archivoUsuarios.write(str(usuariosConRepositorio))
        #archivoUsuarios.close()
                                                                   
# initialize()
usuarios = processCSV(lineaInicialParaElSemestre)
download(usuarios)




