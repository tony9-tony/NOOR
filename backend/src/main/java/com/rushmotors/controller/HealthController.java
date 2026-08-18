package com.rushmotors.controller;

import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
@CrossOrigin(originPatterns = {
        "http://localhost:*",
        "http://127.0.0.1:*",
        "http://0.0.0.0:*",
        "http://192.168.*:*",
        "http://10.*:*",
        "http://172.*.*:*",
        "https://*.ngrok-free.app",
        "https://*.ngrok.io"
}, allowCredentials = "true")
public class HealthController {
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of("status", "ok", "service", "rush-motors-backend"));
    }
}
