# -*- coding: utf-8 -*-
"""
Created on Sun Apr 11 06:47:58 2021

@author: Kevin
"""

import pandas as pd
import os
import gc
#import time
from tkinter import *
from tkinter import StringVar



def leer_archivo_pago(data_pago):  
    """
    Empezamos leyendo el primer archivo, la columna que nos interesa
    es Payment method, los datos de esta columna los agregaremos en una base de datos final

    Returns
    -------
    pagos : TYPE
        DESCRIPTION.

    """
    path = '..\Input'

    filename = data_pago + '.csv'
    
    fullpath_pago = os.path.join(path, filename)
    
    #Definir cuantos decimales requerimos para float
    
    pd.options.display.float_format = '{:,.2}'.format
    
    columnas = ['Order', 'Payment method']
    
    pagos = pd.read_csv(fullpath_pago, usecols = columnas)
    
    pagos.rename(columns={'Payment method':'Payment_method'}, inplace=True)
    
    return pagos

def agregar_filtros(pagos):
    """
    Esta función modificará los parametros de la hoja de cálculo donde
    se encuentran los datos del metodo de pago para hacerla más estética

    Parameters
    ----------
    pagos :      DataFrame
        DESCRIPTION.

    Returns
    -------
    pagos : TYPE
        DESCRIPTION.

    """


    pagos.rename(columns = {'Order':'#id'}, inplace=True)
        
    pagos['Payment_method'].replace({'External credit':'Credit or debit',
                                     'External Terminal Visa':'Credit or debit',
                                     'External Terminal Mastercard':'Credit or debit',
                                     'Pago con tarjeta de crédito y débito':'Credit or debit',
                                     'PayPal Payments Standard':'Paypal'}, inplace=True)
    
    # pagos['Payment_method'] = ['Paypal' if x == 'PayPal Payments Standard' else 'Credit or debit' for x in pagos['Payment_method']]

    return pagos

# =============================================================================
# ############### Base de datos final ###############
# =============================================================================

def leer_archivo_db(data_data):
    """
    Esta función leerá los datos del segundo archivo en la carpeta Input 
    para crear una Base de Datos final

    Returns
    -------
    database : TYPE
        DESCRIPTION.

    """
    path = '..\Input'
        
    entrada_db = data_data + '.csv'
        
    fullpath_db = os.path.join(path, entrada_db)
                
    # Estblecer las columnas necesarias para el Dataframe
            
    columnas_db = ['day', 'order_name', 'pos_location_name',
                       'gross_sales', 'net_sales', 'total_sales',
                       'total_cost']
        
    database = pd.read_csv(fullpath_db, usecols = columnas_db)

    return database


# =============================================================================
# 
# =============================================================================
def combinar(database, pagos):
    """
    Esta función realizará un marge del primer archivo con el segundo
    Además, redifinirá valores para poder crear nuevas columnas con cálculos

    Parameters
    ----------
    database : TYPE
        DESCRIPTION.
    pagos : TYPE
        DESCRIPTION.

    Returns
    -------
    database : TYPE
        DESCRIPTION.

    """
        
    #Renombrar columnda identificador para lograr marge
    
    database.rename(columns = {'order_name':'#id'}, inplace=True)
    
    database = pd.merge(database, pagos, on='#id', how='inner')
    
    database = database.astype({'Payment_method' : 'category'})
    
    #Agregar marge, BuscarV para los de excel xd
    
    database['day'] = pd.to_datetime(
        database['day'],
        errors = 'coerce',
        format = '%d/%m/%Y'
    )
    
    database.sort_values(['day'], inplace=True)
    
    database['pos_location_name'].replace({'San Ángel Studio':'San Angel',
                                         'Prado Norte 439':'Prado Norte',
                                         'Santa Fe Studio':'Santa Fe'}, inplace=True)
    
    #Transformar datos
    database['pos_location_name'].fillna('Online', inplace=True)
    
    # Realizar cálculos para agrgar columnas
        
    database['comision_sin_iva'] = database['net_sales'] * 0.035
    database['comision_con_iva'] = database['net_sales'] * .0406
    database['iva_de_la_comision'] = database['comision_con_iva'] - database['comision_sin_iva']
    database['iva_total'] = database['net_sales'] / 1.16 * 0.16
    database['ventas_sin_iva'] = database['gross_sales'] / 1.16
        
    return database

