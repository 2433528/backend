# 🏢 MiComunidapp

## 📄 Descripción

La aplicación MiComunidapp es una herramienta pensada para el ahorro de
tiempo al gestionar una comunidad de vecinos. Está orientada a gestores
de fincas, pero también de forma indirecta, a los propietarios, que a través
de esta consiguen tener, en un mismo lugar, toda la información de las
comunidades a las que pertenecen y sean gestionadas por esta aplicación.

Hay casos que vivo de cerca, donde las reuniones de vecinos son tediosas,
hablar directamente con el administrador de fincas puede costarte diversas
llamadas en el día, siempre y cuando no esté ocupado, por no hablar de si
tienes un problema con un vecino y no está dispuesto a dialogar. Se me
ocurrió, que varios de estos problemas serían más llevaderos si se
gestionaran a través de una aplicación. Al investigar sobre esto, me di
cuenta que, en la mayoría de los casos aunque el gestor de fincas tenga su
propio software de gestión, no es interactivo con los vecinos, ya que suelen
ser extensiones con un coste elevado. MiComunidapp está pensada para
unir las dos partes principales de una comunidad, gestores y propietarios.

## 🛠️ Tecnologías

### Frontend

    - JavaScript: Lenguaje de programación
    - React: Framework
    - Vite: Herramienta rápida de desarrollo y compilación
    - Yarn: Gestor de paquetes
    - HTML5: Lenguaje de marcas
    - CSS: Diseño
    - Tailwind: Framework de CSS
    - Docker: Contenerización de aplicaciones
    - VSCode: Editor de código

### Backend

    - Python: Lenguaje de programación
    - Django Rest Framework: Framework para la construcción de APIs
    - JWT: Autenticación
    - Gunicorn: Servidor web HTTP
    - PostgreSQL: Sistema gestor de base de datos
    - Docker: Contenerización de aplicaciones
    - VSCode: Editor de código

He usado estas tecnologías frente a otras porque la mayoría las he aprendido durante mi formación como
Técnico Superior en Desarrollo de Aplicaciones Web.

## 🐳 Despliegue con Docker

1. Clona ambos repositorios.

    - front: git clone https://github.com/2433528/frontend.git
    - back: git clone https://github.com/2433528/backend.git

2. Instalamos Docker si no lo tenemos. Creamos una red donde se conecten los dos contenedores (front y back) con el siguiente comando:

    docker network create app-network

    Damos valor a las variables del archivo .env.example en la carpeta
    backend y creamos un archivo .env para el front, dentro de su carpeta,
    con la variable:

        VITE_API_URL= URL que hayamos definido para la API

3. Gracias al Makefile hemos simplificado los comandos para levantar los contenedores.

    Desde la carpeta donde se encuentra el Makefile del front ejecutamos:

        -​ make rebuild-server -> Reconstruye la imagen y aplica cambios si los hemos hecho
        ​
        -​ make up -> Levanta el contenedor
        ​
        -​ make down -> Para el contenedor y lo borra

    Desde la carpeta donde se encuentra el Makefile del back ejecutamos:
        -​ make rebuild-server -> Reconstruye la imagen y aplica cambios si los hemos hecho​
        -​ make up -> Levanta el contenedor
        -​ make migrate-db -> Aplica los cambios en la base de datos
        -​ make down -> Para el contenedor y lo borra

    Otros comandos:
        -​ make createsuperuser -> Crea un super usuario
        -​ make collectstatic -> Reúne archivos estáticos (css, imágenes, ...) en un solo directorio

## ⚙️ Funcionalidades

    - Comunicados: Muestra comunicados importantes a los vecinos. Se pueden enviar de forma individual, eligiendo a que
    propietarios va dirigido. Se muestra un aviso a estos cuando entran a la aplicación.

    - Convocatorias: Para crear las reuniones y escribir los puntos del día. También tiene su propio aviso al entrar a la
    aplicación. Al cerrar la convocatoria, no se podrá editar y se creará el acta.

    - Actas: El acta recoge el resumen de la convocatoria y los puntos del día, en los cuales, para cada uno, podremos abrir
    una votación el tiempo oportuno para que los vecinos voten. Al cerrarla, automáticamente se verá el recuento de votos y si es
    favorable o no. Al marcar el acta como resuelta no se podrá editar.

    - Información: Tablón de anuncios para los vecinos. Se mostrarán aquellos datos relevantes como: Teléfonos,
    contactos, códigos… Muestra el aviso de información.

    - Incidencias: Gestiona el ciclo de las incidencias que surgen en la Comunidad. Los avisos de incidencias solo los ve el gestor de
    la comunidad. Los vecinos podrán dar de alta incidencias y el gestor recibe avisos y gestiona estados.

    - Votaciones: Permite a los vecinos participar en las decisiones referentes a la comunidad. En una reunión de vecinos, si hay
    que hacer por ejemplo una reforma, abrir una votación para ver cuántos están de acuerdo y si se procede a ello. Se incluye en
    el acta. También se muestra el aviso por votación.

    - Gestión de la comunidad: Si se es gestor de la comunidad, tendremos acceso a un submenú, donde podremos dar de alta
    a propietarios y propiedades, listarlos y cambiar los roles entre los propietarios, como por ejemplo, dar a uno el rol de
    presidente o quitarselo. Además podremos crear comunidades para gestionar mediante un formulario o subiendo un archivo
    CSV, tanto de las comunidades, como de los propietarios y sus propiedades.

## 💡 Posibles mejoras y ampliaciones

    - Mejorar el funcionamiento de los avisos.
    - Mejorar la interfaz de usuario.
    -​ Mandar emails desde la aplicación.
    -​ Notificaciones en tiempo real aunque la aplicación esté cerrada.
    -​ Un apartado donde subir documentos de la comunidad para que los vecinos los puedan consultar.
    -​ Poder subir fotos, si es necesario, para documentar una incidencia.
    -​ Incluir un chat en tiempo real.

## 📜 Licencias
    Este proyecto tiene licencia Creative Commons
    Atribución-NoComercial-CompartirIgual 4.0 Internacional (CC BY-NC-SA
    4.0).
    Usted es libre de:
        ●​ Compartir — copiar y redistribuir el material en cualquier medio o
        formato
        ●​ Adaptar — remezclar, transformar y construir a partir del material

    Bajo los siguientes términos:
        ●​ Atribución — Usted debe dar crédito de manera adecuada, brindar
        un enlace a la licencia, e indicar si se han realizado cambios. Puede
        hacerlo en cualquier forma razonable, pero no de forma tal que
        sugiera que usted o su uso tienen el apoyo del licenciante.
        ●​ No Comercial — Usted no puede hacer uso del material con
        propósitos comerciales.
        ●​ Compartir Igual — Si remezcla, transforma o crea a partir del
        material, debe distribuir su contribución bajo la misma licencia del
        original.

    No hay restricciones adicionales — No puede aplicar términos legales ni
    medidas tecnológicas que restrinjan legalmente a otras a hacer cualquier
    uso permitido por la licencia.

## 🔗 Links

    Frontend: https://github.com/2433528/frontend
    Backend: https://github.com/2433528/backend
    VideoDemo: https://youtu.be/9W1U_icHtbo

## 🧑‍💻 Autor
    Cristina García
    LinkedIn: https://www.linkedin.com/in/cristina-garcía-4242b2329
