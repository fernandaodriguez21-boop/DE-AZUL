import pandas as pd
import webbrowser
import urllib.parse
from datetime import datetime
import os

# Configuración del archivo
ARCHIVO_EXCEL = "control_ventas.xlsx"

def cargar_datos():
    if os.path.exists(ARCHIVO_EXCEL):
        return pd.read_excel(ARCHIVO_EXCEL)
    else:
        columnas = ["Fecha", "Cliente", "Telefono", "Producto", "Total", "Abonado", "Saldo_Pendiente", "Esquema", "Estado"]
        return pd.DataFrame(columns=columnas)

def guardar_datos(df):
    df.to_excel(ARCHIVO_EXCEL, index=False)

def enviar_whatsapp(tel, mensaje):
    msg_url = urllib.parse.quote(mensaje)
    url = f"https://web.whatsapp.com/send?phone={tel}&text={msg_url}"
    print("🚀 Abriendo WhatsApp Web...")
    webbrowser.open(url)

def registrar_venta():
    df = cargar_datos()
    print("\n--- 📝 NUEVA VENTA / ANTICIPO ---")
    cliente = input("Nombre del cliente: ")
    tel = input("WhatsApp (ej: 521...): ")
    prod = input("Producto: ")
    total = float(input("Precio Total: $"))
    pago = float(input("Anticipo/Pago hoy: $"))
    
    print("\nEsquema: 1.Exhibición | 2.Semanal | 3.Quincenal | 4.Mensual")
    opc = input("Seleccione (1-4): ")
    esquemas = {"1":"Exhibición", "2":"Semanal", "3":"Quincenal", "4":"Mensual"}
    esquema = esquemas.get(opc, "No especificado")
    
    saldo = total - pago
    estado = "PAGO TOTAL" if saldo <= 0 else "ANTICIPO"
    fecha = datetime.now().strftime("%d/%m/%Y")

    nueva_fila = {
        "Fecha": fecha, "Cliente": cliente, "Telefono": tel, "Producto": prod,
        "Total": total, "Abonado": pago, "Saldo_Pendiente": max(0, saldo),
        "Esquema": esquema, "Estado": estado
    }
    
    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
    guardar_datos(df)

    msg = (f"*🧾 COMPROBANTE DE {estado}*\n"
           f"---------------------------\n"
           f"*Cliente:* {cliente}\n"
           f"*Producto:* {prod}\n"
           f"💰 Total: ${total:,.2f}\n"
           f"💵 Pagado hoy: ${pago:,.2f}\n"
           f"📌 *Saldo Pendiente: ${max(0, saldo):,.2f}*\n"
           f"📅 Plan: {esquema}\n"
           f"---------------------------\n"
           f"¡Gracias por su preferencia!")
    enviar_whatsapp(tel, msg)

def registrar_abono():
    df = cargar_datos()
    print("\n--- 💵 REGISTRAR NUEVO ABONO ---")
    nombre = input("Nombre del cliente: ").lower()
    busqueda = df[df['Cliente'].str.lower().str.contains(nombre)]

    if not busqueda.empty:
        idx = busqueda.index[-1] # Tomamos la última deuda activa
        cliente = df.loc[idx, 'Cliente']
        saldo_ant = df.loc[idx, 'Saldo_Pendiente']
        
        if saldo_ant <= 0:
            print(f"✅ {cliente} ya no tiene deudas pendientes.")
            return

        print(f"Cliente: {cliente} | Deuda Actual: ${saldo_ant:,.2f}")
        abono = float(input("¿Cuánto va a abonar hoy?: $"))
        
        nuevo_saldo = saldo_ant - abono
        df.at[idx, 'Abonado'] += abono
        df.at[idx, 'Saldo_Pendiente'] = max(0, nuevo_saldo)
        if nuevo_saldo <= 0: df.at[idx, 'Estado'] = "PAGO TOTAL"
        
        guardar_datos(df)

        msg = (f"*✅ COMPROBANTE DE ABONO*\n"
               f"---------------------------\n"
               f"Hola *{cliente}*, recibimos tu abono.\n"
               f"💵 Monto abonado: ${abono:,.2f}\n"
               f"📉 *Nuevo Saldo: ${max(0, nuevo_saldo):,.2f}*\n"
               f"---------------------------\n"
               f"¡Gracias por mantenerse al día!")
        enviar_whatsapp(df.loc[idx, 'Telefono'], msg)
    else:
        print("❌ Cliente no encontrado.")

def consultar_saldo():
    df = cargar_datos()
    print("\n--- 🔍 CONSULTA DE ESTADO ---")
    nombre = input("Nombre del cliente: ").lower()
    res = df[df['Cliente'].str.lower().str.contains(nombre)]
    
    if not res.empty:
        print(res[["Fecha", "Cliente", "Producto", "Total", "Saldo_Pendiente", "Estado"]])
    else:
        print("❌ No se encontraron registros.")

# Menú Principal
if __name__ == "__main__":
    while True:
        print("\n=== 🚀 PANEL DE VENTAS & COBRANZA ===")
        print("1. Nueva Venta / Anticipo")
        print("2. Registrar Abono a Deuda")
        print("3. Consultar Saldo/Historial")
        print("4. Salir")
        opcion = input("Selecciona una opción: ")

        if opcion == "1": registrar_venta()
        elif opcion == "2": registrar_abono()
        elif opcion == "3": consultar_saldo()
        elif opcion == "4": break
        else: print("Opción inválida.")