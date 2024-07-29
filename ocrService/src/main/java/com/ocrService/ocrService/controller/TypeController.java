package com.ocrService.ocrService.controller;

import com.ocrService.ocrService.dto.LabelDto;
import com.ocrService.ocrService.dto.TypeDto;
import com.ocrService.ocrService.modal.Type;
import com.ocrService.ocrService.service.TypeService;
import lombok.AllArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/type")
@AllArgsConstructor
public class TypeController {
    private final TypeService typeService;
    @PostMapping("/create")
    public ResponseEntity<TypeDto> create(@RequestBody TypeDto type) {
        return ResponseEntity.ok(TypeDto.fromEntity(typeService.create(type)));
    }
    @PostMapping("/setImage")
    public ResponseEntity<TypeDto> setImage(@RequestBody TypeDto type) {
        return ResponseEntity.ok(TypeDto.fromEntity(typeService.setImage(type)));
    }
    @GetMapping("/all")
    public ResponseEntity<List<TypeDto>> findAll() {
        return ResponseEntity.ok(typeService.findAll().stream().map(TypeDto::fromEntity).toList());
    }
    @GetMapping("/{id}")
    public ResponseEntity<TypeDto> findById(@PathVariable("id") Long id) {
        return ResponseEntity.ok(TypeDto.fromEntity(typeService.findById(id)));
    }
    @DeleteMapping("/delete/{id}")
    public ResponseEntity<List<TypeDto>> delete(@PathVariable Long id) {
        return ResponseEntity.ok(typeService.delete(id).stream().map(TypeDto::fromEntity).toList());
    }
    @PostMapping("/addLabel/{id}")
    public ResponseEntity<List<TypeDto>> addLabel(@PathVariable Long id, @RequestBody List<LabelDto> labels) {
        return ResponseEntity.ok(typeService.addLabel(id, labels).stream().map(TypeDto::fromEntity).toList());
    }

}
