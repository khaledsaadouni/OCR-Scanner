package com.ocrService.ocrService.service;

import com.ocrService.ocrService.dto.LabelDto;
import com.ocrService.ocrService.dto.TypeDto;
import com.ocrService.ocrService.modal.Label;
import com.ocrService.ocrService.modal.Type;
import com.ocrService.ocrService.repository.LabelRepository;
import com.ocrService.ocrService.repository.TypeRepository;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
@AllArgsConstructor
public class TypeService {
    private final TypeRepository typeRepository;
    private final LabelRepository labelRepository;

    public List<Type> findAll() {
        return typeRepository.findAll();
    }
    public Type create(TypeDto type) {
        return typeRepository.save(TypeDto.toEntity(type));

    }
    public Type setImage(TypeDto dto) {
        Type type = findById(dto.getId());
        type.setImage(dto.getImage());
        return typeRepository.save(type);
    }
    public List<Type> delete(Long id) {
        typeRepository.deleteById(id);
        return typeRepository.findAll();
    }
    public Type findById(Long id) {
        return typeRepository.findById(id).orElseThrow();
    }
    public List<Type> addLabel(Long id, List<LabelDto> labels) {
        System.out.println("----------------------------------------->id = " + id);
        Type type = findById(id);
        for(Label label : type.getLabels()) {
            label.setType(null);
            labelRepository.save(label);
        }
        type.setLabels(new ArrayList<>());
        System.out.println("----------------------------------------->id = " + id);
        type = typeRepository.save(type);

        System.out.println("----------------------------------------->length = " + type.getLabels().size());
        for (LabelDto label : labels) {
            var l = labelRepository.save(LabelDto.toEntity(label));
            l.setType(type);

            labelRepository.save(l);
            type.getLabels().add(l);
        }
        typeRepository.save(type);

        System.out.println("----------------------------------------->length 2= " + type.getLabels().size());
        return typeRepository.findAll();
    }

}
