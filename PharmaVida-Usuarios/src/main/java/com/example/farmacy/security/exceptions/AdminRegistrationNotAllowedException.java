package com.example.farmacy.security.exceptions;

public class AdminRegistrationNotAllowedException extends RuntimeException {
    public AdminRegistrationNotAllowedException(String message) {
        super(message);
    }
}