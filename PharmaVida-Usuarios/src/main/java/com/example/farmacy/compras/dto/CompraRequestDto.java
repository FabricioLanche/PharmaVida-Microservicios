package com.example.farmacy.compras.dto;

import lombok.*;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class CompraRequestDto {
    private Long usuarioId;
    private List<Long> productos;
    private List<Integer> cantidades;
}