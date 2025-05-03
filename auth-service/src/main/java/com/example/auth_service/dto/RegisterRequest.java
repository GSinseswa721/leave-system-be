package com.example.auth_service.dto;

import lombok.Data;

@Data
public class RegisterRequest {
    private String email;
    private String password;
    private String name;
    private String department;
    private String profilePicture;
}
