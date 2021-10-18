.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Atzeneta - Importar Facturas Telefonía
============================

Este modulo añade un nuevo elemento de menu "Importar Facturas Telefonía". 
El cual mostrará un wizard para insertar fecha de la factura y el fichero csv que vamos a leer y procesar.

Installation
============
Este necesita las siguientes dependencias:
* account
* sale
* purchase

Configuration
=============
Para un correcto funcionamiento de este modulo, primero es necesario rellenar el cliente la tabla de tarífas telefonicas.
Una vez hecho hecho y asegurandose que tenemos completado el modelo de importación de registros, (este modulo actualmente genera al instalar los registros del 330 y del 340). 
Una vez estas dos puntos anteriores podemos ejecutar el importador, para ellos en "Facturación / Contabilidad" --> "Importar Facturas Telefonia" --> nos lanzará un wizard en el cual nos pedira el fichero, debe ser en .txt nos permite que el formato sea UFT-8 o iso-8859-1.
La fecha que nos pide es la fecha que se introducira en las facturas como fecha de factura y fecha de vencimiento.


Credits
=======

Contributors
------------

* Carlos Ros <cros@praxya.es>

Maintainer
----------

.. image:: http://praxya.com/wp-content/uploads/2015/11/logo-h-nomargin.jpg
   :alt: Praxya
   :target: http://www.praxya.com/

This module is maintained by Praxya.
