package com.example.farmacy.compras.dto;

import lombok.*;

import java.time.LocalDateTime;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class CompraResponseDto {
    private Long id;
    private LocalDateTime fechaCompra;
    private Long usuarioId;
    private List<Long> productos;
    private List<Integer> cantidades;
}