import csv, os
import jinja2
from datetime import date, timedelta
hoy = date.today().strftime("%d%m%y")

latex_jinja_env = jinja2.Environment(
	block_start_string = '\BLOCK{',
	block_end_string = '}',
	variable_start_string = '\VAR{',
	variable_end_string = '}',
	trim_blocks = True,
	autoescape = False,
	loader = jinja2.FileSystemLoader("templates")
        )

nombre_archivo_de_jubilados = "j.csv"

suplemento_archivo_salida = " Vacaciones Jubilados.tex"

archivo_de_jubilados = os.path.join(os.path.dirname(__file__), nombre_archivo_de_jubilados)

FORMATO_DE_FECHA = "%d/%m/%y"

def convierte_string_fecha(str_fecha):
  dia, mes, anno = tuple(map(int, str_fecha.split("/")))
  return date(day=dia, month=mes, year=2000 + anno)

festivos = list(map(convierte_string_fecha,
              ["27/08/17", "02/09/17", "03/09/17", "09/09/17",
               "10/09/17", "16/09/17", "17/09/17", "23/09/17",
               "24/09/17", "30/09/17", "01/10/17", "07/10/17",
               "08/10/17", "12/10/17", "14/10/17", "15/10/17",
               "21/10/17", "22/10/17", "28/10/17", "29/10/17",
               "01/11/17", "04/11/17", "05/11/17", "11/11/17",
               "12/11/17", "18/11/17", "19/11/17", "25/11/17",
               "26/11/17", "02/12/17", "03/12/17", "06/12/17",
               "08/12/17", "09/12/17", "10/12/17", "16/12/17",
               "17/12/17", "23/12/17", "24/12/17", "25/12/17",
               "30/12/17", "31/12/17",
               ]))

# festivos locales {"Las Palmas":["24/06/17","02/02/17], ... resto municipios} 

with open(archivo_de_jubilados, "r", encoding="utf8") as jubilados:
    lista_jubilados = []
    reader = csv.reader(jubilados, delimiter=";")
    for row in reader:
        lista_jubilados.append(row)

# print(lista_jubilados)

def vacaciones_naturales_a_habiles(naturales):
    # 22 -> habiles
    # 30  -> naturales  => naturales = 30 * habiles / 22
    return (22 * naturales)/30 

def fecha_en_letra(fecha_en_numero):
	MESES = { "01":"enero", "02":"febrero", "03":"marzo", "04":"abril",
		  "05":"mayo", "06":"junio", "07":"julio", "08":"agosto",
		  "09":"septiembre", "10":"octubre", "11":"noviembre", "12":"diciembre"}
	dia, mes, anno = tuple(fecha_en_numero.split("/"))
	mes_letra = MESES[mes]
	return "{} de {} de {}".format(dia, mes_letra, anno)
	
def dia_sin_cero(dia):
	if dia[0] == "0":
		return dia[1]
	else:
		return dia
    
def ajusta_si_festivo(fecha_inicio):
    #por-hacer añadir festivos locales quizás mis_festivos = festivos + festivos_mi_localidad
    if fecha_inicio in festivos:
        return ajusta_si_festivo(fecha_inicio - timedelta(days=1))
    else:
        return fecha_inicio
    
def festivos2(fecha, dias):
  if dias == 1:
    return ajusta_si_festivo(fecha)
  else:
    if fecha in festivos:
      return festivos2(fecha -timedelta(days=1), dias)
    else:
      return festivos2(fecha -timedelta(days=1), dias-1)