# =============================================================================
# 
# =============================================================================

def exportar_db(database):
    """
    Esta función creará el archivo Base de Datos.csv, colocándolo en la carpeta
    'Output'
    Parameters
    ----------
    database : TYPE
        DESCRIPTION.
        
    """
    #Exportar base de datos
    
    directorio_output = "..\Output\Base de Datos.csv"
    
    database.to_csv(directorio_output, 
        sep = ",",
        header = True, 
        index = False
        )
    


def leer_final():
    """
    Esta función leerá el archivo Base de Datos.csv en la carpeta Output
    y reasignará el total del dataframe a la variable 'poliza'

    Returns
    -------
    poliza : TYPE
        DESCRIPTION.

    """
    col_poliza = ['day', 'pos_location_name', 'Payment_method', 'net_sales', 
                  'comision_sin_iva', 'comision_con_iva', 'iva_de_la_comision', 
                  'iva_total', 'ventas_sin_iva']

    directorio_output = "..\Output\Base de Datos.csv"
    
    poliza = pd.read_csv(directorio_output, usecols = col_poliza)
    
    return poliza

def test(poliza):
    """
    Esta función manipulará el dataframe de la variable poliza

    Parameters
    ----------
    poliza : TYPE
        DESCRIPTION

    Returns
    -------
    prev_df : TYPE
        DESCRIPTION.

    """
    
    test = poliza.groupby(['day', 'pos_location_name', 'Payment_method']).agg({ 'comision_sin_iva':'sum','net_sales':'sum', 
                                                                        'comision_con_iva':'sum', 'iva_de_la_comision':'sum', 'iva_total':'sum',
                                                                       'ventas_sin_iva':'sum'}).reset_index()
    
    test2 = test[['day', 'pos_location_name', 'Payment_method', 'comision_sin_iva']].copy()
    test2['Account'] = 'comision_sin_iva'
    test2.rename(columns={'comision_sin_iva':'values'}, inplace=True)
    
    test3 = test[['day', 'pos_location_name', 'Payment_method', 'net_sales']].copy()
    test3['Account'] = 'net_sales'
    test3.rename(columns={'net_sales':'values'}, inplace=True)
    
    test4 = test[['day', 'pos_location_name', 'Payment_method', 'comision_con_iva']].copy()
    test4['Account'] = 'comision_con_iva'
    test4.rename(columns={'comision_con_iva':'values'}, inplace=True)
    
    test5 = test[['day', 'pos_location_name', 'Payment_method', 'iva_de_la_comision']].copy()
    test5['Account'] = 'iva_de_la_comision'
    test5.rename(columns={'iva_de_la_comision':'values'}, inplace=True)
    
    test6 = test[['day', 'pos_location_name', 'Payment_method', 'iva_total']].copy()
    test6['Account'] = 'iva_total'
    test6.rename(columns={'iva_total':'values'}, inplace=True)
    
    test7 = test[['day', 'pos_location_name', 'Payment_method', 'ventas_sin_iva']].copy()
    test7['Account'] = 'ventas_sin_iva'
    test7.rename(columns={'ventas_sin_iva':'values'}, inplace=True)
    
    poliza = pd.concat([test2, test3, test4, test5, test6, test7]).reset_index(drop=True)
    poliza = poliza[['day', 'pos_location_name', 'Payment_method', 'Account', 'values']]

    
    return poliza


