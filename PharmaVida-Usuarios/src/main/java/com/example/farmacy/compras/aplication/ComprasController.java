package com.example.farmacy.compras.aplication;

import com.example.farmacy.compras.domain.ComprasService;
import com.example.farmacy.compras.dto.CompraRequestDto;
import com.example.farmacy.compras.dto.CompraResponseDto;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/compras")
public class ComprasController {

    @Autowired
    private ComprasService comprasService;

    @PreAuthorize("hasAnyRole('CLIENTE', 'ADMIN')")
    @PostMapping
    public ResponseEntity<CompraResponseDto> registrarCompra(
            @AuthenticationPrincipal UserDetails userDetails,
            @RequestBody CompraRequestDto dto) {
        Long usuarioId = comprasService.getUsuarioIdFromDni(userDetails.getUsername());
        dto.setUsuarioId(usuarioId);
        CompraResponseDto compra = comprasService.registrarCompra(dto);
        return ResponseEntity.ok(compra);
    }

    @PreAuthorize("hasAnyRole('CLIENTE', 'ADMIN')")
    @GetMapping("/me")
    public ResponseEntity<List<CompraResponseDto>> listarMisCompras(
            @AuthenticationPrincipal UserDetails userDetails) {
        Long usuarioId = comprasService.getUsuarioIdFromDni(userDetails.getUsername());
        List<CompraResponseDto> compras = comprasService.listarComprasPorUsuario(usuarioId);
        return ResponseEntity.ok(compras);
    }

    @PreAuthorize("hasRole('ADMIN')")
    @GetMapping("/all")
    public ResponseEntity<List<CompraResponseDto>> listarTodas() {
        List<CompraResponseDto> compras = comprasService.listarTodasCompras();
        return ResponseEntity.ok(compras);
    }
}
