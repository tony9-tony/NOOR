package com.rushmotors.dto;

public class AuthResponse {
    private final String message;
    private final String username;
    private final String email;

    public AuthResponse(String message, String username, String email) {
        this.message = message;
        this.username = username;
        this.email = email;
    }

    public String getMessage() {
        return message;
    }

    public String getUsername() {
        return username;
    }

    public String getEmail() {
        return email;
    }
}
