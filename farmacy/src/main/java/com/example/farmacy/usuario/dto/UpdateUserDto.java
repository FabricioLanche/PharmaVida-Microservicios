package com.example.farmacy.usuario.dto;

import jakarta.validation.constraints.Email;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UpdateUserDto {

    private String nombre;

    private String apellido;

    private String distrito;

    @Email(message = "El email debe ser válido")
    private String email;

    private String password;
}