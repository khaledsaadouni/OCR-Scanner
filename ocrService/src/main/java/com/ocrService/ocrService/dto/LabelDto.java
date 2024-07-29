package com.ocrService.ocrService.dto;

import com.ocrService.ocrService.modal.Label;
import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class LabelDto {
    private Long id;
    private String name;
    private double top_x;
    private double top_y;
    private double bottom_x;
    private double bottom_y;
    private Long type_id;
    public static LabelDto fromEntity(Label label) {
        return LabelDto.builder()
                .id(label.getId())
                .name(label.getName())
                .top_x(label.getTop_x())
                .top_y(label.getTop_y())
                .bottom_x(label.getBottom_x())
                .bottom_y(label.getBottom_y())
                .type_id(label.getType().getId())
                .build();
    }
    public static Label toEntity(LabelDto labelDto) {
        return Label.builder()
                .name(labelDto.getName())
                .top_x(labelDto.getTop_x())
                .top_y(labelDto.getTop_y())
                .bottom_x(labelDto.getBottom_x())
                .bottom_y(labelDto.getBottom_y())
                .build();
    }
}