def reglas_cargo(poliza):
    
    #========= Variables para cargarlas a las condiciones =========
    
    dia = poliza['fechas']
    
    # Cuentas
    ventas_netas = poliza['Account'] == 'net_sales'
    iva_t = poliza['Account'] == 'iva_total' 
    ventas_siniva = poliza['Account'] == 'ventas_sin_iva'
    comision_siniva = poliza['Account'] == 'comision_sin_iva'
    iva_delacomision = poliza['Account'] == 'iva_de_la_comision'
    comision_coniva = poliza['Account'] == 'comision_con_iva'
    
    #Sucursal
    san_angel = poliza['location'] == 'San Angel'
    prado_norte = poliza['location'] == 'Prado Norte'
    polanco = poliza['location'] == 'Polanco'
    online = poliza['location'] == 'Online'
    santa_fe = poliza['location'] == 'Santa Fe'
    interlomas = poliza['location'] == 'Interlomas'
    
    #Método de pago
    cash = poliza['payment'] == 'Cash'
    creditordebit = poliza['payment'] == 'Credit or debit'
    paypal = poliza['payment'] == 'Paypal'
    exchange = poliza['payment'] == 'Exchange credit'
    conekta = poliza['payment'] == 'Conekta'
    manual = poliza['payment'] == 'Manual'

    
    #========= Reglas Total: 126 cuentas /cargo-abono/ =========
    if dia and ventas_netas and san_angel and cash :
        return 'Cargo'
    elif dia and iva_t and san_angel and cash:
        return 'Abono'
    elif dia and ventas_siniva and san_angel and cash:
        return 'Abono'
    elif dia and comision_siniva and san_angel and cash:
        return 'Cargo'
    elif dia and iva_delacomision and san_angel and cash:
        return 'Cargo'
    elif dia and comision_coniva and san_angel and cash:
        return 'Abono'
    
    elif dia and ventas_netas and san_angel and creditordebit:
        return 'Cargo'
    elif dia and iva_t and san_angel and creditordebit:
        return 'Abono'
    elif dia and ventas_siniva and san_angel and creditordebit:
        return 'Abono'
    elif dia and comision_siniva and san_angel and creditordebit:
        return 'Cargo'
    elif dia and iva_delacomision and san_angel and creditordebit:
        return 'Cargo'
    elif dia and comision_coniva and san_angel and creditordebit:
        return 'Abono'
    
    elif dia and ventas_netas and san_angel and exchange:
        return 'Cargo'
    elif dia and iva_t and san_angel and exchange:
        return 'Abono'
    elif dia and ventas_siniva and san_angel and exchange:
        return 'Abono'
    elif dia and comision_siniva and san_angel and exchange:
        return 'Cargo'
    elif dia and iva_delacomision and san_angel and exchange:
        return 'Cargo'
    elif dia and comision_coniva and san_angel and exchange:
        return 'Abono'
#Condiciones Prado Norte    
    elif dia and ventas_netas and prado_norte and cash :
        return 'Cargo'
    elif dia and iva_t and prado_norte and cash:
        return 'Abono'
    elif dia and ventas_siniva and prado_norte and cash:
        return 'Abono'
    elif dia and comision_siniva and prado_norte and cash:
        return 'Cargo'
    elif dia and iva_delacomision and prado_norte and cash:
        return 'Cargo'
    elif dia and comision_coniva and prado_norte and cash:
        return 'Abono'
    
    elif dia and ventas_netas and prado_norte and creditordebit :
        return 'Cargo'
    elif dia and iva_t and prado_norte and creditordebit:
        return 'Abono'
    elif dia and ventas_siniva and prado_norte and creditordebit:
        return 'Abono'
    elif dia and comision_siniva and prado_norte and creditordebit:
        return 'Cargo'
    elif dia and iva_delacomision and prado_norte and creditordebit:
        return 'Cargo'
    elif dia and comision_coniva and prado_norte and creditordebit:
        return 'Abono'
    
    elif dia and ventas_netas and prado_norte and exchange:
        return 'Cargo'
    elif dia and iva_t and prado_norte and exchange:
        return 'Abono'
    elif dia and ventas_siniva and prado_norte and exchange:
        return 'Abono'
    elif dia and comision_siniva and prado_norte and exchange:
        return 'Cargo'
    elif dia and iva_delacomision and prado_norte and exchange:
        return 'Cargo'
    elif dia and comision_coniva and prado_norte and exchange:
        return 'Abono'
#Condiciones Polanco
    elif dia and ventas_netas and polanco and cash:
        return 'Cargo'
    elif dia and iva_t and polanco and cash:
        return 'Abono'
    elif dia and ventas_siniva and polanco and cash:
        return 'Abono'
    elif dia and comision_siniva and polanco and cash:
        return 'Cargo'
    elif dia and iva_delacomision and polanco and cash:
        return 'Cargo'
    elif dia and comision_coniva and polanco and cash:
        return 'Abono'

    elif dia and ventas_netas and polanco and creditordebit:
        return 'Cargo'
    elif dia and iva_t and polanco and creditordebit:
        return 'Abono'
    elif dia and ventas_siniva and polanco and creditordebit:
        return 'Abono'
    elif dia and comision_siniva and polanco and creditordebit:
        return 'Cargo'
    elif dia and iva_delacomision and polanco and creditordebit:
        return 'Cargo'
    elif dia and comision_coniva and polanco and creditordebit:
        return 'Abono' 
    
    elif dia and ventas_netas and polanco and exchange:
        return 'Cargo'
    elif dia and iva_t and polanco and exchange:
        return 'Abono'
    elif dia and ventas_siniva and polanco and exchange:
        return 'Abono'
    elif dia and comision_siniva and polanco and exchange:
        return 'Cargo'
    elif dia and iva_delacomision and polanco and exchange:
        return 'Cargo'
    elif dia and comision_coniva and polanco and exchange:
        return 'Abono'
