require('dotenv').config();
const AWS = require('aws-sdk');
const fs = require('fs');

// Configura Textract con las credenciales del .env
const textract = new AWS.Textract({
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    sessionToken: process.env.AWS_SESSION_TOKEN,
    region: 'us-east-1'
});

const sts = new AWS.STS({
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    sessionToken: process.env.AWS_SESSION_TOKEN,
    region: process.env.AWS_REGION || 'us-west-1'
});

sts.getCallerIdentity({}, function(err, data) {
    if (err) {
        console.error('Error getCallerIdentity:', err);
    } else {
        console.log('--- AWS CONTEXT ---');
        console.log('AWS ARN:', data.Arn);
        console.log('AWS Account:', data.Account);
        console.log('AWS UserId:', data.UserId);
        console.log('-------------------');
    }
});

// Cambia aquí el nombre de tu PDF de prueba
const filePath = './Receta Médica Digital.pdf';

// Lee el PDF como buffer
const fileBytes = fs.readFileSync(filePath);

// Prepara los parámetros para Textract
const params = {
    Document: {
        Bytes: fileBytes
    }
};

// Ejecuta Textract detectDocumentText
textract.detectDocumentText(params, (err, data) => {
    if (err) {
        console.error('Error en Textract:', err);
    } else {
        // Extrae las líneas de texto
        const textoExtraido = (data.Blocks || [])
            .filter(block => block.BlockType === 'LINE')
            .map(block => block.Text)
            .join('\n');
        console.log('Texto extraído por Textract:\n');
        console.log(textoExtraido);
    }
});