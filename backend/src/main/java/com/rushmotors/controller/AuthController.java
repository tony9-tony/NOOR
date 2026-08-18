package com.rushmotors.controller;

import com.rushmotors.dto.AuthRequest;
import com.rushmotors.dto.AuthResponse;
import com.rushmotors.model.User;
import com.rushmotors.repository.UserRepository;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
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
public class AuthController {
    private final UserRepository userRepository;
    private final BCryptPasswordEncoder passwordEncoder;

    public AuthController(UserRepository userRepository) {
        this.userRepository = userRepository;
        this.passwordEncoder = new BCryptPasswordEncoder();
    }

    @PostMapping("/auth/signup")
    public ResponseEntity<?> signup(@RequestBody AuthRequest request) {
        try {
            if (request == null) {
                return ResponseEntity.badRequest().body(new AuthResponse("Request body is required.", null, null));
            }

            String username = request.getUsername() == null ? "" : request.getUsername().trim();
            String email = request.getEmail() == null ? "" : request.getEmail().trim();
            String password = request.getPassword() == null ? "" : request.getPassword();

            if (username.isEmpty() || email.isEmpty() || password.isEmpty()) {
                return ResponseEntity.badRequest().body(new AuthResponse("Username, email, and password are required.", null, null));
            }

            if (userRepository.existsByEmail(email)) {
                return ResponseEntity.status(HttpStatus.CONFLICT).body(new AuthResponse("Email already registered.", null, null));
            }

            if (userRepository.existsByUsername(username)) {
                return ResponseEntity.status(HttpStatus.CONFLICT).body(new AuthResponse("Username already taken.", null, null));
            }

            String passwordHash = passwordEncoder.encode(password);
            User user = new User(username, email, passwordHash);
            userRepository.save(user);

            return ResponseEntity.status(HttpStatus.CREATED).body(new AuthResponse("Signup successful.", username, email));
        } catch (Exception ex) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(new AuthResponse("Server error during signup.", null, null));
        }
    }

    @PostMapping("/auth/login")
    public ResponseEntity<?> login(@RequestBody AuthRequest request) {
        try {
            if (request == null) {
                return ResponseEntity.badRequest().body(new AuthResponse("Request body is required.", null, null));
            }

            String email = request.getEmail() == null ? "" : request.getEmail().trim();
            String username = request.getUsername() == null ? "" : request.getUsername().trim();
            String password = request.getPassword() == null ? "" : request.getPassword();

            if ((email.isEmpty() && username.isEmpty()) || password.isEmpty()) {
                return ResponseEntity.badRequest().body(new AuthResponse("Email or username and password are required.", null, null));
            }

            User user = null;

            if (!email.isEmpty()) {
                user = userRepository.findByEmail(email).orElse(null);
            } else {
                user = userRepository.findByUsername(username).orElse(null);
            }

            if (user == null) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(new AuthResponse("Invalid credentials.", null, null));
            }

            if (!passwordEncoder.matches(password, user.getPasswordHash())) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(new AuthResponse("Invalid credentials.", null, null));
            }

            return ResponseEntity.ok(new AuthResponse("Login successful.", user.getUsername(), user.getEmail()));
        } catch (Exception ex) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(new AuthResponse("Server error during login.", null, null));
        }
    }
}