#Condiciones Online
    elif dia and ventas_netas and online and paypal:
        return 'Cargo'
    elif dia and iva_t and online and paypal:
        return 'Abono'
    elif dia and ventas_siniva and online and paypal:
        return 'Abono'
    elif dia and comision_siniva and online and paypal:
        return 'Cargo'
    elif dia and iva_delacomision and online and paypal:
        return 'Cargo'
    elif dia and comision_coniva and online and paypal:
        return 'Abono'
    
    elif dia and ventas_netas and online and creditordebit:
        return 'Cargo'
    elif dia and iva_t and online and creditordebit:
        return 'Abono'
    elif dia and ventas_siniva and online and creditordebit:
        return 'Abono'
    elif dia and comision_siniva and online and creditordebit:
        return 'Cargo'
    elif dia and iva_delacomision and online and creditordebit:
        return 'Cargo'
    elif dia and comision_coniva and online and creditordebit:
        return 'Abono'
    
    elif dia and ventas_netas and online and exchange:
        return 'Cargo'
    elif dia and iva_t and online and exchange:
        return 'Abono'
    elif dia and ventas_siniva and online and exchange:
        return 'Abono'
    elif dia and comision_siniva and online and exchange:
        return 'Cargo'
    elif dia and iva_delacomision and online and exchange:
        return 'Cargo'
    elif dia and comision_coniva and online and exchange:
        return 'Abono'
    
    elif dia and ventas_netas and prado_norte and conekta:
        return 'Cargo'
    elif dia and iva_t and prado_norte and conekta:
        return 'Abono'
    elif dia and ventas_siniva and prado_norte and conekta:
        return 'Abono'
    elif dia and comision_siniva and prado_norte and conekta:
        return 'Cargo'
    elif dia and iva_delacomision and prado_norte and conekta:
        return 'Cargo'
    elif dia and comision_coniva and prado_norte and conekta:
        return 'Abono'
    
    elif dia and ventas_netas and prado_norte and manual:
        return 'Cargo'
    elif dia and iva_t and prado_norte and manual:
        return 'Abono'
    elif dia and ventas_siniva and prado_norte and manual:
        return 'Abono'
    elif dia and comision_siniva and prado_norte and manual:
        return 'Cargo'
    elif dia and iva_delacomision and prado_norte and manual:
        return 'Cargo'
    elif dia and comision_coniva and prado_norte and manual:
        return 'Abono'
#Condiciones Santa Fe   
    elif dia and ventas_netas and santa_fe and cash:
        return 'Cargo'
    elif dia and iva_t and santa_fe and cash:
        return 'Abono'
    elif dia and ventas_siniva and santa_fe and cash:
        return 'Abono'
    elif dia and comision_siniva and santa_fe and cash:
        return 'Cargo'
    elif dia and iva_delacomision and santa_fe and cash:
        return 'Cargo'
    elif dia and comision_coniva and santa_fe and cash:
        return 'Abono'
    
    elif dia and ventas_netas and santa_fe and creditordebit:
        return 'Cargo'
    elif dia and iva_t and santa_fe and creditordebit:
        return 'Abono'
    elif dia and ventas_siniva and santa_fe and creditordebit:
        return 'Abono'
    elif dia and comision_siniva and santa_fe and creditordebit:
        return 'Cargo'
    elif dia and iva_delacomision and santa_fe and creditordebit:
        return 'Cargo'
    elif dia and comision_coniva and santa_fe and creditordebit:
        return 'Abono'
    
    elif dia and ventas_netas and prado_norte and exchange:
        return 'Cargo'
    elif dia and iva_t and prado_norte and exchange:
        return 'Abono'
    elif dia and ventas_siniva and prado_norte and exchange:
        return 'Abono'
    elif dia and comision_siniva and prado_norte and exchange:
        return 'Cargo'
    elif dia and iva_delacomision and prado_norte and exchange:
        return 'Cargo'
    elif dia and comision_coniva and prado_norte and exchange:
        return 'Abono'
