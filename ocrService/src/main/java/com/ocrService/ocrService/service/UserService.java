package com.ocrService.ocrService.service;

import com.ocrService.ocrService.dto.UserDto;
import com.ocrService.ocrService.modal.User;
import com.ocrService.ocrService.repository.UserRepository;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@Slf4j
@AllArgsConstructor
public class UserService {
    private final UserRepository userRepository;

    public void create(UserDto userDto) {
        userRepository.save(UserDto.toEntity(userDto));
    }

    public List<User> getAll() {
       return userRepository.findAll();
    }

    public void delete(Long id) {
        userRepository.deleteById(id);
    }
}