def calcula_periodo(fecha_jubilacion, dias):
 MESES = { "01":"enero", "02":"febrero", "03":"marzo", "04":"abril",
    "05":"mayo", "06":"junio", "07":"julio", "08":"agosto",
    "09":"septiembre", "10":"octubre", "11":"noviembre", "12":"diciembre"}
 if dias > 1:
  dia, mes, anno = tuple(map(int, fecha_jubilacion.split("/")))
  fecha_final = date(year=anno, month=mes, day=dia)
  fecha_inicio = festivos2(fecha_final, dias)
  fi = fecha_inicio.strftime(FORMATO_DE_FECHA)
  ff = fecha_final.strftime(FORMATO_DE_FECHA)
  fid, fim, fia = tuple(fi.split("/"))
  ffd, ffm, ffa = tuple(ff.split("/"))
  fim = MESES[fim]
  ffm = MESES[ffm]
  fid = dia_sin_cero(fid)
  ffd = dia_sin_cero(ffd)
  if fim == ffm:
    return "del {} al {} de {} de {}".format(fid, ffd, ffm, "20" + ffa)
  elif fia == ffa:
    return "del {} de {} al {} de {} de {}".format(fid, fim, ffd, ffm, "20" + ffa)
  else:
    fi = "{} de {} de {}".format(fid, fim, "20" + fia)
    ff = "{} de {} de {}".format(ffd, ffm, "20" + ffa)
    return "del {} al {}, ambos inclusive".format(fi, ff)
 else:
  dia, mes, anno = tuple(map(int, fecha_jubilacion.split("/")))
  fecha_final = date(year=anno, month=mes, day=dia)
  fj = ajusta_si_festivo(fecha_final)
  fj = fj.strftime(FORMATO_DE_FECHA)
  if fj != fecha_jubilacion:
      final = " al {}, ambos inclusive".format(fecha_jubilacion)
  else:
      final = ""
  fjd, fjm, fja = tuple(fj.split("/"))
  fjm = MESES[fjm]
  fj = "en el {} de {} de {}{}".format(fjd, fjm, "20" + fja, final)  
  return fj

lista_jubilados_final = []


for jubilado in lista_jubilados:
	jubilado = list(map((lambda x: x.strip().strip('"')), jubilado))
	por_hacer = jubilado[8] # contiene información de la baja
	if por_hacer == "NO SE ENCUENTRA DE BAJA":
		# inicio campos    
		dni = jubilado[0].strip()
		apellido1 = jubilado[1]
		apellido2 = jubilado[2]
		nombre = jubilado[3]
		centro = jubilado[4]
		fecha = jubilado[5].strip(" 0:00:00")
		try:
			mujer = jubilado[6]  
			if mujer == "M":
				dondona = "Doña"
				interesadoa = "a la interesada"
			else:
				dondona = "Don"
				interesadoa = "al interesado"
		except:
			dondona = "\VAR{dondona}"
			interesadoa = "al interesado"
		dias = round( vacaciones_naturales_a_habiles(float( jubilado[7].replace(",", "."))))
		if jubilado[9] == "597":
			cuerpo = "primaria"
		else:
			cuerpo = "secundaria"
		# * por-hacer determinar mis_festivos
		periodo = calcula_periodo(fecha_jubilacion = fecha, dias=int(dias))

		# arreglo nombre
		apellidos = apellido1 + " " + apellido2
		nombre_y_apellido = nombre + " " + apellidos
		nombre_archivo_de_salida = "{} {} {}, {} {} {}".format(centro, apellido1, apellido2, nombre, dni, suplemento_archivo_salida)
		
		# genero template
		
		template = latex_jinja_env.get_template("vacacionator.tex")

		filedata = template.render(
    nombre=nombre_y_apellido,
    dni=dni, fecha=fecha_en_letra(fecha),
    dondona=dondona, al_interesadoa=interesadoa,
    dias=dias,
    periodo=periodo,
    etiqueta = nombre_archivo_de_salida
    )

		# grabo archivo de salida
		g = open(nombre_archivo_de_salida,'w',encoding="utf8")
		g.write(filedata)
		g.close()
		nombre_archivo_lista_comprobacion = "listado de comprobación {}.txt".format(hoy)
		datos_a_grabar = "{} {}, {} días {} - {} {}\n".format(dni, apellidos, nombre, dias, periodo.strip(", ambos inclusive"), cuerpo)
		h = open(nombre_archivo_lista_comprobacion, 'a', encoding="utf8")
		h.write(datos_a_grabar)
		h.close()