#Condidiones Interlomas 
    elif dia and ventas_netas and interlomas and cash:
        return 'Cargo'
    elif dia and iva_t and interlomas and cash:
        return 'Abono'
    elif dia and ventas_siniva and interlomas and cash:
        return 'Abono'
    elif dia and comision_siniva and interlomas and cash:
        return 'Cargo'
    elif dia and iva_delacomision and interlomas and cash:
        return 'Cargo'
    elif dia and comision_coniva and interlomas and cash:
        return 'Abono'
    
    elif dia and ventas_netas and interlomas and creditordebit :
        return 'Cargo'
    elif dia and iva_t and interlomas and creditordebit:
        return 'Abono'
    elif dia and ventas_siniva and interlomas and creditordebit:
        return 'Abono'
    elif dia and comision_siniva and interlomas and creditordebit:
        return 'Cargo'
    elif dia and iva_delacomision and interlomas and creditordebit:
        return 'Cargo'
    elif dia and comision_coniva and interlomas and creditordebit:
        return 'Abono'   
    
    elif dia and ventas_netas and interlomas and exchange:
        return 'Cargo'
    elif dia and iva_t and interlomas and exchange:
        return 'Abono'
    elif dia and ventas_siniva and interlomas and exchange:
        return 'Abono'
    elif dia and comision_siniva and interlomas and exchange:
        return 'Cargo'
    elif dia and iva_delacomision and interlomas and exchange:
        return 'Cargo'
    elif dia and comision_coniva and interlomas and exchange:
        return 'Abono'
    else: 
        None
        
        
