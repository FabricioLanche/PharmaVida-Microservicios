package com.example.farmacy.compras.infrastructure;

import com.example.farmacy.compras.domain.Compras;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ComprasRepository extends JpaRepository<Compras, Long> {
    List<Compras> findByUsuarioId(Long usuarioId);
    List<Compras> findByProductosContaining(Long productoId);
}
