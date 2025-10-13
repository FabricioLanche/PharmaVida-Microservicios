package com.example.farmacy.security.application;

import com.example.farmacy.security.domain.AuthService;
import com.example.farmacy.security.dto.LoginRequestDto;
import com.example.farmacy.security.dto.LoginResponseDto;
import com.example.farmacy.security.dto.RegisterRequestDto;
import com.example.farmacy.security.dto.RegisterResponseDto;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @Autowired
    private AuthService authService;

    @PostMapping("/login")
    public ResponseEntity<LoginResponseDto> login(@Valid @RequestBody LoginRequestDto loginRequest) {
        LoginResponseDto response = authService.login(loginRequest);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/register")
    public ResponseEntity<RegisterResponseDto> register(@Valid @RequestBody RegisterRequestDto registerRequest) {
        RegisterResponseDto response = authService.register(registerRequest);
        return ResponseEntity.ok(response);
    }
}