def style(poliza):

    styles = [ ('NET_SALES', 'San Angel', 'Cash'), 
     ('IVA TOTAL', 'San Angel', 'Cash'), 
     ('VENTAS SIN IVA', 'San Angel', 'Cash'), 
     ('COMISION SIN IVA', 'San Angel', 'Cash'), 
     ('IVA DE LA COMISION', 'San Angel', 'Cash'), 
     ('COMISION CON IVA', 'San Angel', 'Cash'), 
     
     ('NET_SALES', 'San Angel', 'Credit or debit'), 
     ('IVA TOTAL', 'San Angel', 'Credit or debit'), 
     ('VENTAS SIN IVA', 'San Angel', 'Credit or debit'), 
     ('COMISION SIN IVA', 'San Angel', 'Credit or debit'), 
     ('IVA DE LA COMISION', 'San Angel', 'Credit or debit'), 
     ('COMISION CON IVA', 'San Angel', 'Credit or debit'), 
     
     ('NET_SALES', 'San Angel', 'Exchange credit'), 
     ('IVA TOTAL', 'San Angel', 'Exchange credit'), 
     ('VENTAS SIN IVA', 'San Angel', 'Exchange credit'), 
     ('COMISION SIN IVA', 'San Angel', 'Exchange credit'), 
     ('IVA DE LA COMISION', 'San Angel', 'Exchange credit'), 
     ('COMISION CON IVA', 'San Angel', 'Exchange credit'), 
#Prado Norte
     ('NET_SALES', 'Prado Norte', 'Cash'), 
     ('IVA TOTAL', 'Prado Norte', 'Cash'), 
     ('VENTAS SIN IVA', 'Prado Norte', 'Cash'), 
     ('COMISION SIN IVA', 'Prado Norte', 'Cash'), 
     ('IVA DE LA COMISION', 'Prado Norte', 'Cash'), 
     ('COMISION CON IVA', 'Prado Norte', 'Cash'), 
     
     ('NET_SALES', 'Prado Norte', 'Credit or debit'), 
     ('IVA TOTAL', 'Prado Norte', 'Credit or debit'), 
     ('VENTAS SIN IVA', 'Prado Norte', 'Credit or debit'), 
     ('COMISION SIN IVA', 'Prado Norte', 'Credit or debit'), 
     ('IVA DE LA COMISION', 'Prado Norte', 'Credit or debit'), 
     ('COMISION CON IVA', 'Prado Norte', 'Credit or debit'), 
     
     ('NET_SALES', 'Prado Norte', 'Exchange credit'), 
     ('IVA TOTAL', 'Prado Norte', 'Exchange credit'), 
     ('VENTAS SIN IVA', 'Prado Norte', 'Exchange credit'), 
     ('COMISION SIN IVA', 'Prado Norte', 'Exchange credit'), 
     ('IVA DE LA COMISION', 'Prado Norte', 'Exchange credit'), 
     ('COMISION CON IVA', 'Prado Norte', 'Exchange credit'), 
#Polanco
     ('NET_SALES', 'Polanco', 'Cash'), 
     ('IVA TOTAL', 'Polanco', 'Cash'), 
     ('VENTAS SIN IVA', 'Polanco', 'Cash'), 
     ('COMISION SIN IVA', 'Polanco', 'Cash'), 
     ('IVA DE LA COMISION', 'Polanco', 'Cash'), 
     ('COMISION CON IVA', 'Polanco', 'Cash'), 
     
     ('NET_SALES', 'Polanco', 'Credit or debit'), 
     ('IVA TOTAL', 'Polanco', 'Credit or debit'), 
     ('VENTAS SIN IVA', 'Polanco', 'Credit or debit'), 
     ('COMISION SIN IVA', 'Polanco', 'Credit or debit'), 
     ('IVA DE LA COMISION', 'Polanco', 'Credit or debit'), 
     ('COMISION CON IVA', 'Polanco', 'Credit or debit'), 
     
     ('NET_SALES', 'Polanco', 'Exchange credit'), 
     ('IVA TOTAL', 'Polanco', 'Exchange credit'), 
     ('VENTAS SIN IVA', 'Polanco', 'Exchange credit'), 
     ('COMISION SIN IVA', 'Polanco', 'Exchange credit'), 
     ('IVA DE LA COMISION', 'Polanco', 'Exchange credit'), 
     ('COMISION CON IVA', 'Polanco', 'Exchange credit'), 
#Online
     ('NET_SALES', 'Online', 'Manual'), 
     ('IVA TOTAL', 'Online', 'Manual'), 
     ('VENTAS SIN IVA', 'Online', 'Manual'), 
     ('COMISION SIN IVA', 'Online', 'Manual'), 
     ('IVA DE LA COMISION', 'Online', 'Manual'), 
     ('COMISION CON IVA', 'Online', 'Manual'), 
     
     ('NET_SALES', 'Online', 'Gift card'), 
     ('IVA TOTAL', 'Online', 'Gift card'), 
     ('VENTAS SIN IVA', 'Online', 'Gift card'), 
     ('COMISION SIN IVA', 'Online', 'Gift card'), 
     ('IVA DE LA COMISION', 'Online', 'Gift card'), 
     ('COMISION CON IVA', 'Online', 'Gift card'), 
     
     ('NET_SALES', 'Online', 'Paypal'), 
     ('IVA TOTAL', 'Online', 'Paypal'), 
     ('VENTAS SIN IVA', 'Online', 'Paypal'), 
     ('COMISION SIN IVA', 'Online', 'Paypal'), 
     ('IVA DE LA COMISION', 'Online', 'Paypal'), 
     ('COMISION CON IVA', 'Online', 'Paypal'), 
     
     ('NET_SALES', 'Online', 'Conekta'), 
     ('IVA TOTAL', 'Online', 'Conekta'), 
     ('VENTAS SIN IVA', 'Online', 'Conekta'), 
     ('COMISION SIN IVA', 'Online', 'Conekta'), 
     ('IVA DE LA COMISION', 'Online', 'Conekta'), 
     ('COMISION CON IVA', 'Online', 'Conekta'), 
     
     ('NET_SALES', 'Online', 'Credit or debit'), 
     ('IVA TOTAL', 'Online', 'Credit or debit'), 
     ('VENTAS SIN IVA', 'Online', 'Credit or debit'), 
     ('COMISION SIN IVA', 'Online', 'Credit or debit'), 
     ('IVA DE LA COMISION', 'Online', 'Credit or debit'), 
     ('COMISION CON IVA', 'Online', 'Credit or debit'), 
     
     ('NET_SALES', 'Online', 'Exchange credit'), 
     ('IVA TOTAL', 'Online', 'Exchange credit'), 
     ('VENTAS SIN IVA', 'Online', 'Exchange credit'), 
     ('COMISION SIN IVA', 'Online', 'Exchange credit'), 
     ('IVA DE LA COMISION', 'Online', 'Exchange credit'), 
     ('COMISION CON IVA', 'Online', 'Exchange credit'), 
 #Santa Fe
     ('NET_SALES', 'Santa Fe', 'Cash'), 
     ('IVA TOTAL', 'Santa Fe', 'Cash'), 
     ('VENTAS SIN IVA', 'Santa Fe', 'Cash'), 
     ('COMISION SIN IVA', 'Santa Fe', 'Cash'), 
     ('IVA DE LA COMISION', 'Santa Fe', 'Cash'), 
     ('COMISION CON IVA', 'Santa Fe', 'Cash'), 
     
     ('NET_SALES', 'Santa Fe', 'Credit or debit'), 
     ('IVA TOTAL', 'Santa Fe', 'Credit or debit'), 
     ('VENTAS SIN IVA', 'Santa Fe', 'Credit or debit'), 
     ('COMISION SIN IVA', 'Santa Fe', 'Credit or debit'), 
     ('IVA DE LA COMISION', 'Santa Fe', 'Credit or debit'), 
     ('COMISION CON IVA', 'Santa Fe', 'Credit or debit'),
     
     ('NET_SALES', 'Online', 'Exchange credit'), 
     ('IVA TOTAL', 'Online', 'Exchange credit'), 
     ('VENTAS SIN IVA', 'Online', 'Exchange credit'), 
     ('COMISION SIN IVA', 'Online', 'Exchange credit'), 
     ('IVA DE LA COMISION', 'Online', 'Exchange credit'), 
     ('COMISION CON IVA', 'Online', 'Exchange credit'),     
#Interlomas
     ('NET_SALES', 'Interlomas', 'Cash'), 
     ('IVA TOTAL', 'Interlomas', 'Cash'), 
     ('VENTAS SIN IVA', 'Interlomas', 'Cash'), 
     ('COMISION SIN IVA', 'Interlomas', 'Cash'), 
     ('IVA DE LA COMISION', 'Interlomas', 'Cash'), 
     ('COMISION CON IVA', 'Interlomas', 'Cash'), 
     
     ('NET_SALES', 'Interlomas', 'Credit or debit'), 
     ('IVA TOTAL', 'Interlomas', 'Credit or debit'), 
     ('VENTAS SIN IVA', 'Interlomas', 'Credit or debit'), 
     ('COMISION SIN IVA', 'Interlomas', 'Credit or debit'), 
     ('IVA DE LA COMISION', 'Interlomas', 'Credit or debit'), 
     ('COMISION CON IVA', 'Interlomas', 'Credit or debit'),
     
     ('NET_SALES', 'Interlomas', 'Exchange credit'), 
     ('IVA TOTAL', 'Interlomas', 'Exchange credit'), 
     ('VENTAS SIN IVA', 'Interlomas', 'Exchange credit'), 
     ('COMISION SIN IVA', 'Interlomas', 'Exchange credit'), 
     ('IVA DE LA COMISION', 'Interlomas', 'Exchange credit'), 
     ('COMISION CON IVA', 'Interlomas', 'Exchange credit'), 
    ]

    poliza['day'] = pd.to_datetime(poliza['day'])
    final_df = pd.DataFrame(pd.date_range(poliza['day'].min(), poliza['day'].max(), freq='d'), columns=['fechas'])


    testing = []
    for i in range(len(styles)):
        temp_df = final_df.copy()
        temp_df['temp'] = [styles[i] for _ in temp_df.index]
        temp_df[['account', 'location', 'payment']] = pd.DataFrame(temp_df['temp'].tolist(), index=temp_df.index)
        temp_df.drop(columns=['temp'], inplace=True)
        testing.append(temp_df)
    
    final_form = pd.concat(testing)
    final_form.sort_values('fechas', inplace=True)

             
    return final_form
