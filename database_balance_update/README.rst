.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Database Balance Update
=======================

Este modulo añade unas acciones planificadas (ir.cron) 
las cuales se ejecutan diariamente para:

#. Actualizar las familias en la balanza. (Para Odoo product.category)
#. Actualizar los productos y sus attributos en la balanza. (Para Odoo product.product)
#. Generar pedidos de venta del TPV (pos.order) con los datos de los tickets de la balanza.


Installation
============
Este necesita las siguientes dependencias:

* base
* balanzas
* account
* sale
* stock
* account
* product_template_tpv

Configuration
=============
Para conectarse a la balanza es primero crear la configuración de la balanza en el modelo'balanzas.settings'.
Y crear un modelo de balanza con el usuario, contraseña, ip y nombre de la base de datos a la cual nos vamos a connectar

Dependencias externas
---------------------
Neceistas la instanciacion de las siguientes librerias de python:

* mysql-connector-python==8.0.25
* paramiko==2.7.2
* scp==0.13.3

Además del cliente de mysql en el sistema "sudo apt-get install mysql-client" (para linux)

Credits
=======

Contributors
------------

* Carlos Ros <cros@praxya.es>

Maintainer
----------

.. image:: http://visiion.net/logo.png
   :alt: Visiion Soluciones Tecnológicas
   :target: http://www.visiion.net/

This module is maintained by Praxya.
