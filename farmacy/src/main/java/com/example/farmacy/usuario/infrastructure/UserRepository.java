package com.example.farmacy.usuario.infrastructure;

import com.example.farmacy.usuario.domain.User;
import jakarta.validation.constraints.NotBlank;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
    boolean existsByEmail(String email);
    Optional<User> findByDni(String dni);

    boolean existsByDni(@NotBlank(message = "El dni es obligatorio") String dni);
}