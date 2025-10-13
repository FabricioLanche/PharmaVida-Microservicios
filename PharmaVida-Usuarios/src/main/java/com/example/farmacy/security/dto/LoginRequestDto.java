package com.example.farmacy.security.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class LoginRequestDto {
    @Email(message = "Formato de email inválido")
    private String email;

    private String dni;

    @NotBlank(message = "La constraseña es obligatoria")
    private String password;
}