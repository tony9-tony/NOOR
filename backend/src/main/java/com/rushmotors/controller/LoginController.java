package com.rushmotors.controller;

import com.rushmotors.dto.LoginRequest;
import com.rushmotors.model.LoginRecord;
import com.rushmotors.repository.LoginRecordRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*")
public class LoginController {

    private final LoginRecordRepository repository;
    private final BCryptPasswordEncoder passwordEncoder;

    public LoginController(LoginRecordRepository repository) {
        this.repository = repository;
        this.passwordEncoder = new BCryptPasswordEncoder();
    }

    @PostMapping("/signup")
    public ResponseEntity<String> signup(@RequestBody LoginRequest request) {
        return saveRecord(request, "signup", "Signup data saved successfully");
    }

    @PostMapping("/login")
    public ResponseEntity<String> login(@RequestBody LoginRequest request) {
        return saveRecord(request, "login", "Login data saved successfully");
    }

    private ResponseEntity<String> saveRecord(LoginRequest request, String action, String successMessage) {
        if (request.getUsername() == null || request.getUsername().trim().isEmpty()
                || request.getEmail() == null || request.getEmail().trim().isEmpty()
                || request.getPassword() == null || request.getPassword().trim().isEmpty()) {
            return ResponseEntity.badRequest().body("Username, email, and password are required.");
        }

        String hashedPassword = passwordEncoder.encode(request.getPassword());
        LoginRecord record = new LoginRecord(request.getUsername().trim(), request.getEmail().trim(), hashedPassword, action);
        repository.save(record);
        return ResponseEntity.ok(successMessage);
    }
}
