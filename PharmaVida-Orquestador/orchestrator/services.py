"""
Servicios de orquestación que coordinan llamadas entre microservicios.
"""

import requests
from django.conf import settings
from .utils import OrchestrationError
import requests
import logging

logger = logging.getLogger(__name__)


def _get_microservice_url(service_name):
    """Obtiene la URL base de un microservicio."""
    return settings.MICROSERVICES.get(service_name)


def _make_request(method, url, headers=None, json=None, params=None):
    """Realiza una petición HTTP a un microservicio con manejo de errores y logging de debug."""
    try:
        logger.info(f"[ORQUESTADOR][REQUEST] {method} {url} headers={headers} params={params} json={json}")
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=json,
            params=params
        )
        logger.debug(f"[ORQUESTADOR][RESPONSE] status={response.status_code} body={response.text}")

        if response.status_code >= 400:
            # Log response error details
            logger.error(f"[ORQUESTADOR][ERROR RESPONSE] status={response.status_code} body={response.text}")
            try:
                error_data = response.json() if response.content else {}
            except Exception as json_err:
                logger.error(f"[ORQUESTADOR][ERROR RESPONSE][JSON ERROR] {json_err}")
                error_data = {"error": response.text}
            raise OrchestrationError(
                f"Error en microservicio: {error_data.get('error', response.text)}",
                status_code=response.status_code,
                details=error_data
            )

        # Intentar parsear JSON de la respuesta
        try:
            return response.json() if response.content else {}
        except Exception as json_err:
            logger.error(f"[ORQUESTADOR][RESPONSE][JSON ERROR] status={response.status_code} body={response.text}")
            raise OrchestrationError(
                f"Error en petición al microservicio: {str(json_err)}",
                status_code=500
            )

    except requests.Timeout:
        logger.error(f"[ORQUESTADOR][TIMEOUT] {method} {url}")
        raise OrchestrationError("Timeout al comunicarse con el microservicio", status_code=504)
    except requests.ConnectionError:
        logger.error(f"[ORQUESTADOR][CONNECTION ERROR] {method} {url}")
        raise OrchestrationError("No se pudo conectar con el microservicio", status_code=503)
    except Exception as e:
        logger.exception(f"[ORQUESTADOR][UNEXPECTED ERROR] {method} {url}: {str(e)}")
        if isinstance(e, OrchestrationError):
            raise
        raise OrchestrationError(f"Error en petición al microservicio: {str(e)}", status_code=500)

def registrar_compra_orquestada(productos_compra, cantidades_compra, auth_token, datos_adicionales=None):
    headers = {'Authorization': auth_token}

    # Paso 1: Obtener info usuario
    usuarios_url = _get_microservice_url('usuarios_y_autenticacion_y_compras')
    usuario_response = _make_request(
        'GET',
        f"{usuarios_url}/api/user/me",
        headers=headers
    )
    usuario_dni = usuario_response.get('dni')
    if not usuario_dni:
        raise OrchestrationError("No se pudo obtener el DNI del usuario", status_code=400)

    # Paso 2: Obtener recetas validadas del usuario
    recetas_url = _get_microservice_url('recetas_y_medicos')
    recetas_response = _make_request(
        'GET',
        f"{recetas_url}/api/recetas/filter",
        headers=headers,
        params={
            'dni': usuario_dni,
            'estado': 'validada',
            'page': 1,
            'pagesize': 100
        }
    )
    recetas_validadas = recetas_response.get('items', [])
    productos_con_receta_validada = set()
    for receta in recetas_validadas:
        for prod in receta.get('productos', []):
            productos_con_receta_validada.add(prod.get('id'))

    # Paso 3: Validar productos y stock
    productos_url = _get_microservice_url('productos_y_ofertas')
    productos_detallados = []
    productos_requieren_receta = []

    for producto_id, cantidad in zip(productos_compra, cantidades_compra):
        producto = _make_request(
            'GET',
            f"{productos_url}/api/productos/{producto_id}",
            headers=headers
        )
        if producto.get('stock', 0) < cantidad:
            raise OrchestrationError(
                f"Stock insuficiente para el producto '{producto.get('nombre')}'. "
                f"Disponible: {producto.get('stock')}, Solicitado: {cantidad}",
                status_code=400
            )
        productos_detallados.append({
            'producto_id': producto_id,
            'cantidad': cantidad,
            'producto': producto
        })
        # Si requiere receta, agregar a lista de comprobación
        if producto.get('requiere_receta'):
            productos_requieren_receta.append({
                'id': producto_id,
                'nombre': producto.get('nombre')
            })

    # Validar que todos los productos que requieren receta estén en alguna receta validada
    productos_sin_receta_validada = [
        prod['nombre'] for prod in productos_requieren_receta
        if prod['id'] not in productos_con_receta_validada
    ]
    if productos_sin_receta_validada:
        raise OrchestrationError(
            f"Los siguientes productos requieren receta médica validada: {', '.join(productos_sin_receta_validada)}",
            status_code=400,
            details={'productos_sin_receta': productos_sin_receta_validada}
        )

    # Paso 4: Actualizar stock en backend de productos
    for prod in productos_detallados:
        producto_id = prod['producto_id']
        cantidad = prod['cantidad']
        _make_request(
            'PUT',
            f"{productos_url}/api/productos/{producto_id}",
            headers=headers,
            json={'stock': prod['producto']['stock'] - cantidad}
        )

    # Paso 5: Registrar la compra en backend de usuarios/compras
    compra_request = {
        'usuarioId': usuario_response.get('id'),
        'productos': [p['producto_id'] for p in productos_detallados],
        'cantidades': [p['cantidad'] for p in productos_detallados]
    }
    if datos_adicionales:
        compra_request.update(datos_adicionales)

    compra_response = _make_request(
        'POST',
        f"{usuarios_url}/api/compras",
        headers=headers,
        json=compra_request
    )

    compra_response['productos_detalle'] = [
        {
            'producto_id': p['producto_id'],
            'cantidad': p['cantidad'],
            'nombre': p['producto'].get('nombre'),
            'precio': p['producto'].get('precio'),
            'tipo': p['producto'].get('tipo'),
            'requiere_receta': bool(p['producto'].get('requiere_receta'))
        }
        for p in productos_detallados
    ]
    return compra_response

