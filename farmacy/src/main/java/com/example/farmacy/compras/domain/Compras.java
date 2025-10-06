package com.example.farmacy.compras.domain;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "compras")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Compras {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private LocalDateTime fechaCompra;

    @Column(nullable = false)
    private Long usuarioId;

    @ElementCollection
    @CollectionTable(name = "compra_productos", joinColumns = @JoinColumn(name = "compra_id"))
    @Column(name = "producto_id")
    private List<Long> productos;

    @ElementCollection
    @CollectionTable(name = "compra_cantidades", joinColumns = @JoinColumn(name = "compra_id"))
    @Column(name = "cantidad")
    private List<Integer> cantidades;
}