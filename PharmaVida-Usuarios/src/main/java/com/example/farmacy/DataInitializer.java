package com.example.farmacy;

import com.example.farmacy.usuario.domain.User;
import com.example.farmacy.usuario.domain.UserRole;
import com.example.farmacy.usuario.infrastructure.UserRepository;
import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Component
public class DataInitializer {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Value("${admin.email}")
    private String adminEmail;

    @Value("${admin.password}")
    private String adminPassword;

    @Value("${admin.firstName}")
    private String adminFirstName;

    @Value("${admin.lastName}")
    private String adminLastName;

    @Value("${admin.dni}")
    private String adminDni;

    @PostConstruct
    public void initializeData() {
        if (!userRepository.existsByEmail(adminEmail)) {
            User admin = User.builder()
                    .nombre(adminFirstName)
                    .apellido(adminLastName)
                    .email(adminEmail)
                    .password(passwordEncoder.encode(adminPassword))
                    .dni(adminDni)
                    .role(UserRole.ADMIN)
                    .distrito("San Borja")
                    .build();
            userRepository.save(admin);
            System.out.println("Usuario administrador creado por defecto: " + adminEmail);
        } else {
            System.out.println("Usuario administrador ya existe: " + adminEmail);
        }
    }
}