# Prefect
### Gómez Aldrete Luis Ignacio
### 216588253
#
En esta práctica se piensa implementar el uso de un *workflow manager* conocido como *Prefect* en *Python*. *Prefect* es una biblioteca de flujo de trabajo en *Python* que facilita la creación, el planificación y la orquestación de flujos de trabajo complejos y escalables en un entorno distribuido. Algunas de sus principales utilidades son:

+ Facilita la creación y el mantenimiento de flujos de trabajo complejos en *Python*, permitiendo la definición de tareas y dependencias entre ellas de manera clara y sencilla.
+ Permite la ejecución distribuida de flujos de trabajo, ya sea en una sola máquina o en un clúster de computadoras, facilitando la escalabilidad de los mismos.
Proporciona una API intuitiva y extensible para el monitoreo, registro y gestión de flujos de trabajo en ejecución, lo que ayuda a mejorar la visibilidad y la depuración de problemas.
+ Permite la integración con otras herramientas y servicios de terceros, como bases de datos, servicios de nube, herramientas de orquestación de contenedores, entre otros.
+Ofrece una gran flexibilidad en la definición de flujos de trabajo, permitiendo la definición de tareas personalizadas y el uso de diferentes tipos de orquestadores.

Para empezar, se tiene que instalar la librería de *Prefect* desde la terminal con el siguiente comando.
```cmd
pip install prefect
```
Una vez instalada la libería, se sigue el tutorial del vídeo [Getting Started with Prefect (PyData Denver)](https://www.youtube.com/watch?v=FETN0iivZps&t=2545s) para hacer un breve ejemplo de como se pueden usar los *workflow managers* para automatizar y perfeccionar la ejecución de funciones. Solo que se realizará una pequeña modificación al ejemplo, pues en lugar de almacenar la información que se extrae, transforma y carga en una base de datos, esta será almacenada en un archivo csv.

Para empezar a usar *Prefect* se tienen que definir las funciones pricipales de un *workflow manager*, el *ETL(extract, transform, load)*. En el caso de este ejemplo, las funciones se encargaran de extraer la información de quejas y transformarla para que se adapten al formato del archivo donde serán cargadas; esto crea un flujo bien definido donde se realizan estas acciones en un orden específico.
```python
with Flow("etl flow",schedule) as f:
    doc = create_document()
    raw = get_complaint_data()
    modificados = parse_complaint_data(raw)
    populated_table = store_complaints(modificados)
    populated_table.set_upstream(doc)
```
Donde cada función, exceptuando la de creación del archivo, es una parte del *ETL*.

Siendo extraer:
```python
@task(max_retries=10, retry_delay=datetime.timedelta(seconds=30))
def get_complaint_data():
    r = requests.get("https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/", params={'size':10})
    response_json = json.loads(r.text)
    return response_json['hits']['hits']
```

Después transformar:
```python
@task
def parse_complaint_data(raw):
    complaints = []
    Complaint = namedtuple('Complaint', ['data_received', 'state', 'product', 'company', 'complaint_what_happened'])
    for row in raw:
        source = row.get('_source')
        this_complaint = Complaint(
            data_received=source.get('date_recieved'),
            state=source.get('state'),
            product=source.get('product'),
            company=source.get('company'),
            complaint_what_happened=source.get('complaint_what_happened')
        )
        complaints.append(this_complaint)
    return complaints
```

Y por útlimo cargar:
```python
@task
def store_complaints(modificados):
    file = open('complaints.csv','w')
    csv_writer = csv.writer(file)
    title = ('State, Product, Company',)
    csv_writer.writerow(title)
    for complain in modificados:
        csv_writer.writerow(complain[1:-1])
    file.close()
    return
```

Y su ejecución en el flujo es regida por un horario especifíco; en este caso, cada minuto.
```python
schedule = IntervalSchedule(interval=datetime.timedelta(minutes=1))
```

Ya con todo esto es posible intentar replicar el ejemplo del vídeo, sin embargo hacerlo funcionar fue complicado, pues actualmente *pPrefect* ha sido actualizado a *Prefect 2* y mucha de la sintaxis usada en el vídeo de ejemplo quedó obsoleta y en la nueva documentación no queda muy claro como es que se tiene que migrar este ejemplo a la nueva versión. Para solucionar esto, se instaló la versión antigua de *Prefect* y de nuevo se intentó realizar el ejemplo del vídeo, aunque no estoy seguro de que funcione correctamente; en el vídeo dicen que el API al que se conecta solo se actualiza una vez al día, por lo que no se deberían esperar muchos cambios al ejecutar las fuciones del flujo cada minuto, pero como no me es posible dejar el flujo en ejecución todo el día, solo obtuve unos pocos resultados en el archivo. 

A pesar de las dificultades que tuve para realizar esta actividad, puedo ver el valor del uso de *workflow managers*. El uso de estas herramientas me ha dado una nueva perspectiva sobre cómo programar flujos de trabajo con un mayor control sobre todos los procesos involucrados en un programa. Creo que esta herramienta ayuda a dividir mejor los programas en tareas con propósitos específicos, lo que permite una división efectiva para que todas las tareas puedan complementarse entre sí y lograr que el programa funcione correctamente. Además, considero que es especialmente útil en proyectos grandes donde existe una clara dependencia entre tareas. En proyectos muy pequeños, como este ejemplo, puede que no sea tan eficiente o necesario, pero sigue siendo una herramienta que se puede implementar si así se desea.
