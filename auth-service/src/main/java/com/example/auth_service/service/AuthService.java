package com.example.auth_service.service;

import com.example.auth_service.dto.LoginRequest;
import com.example.auth_service.dto.RegisterRequest;
import com.example.auth_service.dto.UserResponse;
import com.example.auth_service.exception.AuthenticationException;
import com.example.auth_service.model.User;
import com.example.auth_service.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import javax.validation.Valid;
import java.util.Arrays;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public UserResponse register(@Valid RegisterRequest request) {
        validateRegistrationRequest(request);
        
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new AuthenticationException("Email already in use");
        }

        User user = User.builder()
                .email(request.getEmail())
                .password(passwordEncoder.encode(request.getPassword()))
                .name(request.getName())
                .department(request.getDepartment())
                .profilePicture(request.getProfilePicture())
                .roles(Arrays.asList("USER"))
                .build();

        User savedUser = userRepository.save(user);
        String token = jwtService.generateToken(savedUser);
        return mapToUserResponse(savedUser, token);
    }

    public UserResponse login(@Valid LoginRequest request) {
        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new AuthenticationException("Invalid email or password"));
        
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new AuthenticationException("Invalid email or password");
        }
        
        String token = jwtService.generateToken(user);
        return mapToUserResponse(user, token);
    }

    public UserResponse validateToken(String token) {
        if (!StringUtils.hasText(token)) {
            throw new AuthenticationException("Token is required");
        }

        String email = jwtService.extractUsername(token);
        if (!jwtService.isTokenValid(token)) {
            throw new AuthenticationException("Invalid or expired token");
        }

        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new AuthenticationException("User not found"));
        
        return mapToUserResponse(user, token);
    }

    private UserResponse mapToUserResponse(User user, String token) {
        return UserResponse.builder()
                .id(user.getId())
                .email(user.getEmail())
                .name(user.getName())
                .roles(user.getRoles())
                .department(user.getDepartment())
                .profilePicture(user.getProfilePicture())
                .token(token)
                .build();
    }

    private void validateRegistrationRequest(RegisterRequest request) {
        if (!StringUtils.hasText(request.getEmail()) || !request.getEmail().contains("@")) {
            throw new AuthenticationException("Invalid email format");
        }
        if (!StringUtils.hasText(request.getPassword()) || request.getPassword().length() < 6) {
            throw new AuthenticationException("Password must be at least 6 characters long");
        }
        if (!StringUtils.hasText(request.getName())) {
            throw new AuthenticationException("Name is required");
        }
    }
}