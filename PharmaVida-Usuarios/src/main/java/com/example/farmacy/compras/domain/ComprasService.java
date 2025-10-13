package com.example.farmacy.compras.domain;

import com.example.farmacy.compras.dto.CompraRequestDto;
import com.example.farmacy.compras.dto.CompraResponseDto;
import com.example.farmacy.compras.infrastructure.ComprasRepository;
import com.example.farmacy.security.exceptions.UserNotFoundException;
import com.example.farmacy.usuario.domain.User;
import com.example.farmacy.usuario.infrastructure.UserRepository;
import com.example.farmacy.utils.SequenceSyncUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class ComprasService {

    @Autowired
    private ComprasRepository comprasRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private SequenceSyncUtil sequenceSyncUtil;

    public Long getUsuarioIdFromDni(String dni) {
        User user = userRepository.findByDni(dni)
                .orElseThrow(() -> new UserNotFoundException("Usuario no encontrado con DNI: " + dni));
        return user.getId();
    }

    public CompraResponseDto registrarCompra(CompraRequestDto dto) {
        sequenceSyncUtil.syncSequence("compras", "id");

        if (!userRepository.existsById(dto.getUsuarioId())) {
            throw new IllegalArgumentException("El usuario no existe");
        }
        if (dto.getProductos() == null || dto.getCantidades() == null ||
                dto.getProductos().size() != dto.getCantidades().size() || dto.getProductos().isEmpty()) {
            throw new IllegalArgumentException("Las listas de productos y cantidades deben ser válidas y del mismo tamaño");
        }

        Compras compra = Compras.builder()
                .usuarioId(dto.getUsuarioId())
                .productos(dto.getProductos())
                .cantidades(dto.getCantidades())
                .fechaCompra(LocalDateTime.now())
                .build();

        Compras saved = comprasRepository.save(compra);

        return new CompraResponseDto(
                saved.getId(),
                saved.getFechaCompra(),
                saved.getUsuarioId(),
                saved.getProductos(),
                saved.getCantidades()
        );
    }

    public List<CompraResponseDto> listarComprasPorUsuario(Long usuarioId) {
        List<Compras> compras = comprasRepository.findByUsuarioId(usuarioId);
        return compras.stream()
                .map(c -> new CompraResponseDto(
                        c.getId(),
                        c.getFechaCompra(),
                        c.getUsuarioId(),
                        c.getProductos(),
                        c.getCantidades()
                ))
                .collect(Collectors.toList());
    }

    public List<CompraResponseDto> listarTodasCompras() {
        List<Compras> compras = comprasRepository.findAll();
        return compras.stream()
                .map(c -> new CompraResponseDto(
                        c.getId(),
                        c.getFechaCompra(),
                        c.getUsuarioId(),
                        c.getProductos(),
                        c.getCantidades()
                ))
                .collect(Collectors.toList());
    }
}
