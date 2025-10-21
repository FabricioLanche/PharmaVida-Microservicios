const Receta = require('../models/recetaModel');
const Medico = require('../models/medicosModel');
const AWS = require('aws-sdk');
const { v4: uuidv4 } = require('uuid');
const path = require('path');
const axios = require('axios');
require('dotenv').config();

AWS.config.update({ region: 'us-east-1' });
const s3 = new AWS.S3();
const textract = new AWS.Textract();

// Función auxiliar para extraer texto y campos desde PDF usando Textract
async function extraerCamposDesdePDF(buffer, textract) {
    const params = {
        Document: {
            Bytes: buffer
        }
    };

    // Textract detectDocumentText solo soporta PDFs de hasta 5 páginas
    const data = await textract.detectDocumentText(params).promise();
    const texto = (data.Blocks || [])
        .filter(block => block.BlockType === 'LINE')
        .map(block => block.Text)
        .join('\n');

    // Regex para extraer campos principales
    const pacienteDNI = (texto.match(/Paciente DNI:\s*(\d{8,12})/) || [])[1];
    const medicoCMP = (texto.match(/Médico CMP:\s*([A-Za-z0-9]+)/) || [])[1];
    const fechaEmision = (texto.match(/Fecha de emisión:\s*([\d\-]+)/) || [])[1];

    // Extraer productos del bloque Productos
    const productos = [];
    const productosStart = texto.indexOf('Productos:');
    let productosBloque = '';
    if (productosStart !== -1) {
        let productosEnd = texto.indexOf('Observaciones:', productosStart);
        if (productosEnd === -1) productosEnd = texto.length;
        productosBloque = texto.substring(productosStart, productosEnd);
    }
    // Regex exacto para tu formato
    const productoRegex = /- Código:\s*(\d+),\s*Nombre:\s*([^,]+),\s*Cantidad:\s*(\d+)/g;
    let prodMatch;
    while ((prodMatch = productoRegex.exec(productosBloque)) !== null) {
        productos.push({
            id: Number(prodMatch[1]),              // Código como id (number)
            nombre: prodMatch[2].trim(),
            cantidad: Number(prodMatch[3])
        });
    }

    return { pacienteDNI, medicoCMP, fechaEmision, productos };
}

