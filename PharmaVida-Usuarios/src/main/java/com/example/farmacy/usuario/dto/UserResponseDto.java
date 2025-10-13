package com.example.farmacy.usuario.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserResponseDto {
    private String dni;
    private String email;
    private String nombre;
    private String apellido;
    private String role;
    private String distrito;
}