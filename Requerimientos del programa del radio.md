###### Requerimientos del programa del radio automatizada:



problema:



El profesor necesita automatizar el flujo de trabajo de su radio.



1\. Necesita crear una automatización para descargar programas de diferentes plataformas de contenido 



(principalmente radios cristianas {radio japon (1 vez a la semana) 8AM, radio clásica 7AM, Amor que vale, Golpe de Bit, Noticias Telemundo (se descarga de youtube), 15:00 Grandes ciclos (radio clasic), 16:30 Tu historia preferida (listos se saltan el paso 2)}, 19:00 documentales de la DW (de yt), 20:00 Radio classic (musica antigua- esta listo), 21:15 noticias Telemenudo, 22:00 A travez de la biblia, 23:00 radio classic, 4:00 conferencias fundación march).



2\. Necesita que se editen automáticamente (recortar principio, también partes que involucren contenido no relacionado - radio classic) y reemplazarlas por las secciones que el crea (audios especiales de introducción al contenido).



3\. Enviar las ediciones al computador de Antofagasta, automático (actualmente se ocupa AnyDesk)



4\. SaraRadio es el programa para que ocupa para calendarizar las ediciones de audio (grabaciones) en horarios especificos



###### tecnologías sugeridas:



Principalmente Python, se podría implementar el uso del drive para almacenar las descargas y automatizar su subida y descarga, usando librerías de drive



typescript, javaSript



Podría ser bueno implementar un dashboard para realizar todas esas actividades automático, y un calendario en donde se pueda programar las grabaciones (seria la GUI para el punto 4)



Base de datos sujeta a implementación. (Revisar)



Idea principal: implementar búsqueda de API's de las paginas web para agregar esas sintonias



