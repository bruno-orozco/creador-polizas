'''
Autor: Bruno Orozco Mejía
'''

import pandas as pd

def main():
    pagos = leer_archivo_pago()
    pagos = agregar_filtros(pagos)
    database = leer_archivo_db()
    database = combinar(database, pagos)
    exportar_db(database)

#Empezamos leyendo el primer archivo, la columna que nos interesa
#es Payment method, los datos de esta columna los agregaremos en una base de datos final

def leer_archivo_pago():
    
    import os
    
    path = '..\Input'
    
    filename = input("Por favor, ingresa el nombre del primer archivo: [pago] ") + 'csv'
    
    fullpath = os.path.join(path, filename)
    
    #Definir cuantos decimales requerimos para float
    
    pd.options.display.float_format = '{:,.2}'.format

    columnas = ['Date', 'Order', 'Payment method']
    
    directorio_input_pay = "..\Input\pago.csv"
    
    pagos = pd.read_csv(directorio_input_pay, usecols = columnas)
    
    return pagos

#Esta función modificará los parametros de la hoja de cálculo donde
#se encuentran los datos del metodo de pago para hacerla más estética

def agregar_filtros(pagos):
    print("Realizando cambios . . .")

    pagos['Date'] = pd.to_datetime(
        pagos['Date'],
        errors = 'coerce',
        format = '%Y-%m-%d'
        )
    
#Remplazar valores necesarios

    pagos = pagos.rename(index = str, columns = {'Order':'#id'})
    
    pagos.loc[pagos['Payment method'] == 
              'External credit', 'Payment method'] = 'Credit or debit'
    pagos.loc[pagos['Payment method'] == 
              'External Terminal Visa', 'Payment method'] = 'Credit or debit'
    pagos.loc[pagos['Payment method'] == 
              'External Terminal Mastercard', 'Payment method'] = 'Credit or debit'
    pagos.loc[pagos['Payment method'] == 
              'Pago con tarjeta de crédito y débito', 'Payment method'] = 'Credit or debit'
    pagos.loc[pagos['Payment method'] == 
              'PayPal Payments Standard', 'Payment method'] = 'Paypal'
    
    return pagos

print("¡El primer archivo ha sidoagregado exitosamente!")

############### Base de datos final ###############

#Esta función leerá los datos del segundo archivo en la carpeta Input 
#para crear una Base de Datos final

def leer_archivo_db():

    import os
    
    path = '..\Input'
        
    entrada_db = input("Por favor, ingresa el nombre del segundo archivo: [db] ") + 'csv'
        
    fullpath = os.path.join(path, entrada_db)
        
    directorio_input_db = "..\Input\db.csv"
        
    #Estblecer las columnas necesarias para el Dataframe
            
    columnas_db = ['day', 'order_name', 'pos_location_name',
                       'gross_sales', 'net_sales', 'total_sales',
                       'total_cost']
        
    database = pd.read_csv(directorio_input_db, usecols = columnas_db)
    
    return database

    
# Esta función realizará un marge del primer archivo con el segundo
# Además, redifinirá valores para poder crear nuevas columnas con cálculos

def combinar(database, pagos):
    
    print("Realizando cambios . . .")
    
    #Renombrar columnda identificador para lograr marge
    
    database = database.rename(index = str, columns = {'order_name':'#id'})
    
    database = pd.merge(database, pagos)
    
    database = database.astype({'Payment method' : 'category'})
    
    #Agregar marge, BuscarV para los de excel xd

    database['day'] = pd.to_datetime(
        database['day'],
        errors = 'coerce',
        format = '%d/%m/%Y'
    )
    
    database = database.sort_values(['day'])
    

    database.loc[database['pos_location_name'] == 
                 'San Ángel Studio', 'pos_location_name'] = 'San Angel'
    database.loc[database['pos_location_name'] == 
                 'Prado Norte 439', 'pos_location_name'] = 'Prado Norte'
    database.loc[database['pos_location_name'] == 
                 'Santa Fe Studio', 'pos_location_name'] = 'Santa Fe'
    
    #Transformar datos
    pos = database['pos_location_name']
        
    pos.fillna('Online', inplace = True)
    
    
    # Realizar cálculos para agrgar columnas
        
    database['comision_sin_iva'] = database['net_sales'] * 0.035
    database['comision_con_iva'] = database['net_sales'] * .0406
    database['iva_de_la_comision'] = database['comision_con_iva'] - database['comision_sin_iva']
    database['iva_total'] = database['net_sales'] / 1.16 * 0.16
    database['ventas_sin_iva'] = database['gross_sales'] / 1.16
    
    return database
    
#Finalmente, exportamos los datos manipulados a un archivo nombrado 'Base de Datos

def exportar_db(database):

    #Exportar base de datos
    
    directorio_output = "..\Output\Base de Datos.csv"
    
    database.to_csv(directorio_output, 
        sep = ",",
        header = True, 
        index = False
        )
    
    input('''
¡Tu archivo ya está listo!
Los resultados los puedes revisar en la carpeta \'Output\'.
Presiona enter para salir.''')

 
    '''
    #### Poliza ### Cóigo para crear nuevos cálculos
    
    la idea es poder realizar tipo suma si conjunto como excel
    
    poliza = pd.read_csv(directorio_output)
    
    diccionario = {'comision_sin_iva': sum}
     
    poliza=  poliza.groupby(['Payment method', 'pos_location_name', 'day']).agg(diccionario)
    #
    
    
    
    dirpoliza_output = "..\Output\Poliza.csv"
    poliza.to_csv(dirpoliza_output,
        sep = ",",
        header = True,
        index = True
        )
'''
    
if __name__ == "__main__":
    main()
    
    

