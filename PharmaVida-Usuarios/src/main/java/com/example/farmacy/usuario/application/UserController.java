package com.example.farmacy.usuario.application;

import com.example.farmacy.usuario.domain.UserService;
import com.example.farmacy.usuario.dto.UpdateUserDto;
import com.example.farmacy.usuario.dto.UserResponseDto;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/user")
public class UserController {

    @Autowired
    private UserService userService;

    @PreAuthorize("hasRole('ADMIN')")
    @GetMapping("/all")
    public ResponseEntity<List<UserResponseDto>> getAllUsers() {
        List<UserResponseDto> users = userService.getAllUsers();
        return ResponseEntity.ok(users);
    }

    @PreAuthorize("hasAnyRole('CLIENTE', 'ADMIN')")
    @GetMapping("/me")
    public ResponseEntity<UserResponseDto> getMe(@AuthenticationPrincipal UserDetails userDetails) {
        UserResponseDto response = userService.getMe(userDetails.getUsername());
        return ResponseEntity.ok(response);
    }

    @PreAuthorize("hasAnyRole('CLIENTE', 'ADMIN')")
    @PutMapping("/me")
    public ResponseEntity<UserResponseDto> updateProfile(
            @AuthenticationPrincipal UserDetails userDetails,
            @Valid @RequestBody UpdateUserDto updateUserDto) {
        UserResponseDto response = userService.updateProfile(userDetails.getUsername(), updateUserDto);
        return ResponseEntity.ok(response);
    }

    @PreAuthorize("hasRole('CLIENTE')")
    @DeleteMapping("/me")
    public ResponseEntity<Void> deleteAccount(@AuthenticationPrincipal UserDetails userDetails) {
        userService.deleteAccount(userDetails.getUsername());
        return ResponseEntity.noContent().build();
    }
}