const recetasService = {
    // Listar recetas con filtros y paginación
    async listarRecetas(req, res) {
        try {
            const {
                dni,
                cmp,
                estado,
                page = '1',
                pagesize = '10'
            } = req.query;

            const filtro = {};
            if (dni) filtro.pacienteDNI = String(dni);
            if (cmp) filtro.medicoCMP = String(cmp);
            if (estado) filtro.estadoValidacion = String(estado);

            const pagina = Math.max(parseInt(page, 10) || 1, 1);
            const tamano = Math.min(Math.max(parseInt(pagesize, 10) || 10, 1), 100);

            // Ordenar por fecha de creación descendente por defecto
            const sortObj = { createdAt: -1 };

            const [items, total] = await Promise.all([
                Receta.find(filtro)
                    .sort(sortObj)
                    .skip((pagina - 1) * tamano)
                    .limit(tamano),
                Receta.countDocuments(filtro)
            ]);

            res.json({
                page: pagina,
                pagesize: tamano,
                total,
                items
            });
        } catch (error) {
            res.status(500).json({ error: 'Error al listar recetas', detalle: error.message });
        }
    },

    // Subir receta PDF
    async subirReceta(req, res) {
        try {
            if (!req.file) {
                return res.status(400).json({ error: 'Falta archivo PDF (campo archivoPDF)' });
            }

            // Subir PDF a S3
            const fileExtension = path.extname(req.file.originalname);
            const fileName = `recetas/${uuidv4()}${fileExtension}`;
            const bucket = process.env.AWS_S3_BUCKET || process.env.BUCKET_NAME;
            if (!bucket) {
                return res.status(500).json({ error: 'Falta configuración del bucket S3' });
            }
            const params = {
                Bucket: bucket,
                Key: fileName,
                Body: req.file.buffer,
                ContentType: req.file.mimetype,
            };
            await s3.upload(params).promise();
            
            // Construir URL completa del PDF
            const region = process.env.AWS_REGION || 'us-east-1';
            const archivoPDF = `https://${bucket}.s3.${region}.amazonaws.com/${fileName}`;

            // Extraer campos desde el PDF usando Textract
            const { pacienteDNI, medicoCMP, fechaEmision, productos } = await extraerCamposDesdePDF(req.file.buffer, textract);

            // Validar datos extraídos
            if (!pacienteDNI || !medicoCMP || !fechaEmision || productos.length === 0) {
                return res.status(400).json({
                    error: 'No se encontraron todos los campos requeridos en el PDF',
                    detalle: { pacienteDNI, medicoCMP, fechaEmision, productos }
                });
            }

            // Crear entrada en MongoDB
            const nuevaReceta = new Receta({
                pacienteDNI,
                medicoCMP,
                fechaEmision,
                productos,
                archivoPDF,
                estadoValidacion: 'pendiente'
            });

            await nuevaReceta.save();
            res.status(201).json({ mensaje: 'Receta subida correctamente', receta: nuevaReceta });
        } catch (error) {
            res.status(500).json({ error: 'Error al subir la receta', detalle: error.message });
        }
    },

    async validarRecetaPorId(req, res) {
        try {
            const recetaId = req.params.id;
            console.log(`[VALIDAR] Iniciando validación para receta ID: ${recetaId}`);

            if (!recetaId.match(/^[0-9a-fA-F]{24}$/)) {
                return res.status(400).json({ error: 'ID de receta inválido' });
            }

            // Buscar la receta por id
            const receta = await Receta.findById(recetaId);
            if (!receta) {
                console.log(`[VALIDAR] Receta no encontrada: ${recetaId}`);
                return res.status(404).json({ error: 'Receta no encontrada' });
            }

            console.log(`[VALIDAR] Receta encontrada. archivoPDF: ${receta.archivoPDF}`);

            if (!receta.archivoPDF) {
                return res.status(400).json({ error: 'La receta no tiene archivo PDF asociado.' });
            }

            // Extraer la clave del archivo desde la URL
            const key = receta.archivoPDF.includes('amazonaws.com/') 
                ? receta.archivoPDF.split('amazonaws.com/')[1]
                : receta.archivoPDF;

            console.log(`[VALIDAR] Clave extraída del S3: ${key}`);

            // Descargar el PDF desde S3
            const bucket = process.env.AWS_S3_BUCKET || process.env.BUCKET_NAME;
            console.log(`[VALIDAR] Descargando desde bucket: ${bucket}, key: ${key}`);
            
            const params = { Bucket: bucket, Key: key };
            const s3Object = await s3.getObject(params).promise();
            const pdfBuffer = s3Object.Body;
            
            console.log(`[VALIDAR] PDF descargado correctamente. Tamaño: ${pdfBuffer.length} bytes`);

            // Extraer los campos desde el PDF usando Textract
            console.log(`[VALIDAR] Iniciando extracción con Textract...`);
            const { pacienteDNI, medicoCMP, fechaEmision, productos } = await extraerCamposDesdePDF(pdfBuffer, textract);

            console.log(`[VALIDAR] Datos extraídos - DNI: ${pacienteDNI}, CMP: ${medicoCMP}, Fecha: ${fechaEmision}, Productos: ${productos.length}`);

            // Validar los campos extraídos
            if (
                !pacienteDNI ||
                !medicoCMP ||
                !fechaEmision ||
                !Array.isArray(productos) ||
                productos.length === 0
            ) {
                return res.status(400).json({ error: 'PDF incompleto o inválido', detalle: { pacienteDNI, medicoCMP, fechaEmision, productos } });
            }

            // Validar productos (id, nombre, cantidad)
            for (const prod of productos) {
                if (
                    typeof prod.id !== 'number' ||
                    !prod.nombre || typeof prod.nombre !== 'string' ||
                    typeof prod.cantidad !== 'number' || prod.cantidad <= 0
                ) {
                    return res.status(400).json({ error: 'Producto inválido en el PDF', detalle: prod });
                }
            }

            // Validar CMP en la base de datos
            console.log(`[VALIDAR] Validando CMP: ${medicoCMP}`);
            const medico = await Medico.findOne({ cmp: medicoCMP, colegiaturaValida: true });
            if (!medico) {
                return res.status(400).json({ error: 'CMP no registrado o colegiatura no válida' });
            }

            // Regla de validez temporal
            const emision = new Date(fechaEmision);
            const ahora = new Date();
            if (emision > ahora) {
                return res.status(400).json({ error: 'La fecha de emisión no puede ser futura' });
            }
            const msPorDia = 24 * 60 * 60 * 1000;
            const diasTranscurridos = Math.floor((ahora - emision) / msPorDia);
            const VALIDEZ_DIAS = Number(process.env.RECETA_VALIDEZ_DIAS || 30);
            if (diasTranscurridos > VALIDEZ_DIAS) {
                return res.status(400).json({ error: `La receta ha expirado (validez ${VALIDEZ_DIAS} días)` });
            }

            // Actualiza la receta en la base de datos con los datos extraídos y estado validada
            console.log(`[VALIDAR] Actualizando receta a estado 'validada'`);
            const recetaActualizada = await Receta.findByIdAndUpdate(
                recetaId,
                {
                    pacienteDNI,
                    medicoCMP,
                    fechaEmision,
                    productos,
                    estadoValidacion: 'validada'
                },
                { new: true, runValidators: true }
            );

            console.log(`[VALIDAR] Validación completada exitosamente para receta ID: ${recetaId}`);
            res.json({ mensaje: 'Receta validada y actualizada correctamente', receta: recetaActualizada });
        } catch (error) {
            console.error('[ERROR] validarRecetaPorId:', error);
            console.error('[ERROR] Stack:', error.stack);
            res.status(500).json({ 
                error: 'Error al validar la receta', 
                detalle: error.message,
                codigo: error.code || 'UNKNOWN'
            });
        }
    },

    // Eliminar archivo PDF de una receta
    async eliminarArchivoReceta(req, res) {
        try {
            const recetaId = req.params.id;
            if (!recetaId.match(/^[0-9a-fA-F]{24}$/)) {
                return res.status(400).json({ error: 'ID de receta inválido' });
            }

            const receta = await Receta.findById(recetaId);
            if (!receta) return res.status(404).json({ error: 'Receta no encontrada' });

            if (!receta.archivoPDF) {
                return res.status(400).json({ error: 'No hay archivo para eliminar' });
            }

            // Extraer la clave del archivo desde la URL
            const key = receta.archivoPDF.includes('amazonaws.com/') 
                ? receta.archivoPDF.split('amazonaws.com/')[1]
                : receta.archivoPDF;
                
            const bucket = process.env.AWS_S3_BUCKET || process.env.BUCKET_NAME;
            if (!bucket) {
                return res.status(500).json({ error: 'Falta configuración del bucket S3' });
            }
            const params = { Bucket: bucket, Key: key };
            await s3.deleteObject(params).promise();

            // Eliminar el registro completo de la base de datos
            await Receta.findByIdAndDelete(recetaId);

            res.json({ 
                mensaje: 'Receta y archivo eliminados exitosamente',
                id: recetaId
            });
        } catch (error) {
            res.status(500).json({ error: 'Error al eliminar la receta', detalle: error.message });
        }
    },

    async obtenerRecetaPorId(req, res) {
        try {
            const { id } = req.params;
            if (!id.match(/^[0-9a-fA-F]{24}$/)) {
                return res.status(400).json({ error: 'ID de receta inválido' });
            }
            const receta = await Receta.findById(id);
            if (!receta) return res.status(404).json({ error: 'Receta no encontrada' });

            let pdfUrl = null;
            if (receta.archivoPDF) {
                // Extraer la clave del archivo desde la URL
                const key = receta.archivoPDF.includes('amazonaws.com/') 
                    ? receta.archivoPDF.split('amazonaws.com/')[1]
                    : receta.archivoPDF;
                    
                const bucket = process.env.AWS_S3_BUCKET || process.env.BUCKET_NAME;
                if (bucket) {
                    const params = {
                        Bucket: bucket,
                        Key: key
                    };
                    pdfUrl = await s3.getSignedUrlPromise('getObject', params);
                }
            }

            res.json({
                ...receta.toObject(),
                pdfUrl
            });
        } catch (error) {
            console.error('[ERROR] obtenerRecetaPorId:', error);
            res.status(500).json({ error: 'Error al obtener la receta', detalle: error.message });
        }
    },

};

module.exports = recetasService;