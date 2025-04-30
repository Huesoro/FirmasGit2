import azure.functions as func
import uuid
import datetime
import base64
import io
import json
from docx import Document

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

def generar_documento_desde_base64(datos):
    doc_id = str(uuid.uuid4())
    fecha = datetime.date.today().strftime("%d de %B de %Y")

    # Leer contenido base64 del machote
    base64_bytes = datos.get("contenido_docx_base64").encode("utf-8")
    docx_bytes = base64.b64decode(base64_bytes)
    docx_stream = io.BytesIO(docx_bytes)
    doc = Document(docx_stream)

    # Rellenar los campos del machote
    for p in doc.paragraphs:
        for r in p.runs:
            r.text = r.text.replace("{fecha_donacion}", fecha)
            r.text = r.text.replace("{nombre_donante}", datos.get("nombre_donante", ""))
            r.text = r.text.replace("{monto_donado}", str(datos.get("monto_donado", "")))
            r.text = r.text.replace("{lista_articulos}", datos.get("lista_articulos", ""))
            r.text = r.text.replace("{nombre_receptor}", datos.get("nombre_receptor", ""))
            r.text = r.text.replace("{nombre_finanzas}", datos.get("nombre_finanzas", ""))
            r.text = r.text.replace("{nombre_inventario}", datos.get("nombre_inventario", ""))
            r.text = r.text.replace("{nombre_dueno}", datos.get("nombre_dueno", ""))

    # Guardar el archivo resultante en memoria
    output_stream = io.BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)

    # Codificar en base64 para enviar de regreso
    docx_base64 = base64.b64encode(output_stream.read()).decode("utf-8")

    return {
        "id_documento": doc_id,
        "fecha": fecha,
        "contenido_base64": docx_base64
    }

@app.route(route="CrearDoc", methods=["POST"])
def crear_doc(req: func.HttpRequest) -> func.HttpResponse:
    try:
        datos = req.get_json()
        resultado = generar_documento_desde_base64(datos)
        return func.HttpResponse(
            body=json.dumps(resultado),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(
            f"Error al procesar documento: {str(e)}",
            status_code=500
        )


