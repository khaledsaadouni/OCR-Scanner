package com.ocrService.ocrService.dto;

import com.ocrService.ocrService.modal.Type;
import lombok.Builder;
import lombok.Data;

import java.util.ArrayList;
import java.util.List;

@Builder
@Data
public class TypeDto {
    private Long id;
    private String name;
    private String image;
    private double width;
    private double height;
    private boolean crop;
    private int threshold;
    private List<LabelDto> labels;
    public static TypeDto fromEntity(Type type) {
        return TypeDto.builder()
                .id(type.getId())
                .name(type.getName())
                .width(type.getWidth())
                .height(type.getHeight())
                .threshold(type.getThreshold())
                .image(type.getImage())
                .crop(type.isCrop())
                .labels(type.getLabels()!= null ? type.getLabels().stream().map(LabelDto::fromEntity).toList() : new ArrayList<>())
                .build();
    }
    public static Type toEntity(TypeDto typeDto) {
        return Type.builder()
                .name(typeDto.getName())
                .width(typeDto.getWidth())
                .height(typeDto.getHeight())
                .crop(typeDto.isCrop())
                .threshold(typeDto.getThreshold())
                .image(typeDto.getImage())
                .build();
    }
}