'''
def pivotes(poliza):
    
    poliza['type_operation'] = poliza.apply(reglas_cargo, axis=1)

    test2 = pd.pivot_table(poliza, values='comision_sin_iva', index=['day','pos_location_name','Payment method'], columns='type_operation').reset_index()
    
    test3 = pd.pivot_table(poliza, values='net_sales', index=['day','pos_location_name','Payment method'], columns='type_operation').reset_index()
    
    test4 = pd.pivot_table(poliza, values='comision_con_iva', index=['day','pos_location_name','Payment method'], columns='type_operation').reset_index()
    
    test5 = pd.pivot_table(poliza, values='iva_de_la_comision', index=['day','pos_location_name','Payment method'], columns='type_operation').reset_index()
    
    test6 = pd.pivot_table(poliza, values='iva_total', index=['day','pos_location_name','Payment method'], columns='type_operation').reset_index()
    
    test7 = pd.pivot_table(poliza, values='ventas_sin_iva', index=['day','pos_location_name','Payment method'], columns='type_operation').reset_index()
    
    final = pd.concat([test2, test3, test4, test5, test6, test7])
    
    final.sort_values('day', inplace=True)
    
    return final
'''
def exportar_final(poliza):
    """
    Esta función exportará los resultados de la manipulación de datos a un archivo
    poliza.csv que será encontrada en la carpeta 'Output'

    Parameters
    ----------
    poliza : TYPE
        DESCRIPTION.
    """
    
    dirpoliza_output = "..\Output\Poliza.csv"
    
    poliza.to_csv(dirpoliza_output,
        sep = ",",
        header = True,
        index = False)
    
    

