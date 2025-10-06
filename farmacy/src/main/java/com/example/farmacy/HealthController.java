package com.example.farmacy;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("")
public class HealthController {

    @GetMapping("/echo")
    public ResponseEntity<Map<String, Object>> echo() {
        Map<String, Object> response = new HashMap<>();
        response.put("message", "¡Hola! El servidor está funcionando correctamente");
        response.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        response.put("status", "UP");

        return ResponseEntity.ok(response);
    }
}