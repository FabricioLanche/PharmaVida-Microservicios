package com.example.farmacy.security.domain;

import com.example.farmacy.security.dto.LoginRequestDto;
import com.example.farmacy.security.dto.LoginResponseDto;
import com.example.farmacy.security.dto.RegisterRequestDto;
import com.example.farmacy.security.dto.RegisterResponseDto;
import com.example.farmacy.security.exceptions.AuthenticationFailedException;
import com.example.farmacy.security.exceptions.RegistrationException;
import com.example.farmacy.security.exceptions.UserAlreadyExistsException;
import com.example.farmacy.security.exceptions.UserNotFoundException;
import com.example.farmacy.usuario.domain.User;
import com.example.farmacy.usuario.domain.UserRole;
import com.example.farmacy.usuario.infrastructure.UserRepository;
import com.example.farmacy.utils.SequenceSyncUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.util.Optional;

@Service
public class AuthService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private SequenceSyncUtil sequenceSyncUtil;

    public LoginResponseDto login(LoginRequestDto loginRequest) {
        try {
            Optional<User> userOptional;

            if (StringUtils.hasText(loginRequest.getEmail())) {
                userOptional = userRepository.findByEmail(loginRequest.getEmail());
            } else if (StringUtils.hasText(loginRequest.getDni())) {
                userOptional = userRepository.findByDni(loginRequest.getDni());
            } else {
                throw new UserNotFoundException("Debe proporcionar email o dni");
            }

            if (userOptional.isEmpty()) {
                throw new UserNotFoundException("Usuario no encontrado");
            }

            User user = userOptional.get();

            if (!passwordEncoder.matches(loginRequest.getPassword(), user.getPassword())) {
                throw new AuthenticationFailedException("Contraseña incorrecta");
            }

            String token = jwtUtil.generateToken(user.getDni(), user.getRole().name());
            return new LoginResponseDto(token);

        } catch (UserNotFoundException | AuthenticationFailedException e) {
            throw e;
        } catch (Exception e) {
            throw new AuthenticationFailedException("Error en el proceso de autenticación", e);
        }
    }

    public RegisterResponseDto register(RegisterRequestDto registerRequest) {

        sequenceSyncUtil.syncSequence("users", "id");

        try {
            if (userRepository.existsByEmail(registerRequest.getEmail())) {
                throw new UserAlreadyExistsException("Ya existe un usuario con el email: " + registerRequest.getEmail());
            }

            if (userRepository.existsByDni(registerRequest.getDni())) {
                throw new UserAlreadyExistsException("Ya existe un usuario con el DNI: " + registerRequest.getDni());
            }

            User newUser = User.builder()
                    .nombre(registerRequest.getNombre())
                    .apellido(registerRequest.getApellido())
                    .email(registerRequest.getEmail())
                    .password(passwordEncoder.encode(registerRequest.getPassword()))
                    .dni(registerRequest.getDni())
                    .role(UserRole.CLIENTE)
                    .distrito(registerRequest.getDistrito())
                    .build();

            User savedUser = userRepository.save(newUser);

            String token = jwtUtil.generateToken(savedUser.getDni(), savedUser.getRole().name());
            return new RegisterResponseDto(token);

        } catch (UserAlreadyExistsException e) {
            throw e;
        } catch (Exception e) {
            throw new RegistrationException("Error en el proceso de registro", e);
        }
    }
}