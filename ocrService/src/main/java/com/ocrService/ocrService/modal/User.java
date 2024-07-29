package com.ocrService.ocrService.modal;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Builder
@Data
@AllArgsConstructor
@NoArgsConstructor
public class User {
    @Id
    @GeneratedValue
    private Long id;
    private String lastName;
    private String firstName;
    private String address;
    private String numbers;
    private String serialDate;
    private String region;
    private String serial;
    private String religion;
    private String status;
    private String deadline;
    private String gender;
    private String job;
    private String birthday;
    private String nationality;
    private String fullName;
}