def listar_compras_usuario_detalladas(auth_token):
    """
    Obtiene las compras del usuario con detalles de productos y ofertas.

    Args:
        auth_token: Token JWT del usuario

    Returns:
        dict: Compras con detalles completos
    """
    headers = {'Authorization': auth_token}

    # Obtener compras del usuario
    usuarios_url = _get_microservice_url('usuarios_y_autenticacion_y_compras')
    compras_response = _make_request(
        'GET',
        f"{usuarios_url}/api/compras/me",
        headers=headers
    )

    # La respuesta debe ser una lista
    compras = compras_response if isinstance(compras_response, list) else []

    productos_url = _get_microservice_url('productos_y_ofertas')

    for compra in compras:
        productos_ids = compra.get('productos', [])
        cantidades = compra.get('cantidades', [])
        productos_detalle = []

        # Iterar en paralelo productos y cantidades
        for producto_id, cantidad in zip(productos_ids, cantidades):
            try:
                producto = _make_request(
                    'GET',
                    f"{productos_url}/api/productos/{producto_id}",
                    headers=headers
                )
                productos_detalle.append({
                    'producto_id': producto_id,
                    'cantidad': cantidad,
                    'nombre': producto.get('nombre'),
                    'precio': producto.get('precio'),
                    'tipo': producto.get('tipo'),
                    'stock': producto.get('stock')
                })
            except Exception as e:
                logger.warning(f"No se pudo obtener detalle del producto {producto_id}: {str(e)}")
                productos_detalle.append({
                    'producto_id': producto_id,
                    'cantidad': cantidad,
                    'error': 'Producto no disponible'
                })

        compra['productos_detalle'] = productos_detalle

    return {'compras': compras}

def validar_y_actualizar_estado_receta(receta_id, nuevo_estado, auth_token):
    """
    Valida una receta y actualiza su estado:
    1. Obtiene información de la receta
    2. Valida productos existan y coincidan nombre
    3. Valida médico esté colegiado
    4. Valida paciente coincide con token
    5. Actualiza estado

    Args:
        receta_id: ID de la receta
        nuevo_estado: Nuevo estado a asignar
        auth_token: Token JWT

    Returns:
        dict: Receta actualizada
    """

    headers = {'Authorization': auth_token}
    recetas_url = _get_microservice_url('recetas_y_medicos')

    # Paso 1: Obtener información de la receta
    receta = _make_request(
        'GET',
        f"{recetas_url}/api/recetas/{receta_id}",
        headers=headers
    )

    # Paso 2: Validar productos existan y coincidan nombre
    productos_url = _get_microservice_url('productos_y_ofertas')
    productos_receta = receta.get('productos', [])

    for producto in productos_receta:
        producto_id = producto.get('id')
        producto_nombre = producto.get('nombre')
        try:
            producto_info = _make_request(
                'GET',
                f"{productos_url}/api/productos/{producto_id}",
                headers=headers
            )
        except OrchestrationError:
            raise OrchestrationError(
                f"El producto con ID {producto_id} mencionado en la receta no existe",
                status_code=400
            )
        # Validar que el nombre coincide
        if producto_info.get('nombre') != producto_nombre:
            raise OrchestrationError(
                f"Nombre del producto con ID {producto_id} no coincide: '{producto_nombre}' vs '{producto_info.get('nombre')}'",
                status_code=400
            )

    # Paso 4: Validar paciente coincide con el del token
    usuarios_url = _get_microservice_url('usuarios_y_autenticacion_y_compras')
    paciente_dni = receta.get('pacienteDNI') or receta.get('pacientedni')

    usuario_me = _make_request(
        'GET',
        f"{usuarios_url}/api/user/me",
        headers=headers
    )
    usuario_me_dni = str(usuario_me.get('dni'))

    if str(paciente_dni) != usuario_me_dni:
        raise OrchestrationError(
            f"El DNI del usuario autenticado ({usuario_me_dni}) no coincide con el paciente de la receta ({paciente_dni})",
            status_code=400
        )

    # Paso 5: Actualizar estado de la receta
    resultado = _make_request(
        'PUT',
        f"{recetas_url}/api/recetas/{receta_id}/validar",
        headers=headers,
        json={'estadovalidacion': nuevo_estado}
    )

    return {
        'mensaje': 'Receta validada y actualizada exitosamente',
        'receta': resultado,
        'validaciones': {
            'productos_validados': len(productos_receta),
            'medico_valido': True,
            'paciente_valido': True
        }
    }