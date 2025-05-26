import streamlit as st import time from binance.um_futures import UMFutures from binance.error import ClientError

st.set_page_config(page_title="Futures Bot", layout="centered")

--- Sidebar para configuración ---

st.sidebar.title("Configuración del Bot") api_key = st.sidebar.text_input("API Key", type="password") api_secret = st.sidebar.text_input("API Secret", type="password")

symbol = st.sidebar.text_input("Símbolo", value="NEIROETHUSDT") inversion = st.sidebar.number_input("Inversión (USDT)", value=4.40, step=0.1) apalancamiento = st.sidebar.slider("Apalancamiento", 1, 20, 10) stop_loss_pct = st.sidebar.slider("Stop Loss %", 0.5, 5.0, 2.0) take_profit_pct = st.sidebar.slider("Take Profit %", 0.1, 3.0, 0.5)

activar = st.sidebar.toggle("Activar Bot")

--- Estado ---

st.title("Bot de Futuros Binance - Versión Móvil")

if not api_key or not api_secret: st.warning("Ingresa tus claves API para iniciar el bot.") st.stop()

client = UMFutures(key=api_key, secret=api_secret)

--- Funciones ---

def abrir_posicion(): try: # Setear apalancamiento client.change_leverage(symbol=symbol, leverage=apalancamiento)

# Precio de mercado actual
    ticker = client.ticker_price(symbol=symbol)
    precio = float(ticker['price'])

    # Tamaño de orden
    qty = round((inversion * apalancamiento) / precio, 4)

    # Crear orden de mercado
    orden = client.new_order(
        symbol=symbol,
        side="BUY",
        type="MARKET",
        quantity=qty
    )

    st.success(f"Orden ejecutada: {qty} {symbol} a {precio:.4f} USDT")
    return precio, qty
except ClientError as e:
    st.error(f"Error en orden: {e}")
    return None, None

def cerrar_posicion(qty): try: orden = client.new_order( symbol=symbol, side="SELL", type="MARKET", quantity=qty ) st.info("Posición cerrada automáticamente.") except Exception as e: st.error(f"Error al cerrar: {e}")

--- Ejecución del Bot ---

if activar: st.success("Bot activo... buscando oportunidad") precio_entrada, qty = abrir_posicion() if precio_entrada: stop_loss = precio_entrada * (1 - stop_loss_pct / 100) take_profit = precio_entrada * (1 + take_profit_pct / 100)

st.write(f"SL: {stop_loss:.4f} | TP: {take_profit:.4f}")

    while True:
        time.sleep(3)
        precio_actual = float(client.ticker_price(symbol=symbol)['price'])
        st.write(f"Precio actual: {precio_actual:.4f}")

        if precio_actual <= stop_loss or precio_actual >= take_profit:
            cerrar_posicion(qty)
            break

else: st.info("El bot está desactivado. Usa el interruptor en el panel lateral.")