if __name__ == '__main__':
    
# No entendía bien cómo podían declarse las funciones en un sóla línea
# Las coloqué de la única manera que sé

    def send_data():
        data_pago = str(m_pago.get())
        data_data = str(data.get())
        
            
        pagos = leer_archivo_pago(data_pago)
        pagos = agregar_filtros(pagos)
        database = leer_archivo_db(data_data)
        database = combinar(database, pagos)
        exportar_db(database)
        #inicio = time.time()  
        poliza = leer_final()
        poliza = test(poliza)
        poliza = style(poliza)
        #reglas_cargo = reglas_cargo(prev_df)
        #poliza = pivotes(poliza)
        exportar_final(poliza)
        
        
        
        
    #Principal
    window = Tk()
    window.title("Creador de polizas")
    window.geometry("750x220")
    window.config(background = "#34495E")
    window.resizable(False, False)
    main_label = Label(text = "Ingresa el nombre del archivo según correspnda al campo para generar la poliza",
                       font= "Helvetica 12", bg = "#56CD63", fg = "white", width = 83, height = 2)
    main_label.grid(row = 0, column = 0, columnspan = 1)
    
    
    #Entiquetas
    etiqueta_pagos = Label(window, font = "Helvetica 12", 
                                 text = "Ingresa el nombre del archivo métodos de pago: ")
    etiqueta_db = Label(window, 
                              font = "Helvetica 12", 
                              text = "Ingresa el nombre del archivo reporte de ventas: ")
    
    
    #Valores variables
    m_pago = StringVar()
    data = StringVar()
    
    
    #Entradas
    entrada_pagos = Entry(window, textvariable = m_pago, width = 30, font = "Helvetica 12")
    entrada_pagos.place(x = 25, y = 95)
    data = Entry(window, textvariable = data, width = 30, font = "Helvetica 12")
    data.place(x = 25, y = 170)
    
    #Boton
    ejecutar = Button(window, font = "Helvetica 10", text = "Crear poliza", padx = 12, pady= 6, 
                            command = send_data)
    
    ejecutar.place(x = 550, y = 160)
    
    #Diseño
    etiqueta_pagos.config(background = "#34495E", fg = "#FFFFFF")
    etiqueta_db.config(background = "#34495E", fg = "#FFFFFF")
    etiqueta_pagos.place(x = 22, y = 65)
    etiqueta_db.place(x = 22, y = 140)
    
        
    window.mainloop()
'''
def main():

    pagos = leer_archivo_pago(data_pago)
    pagos = agregar_filtros(pagos)
    database = leer_archivo_db(data_data)
    database = combinar(database, pagos)
    exportar_db(database)
    inicio = time.time()  
    poliza = leer_final()
    poliza = test(poliza)
    poliza = style(poliza)
    #reglas_cargo = reglas_cargo(prev_df)
    #poliza = pivotes(poliza)
    exportar_final(poliza)
    fin = time.time()
    calctiempo = (fin-inicio)
'''

    #del path 
    
    
   #gc.collect()
