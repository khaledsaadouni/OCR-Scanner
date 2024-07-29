package com.ocrService.ocrService.dto;

import com.ocrService.ocrService.modal.User;
import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class UserDto {
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
    private String nationality;
    private String gender;
    private String birthday;
    private String job;
    private String fullName;
    public static UserDto fromEntity(User user) {
        return UserDto.builder()
                .id(user.getId())
                .lastName(user.getLastName())
                .firstName(user.getFirstName())
                .address(user.getAddress())
                .numbers(user.getNumbers())
                .serialDate(user.getSerialDate())
                .region(user.getRegion())
                .serial(user.getSerial())
                .religion(user.getReligion())
                .status(user.getStatus())
                .deadline(user.getDeadline())
                .nationality(user.getNationality())
                .gender(user.getGender())
                .birthday(user.getBirthday())
                .job(user.getJob())
                .fullName(user.getFullName())
                .build();
    }
    public static User toEntity(UserDto userDto) {
        return User.builder()
                .id(userDto.getId())
                .lastName(userDto.getLastName())
                .firstName(userDto.getFirstName())
                .address(userDto.getAddress())
                .numbers(userDto.getNumbers())
                .serialDate(userDto.getSerialDate())
                .region(userDto.getRegion())
                .serial(userDto.getSerial())
                .religion(userDto.getReligion())
                .status(userDto.getStatus())
                .deadline(userDto.getDeadline())
                .gender(userDto.getGender())
                .birthday(userDto.getBirthday())
                .nationality(userDto.getNationality())
                .fullName(userDto.getFullName())
                .job(userDto.getJob())
                .build();
    }
}
