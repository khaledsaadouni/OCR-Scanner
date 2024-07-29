package com.ocrService.ocrService.controller;

import com.ocrService.ocrService.dto.UserDto;
import com.ocrService.ocrService.service.UserService;
import lombok.AllArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/user")
@AllArgsConstructor
public class UserController {
    private final UserService userService;
    @PostMapping("/create")
    public ResponseEntity<Void> create(@RequestBody UserDto userDto) {
        userService.create(userDto);
        return ResponseEntity.ok().build();
    }
    @GetMapping("/all")
    public ResponseEntity<List<UserDto>> getAll() {
        return ResponseEntity.ok(userService.getAll().stream().map(UserDto::fromEntity).toList());
    }
    @DeleteMapping("/delete/{id}")
    public ResponseEntity<List<UserDto>> delete(@PathVariable Long id) {
        userService.delete(id);
        return ResponseEntity.ok(userService.getAll().stream().map(UserDto::fromEntity).toList());
    }
}
